"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { searchMatches, sendFeedback } from "@/lib/api";
import { useOnboarding } from "@/store/onboarding";
import type { JobMatch } from "@/types";

// ── Demo fallback (shown when no resumeId or API unavailable) ─────────────────
const DEMO: JobMatch[] = [
  {
    id: "demo-1",
    title: "Senior Product Manager",
    company: "Grab",
    location: "Singapore",
    work_arrangement: "hybrid",
    salary_min: 8000, salary_max: 12000, currency: "SGD",
    highlights: [
      "Own GrabPay's merchant checkout roadmap end-to-end",
      "Cross-functional leadership across 3 SEA markets",
      "High ownership, fast-shipping culture",
    ],
    tags: ["product management", "fintech", "payments"],
    match_score: 94,
    why_fit: [
      "Payments domain aligns with your background",
      "Hybrid matches your work arrangement preference",
      "Salary range within your expectations",
    ],
  },
  {
    id: "demo-2",
    title: "Product Manager, AI Features",
    company: "GoTo Group",
    location: "Jakarta, Indonesia",
    work_arrangement: "hybrid",
    salary_min: 30_000_000, salary_max: 50_000_000, currency: "IDR",
    highlights: [
      "Lead AI initiatives across Gojek & Tokopedia",
      "Bridge ML research and product execution",
      "Serve 100M+ users across Indonesia",
    ],
    tags: ["AI", "product management", "machine learning"],
    match_score: 88,
    why_fit: [
      "AI product experience matches the role scope",
      "Growth-stage environment fits your stated goals",
      "Strong cross-functional background",
    ],
  },
  {
    id: "demo-3",
    title: "Senior Software Engineer, Backend",
    company: "Sea Group",
    location: "Singapore",
    work_arrangement: "hybrid",
    salary_min: 8000, salary_max: 14000, currency: "SGD",
    highlights: [
      "Scale systems to 100M+ daily transactions",
      "Own services from design to production",
      "Small team, direct impact",
    ],
    tags: ["Go", "Kafka", "distributed systems"],
    match_score: 82,
    why_fit: [
      "Backend skills align with Go/Kafka stack",
      "Hybrid work arrangement matches preference",
      "Competitive SGD salary band",
    ],
  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
type DotStatus = "pending" | "current" | "liked" | "disliked";

function formatSalary(m: JobMatch): string {
  if (!m.salary_min && !m.salary_max) return "Salary TBD";
  const fmt = (n: number) =>
    n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n.toLocaleString();
  return `${m.currency} ${fmt(m.salary_min!)}–${fmt(m.salary_max!)}`;
}

// ── Component ─────────────────────────────────────────────────────────────────
export function Matches() {
  const { resumeId, setStep, setMatchData, addFeedbackReason } = useOnboarding();

  const [matches,   setMatches]   = useState<JobMatch[]>([]);
  const [statuses,  setStatuses]  = useState<DotStatus[]>([]);
  const [cur,       setCur]       = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [subtitle,  setSubtitle]  = useState("");
  const [dlOpen,    setDlOpen]    = useState(false);
  const [dlReason,  setDlReason]  = useState("");

  // Load on mount
  useEffect(() => {
    async function load() {
      let loaded = DEMO;
      if (resumeId) {
        try {
          const data = await searchMatches(resumeId, 3);
          if (data.matches.length) loaded = data.matches;
        } catch { /* fall back to demo */ }
      }
      setMatches(loaded);
      setMatchData(loaded);
      setStatuses(loaded.map((_, i) => (i === 0 ? "current" : "pending")));
      setSubtitle(`${loaded.length} highly matched jobs based on your profile`);
      setIsLoading(false);
    }
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Advance to next card or step 4
  function advance(status: "liked" | "disliked") {
    setStatuses((prev) => {
      const next = [...prev];
      next[cur] = status;
      if (cur + 1 < next.length) next[cur + 1] = "current";
      return next;
    });
    if (cur + 1 < matches.length) {
      setCur((c) => c + 1);
    } else {
      setTimeout(() => setStep(4), 350);
    }
  }

  function handleLike() {
    const jd = matches[cur];
    if (resumeId && jd) {
      sendFeedback({ resume_id: resumeId, jd_id: jd.id, action: "like" }).catch(() => {});
    }
    advance("liked");
  }

  function handleDislikeSubmit() {
    const reason = dlReason.trim();
    if (!reason) return;
    const jd = matches[cur];
    addFeedbackReason({ jobIdx: cur, reason });
    if (resumeId && jd) {
      sendFeedback({ resume_id: resumeId, jd_id: jd.id, action: "dislike", reason }).catch(() => {});
    }
    setDlOpen(false);
    setDlReason("");
    advance("disliked");
  }

  const m = matches[cur];

  return (
    <main className="flex-1 flex flex-col items-center px-6 pt-6 pb-10 bg-gray-50">

      {/* Header */}
      <div className="text-center mb-5">
        <h2 className="text-[22px] font-bold tracking-tight mb-1">Your Top Matches</h2>
        <p className="text-[13px] text-gray-500">
          {isLoading ? "Finding your best matches…" : subtitle}
        </p>
        {/* Dot indicators */}
        <div className="flex gap-1.5 mt-3.5 justify-center">
          {statuses.map((s, i) => (
            <div
              key={i}
              className={cn(
                "h-1 rounded-full transition-all duration-300",
                s === "current"  && "w-8 bg-blue-600",
                s === "pending"  && "w-6 bg-gray-200",
                s === "liked"    && "w-6 bg-green-500",
                s === "disliked" && "w-6 bg-red-400"
              )}
            />
          ))}
        </div>
      </div>

      {/* Card */}
      <div className="w-full max-w-[620px] flex-1 flex flex-col">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-[13px] text-gray-300">Loading…</p>
          </div>
        ) : m ? (
          <div
            key={cur}
            className="bg-white border border-gray-200 rounded-xl shadow-md px-7 py-7 flex-1 flex flex-col animate-fadeUp"
          >
            {/* Job header */}
            <div className="flex items-start gap-4 mb-6">
              <div className="w-[52px] h-[52px] rounded-xl bg-gray-100 flex items-center justify-center text-2xl flex-shrink-0">
                🏢
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[12px] text-gray-500 mb-0.5">
                  {m.company} · {m.location}
                </p>
                <h3 className="text-[18px] font-bold tracking-tight mb-2.5">{m.title}</h3>
                <div className="flex flex-wrap gap-1.5">
                  <span className="px-2.5 py-0.5 rounded border border-gray-200 text-[12px] text-gray-500">
                    {formatSalary(m)}
                  </span>
                  {m.work_arrangement && (
                    <span className="px-2.5 py-0.5 rounded border border-gray-200 text-[12px] text-gray-500 capitalize">
                      {m.work_arrangement}
                    </span>
                  )}
                  <span className="px-2.5 py-0.5 rounded bg-green-50 border border-green-200 text-[12px] text-green-700 font-semibold">
                    {m.match_score}% Match
                  </span>
                </div>
              </div>
            </div>

            {/* Highlights */}
            <p className="text-[11px] font-bold tracking-[0.05em] uppercase text-gray-500 mb-2.5">
              Highlights
            </p>
            <div className="flex flex-col gap-2 mb-4">
              {m.highlights.map((h, i) => (
                <div key={i} className="flex gap-2.5 text-[13px] text-gray-600 leading-relaxed items-start">
                  <span className="text-gray-300 text-base leading-[1.4] flex-shrink-0">·</span>
                  {h}
                </div>
              ))}
            </div>

            <div className="h-px bg-gray-100 my-1" />

            {/* Why it fits */}
            <p className="text-[11px] font-bold tracking-[0.05em] uppercase text-gray-500 mb-2.5 mt-4">
              Why it fits you
            </p>
            <div className="flex flex-col gap-2">
              {m.why_fit.map((r, i) => (
                <div
                  key={i}
                  className="text-[13px] px-3.5 py-2 rounded-lg bg-blue-50 border border-blue-100 text-gray-800 leading-relaxed"
                >
                  ✓ {r}
                </div>
              ))}
            </div>

            <div className="flex-1" />
          </div>
        ) : null}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 mt-5 w-full max-w-[620px]">
        <button
          onClick={() => { setDlOpen(true); setDlReason(""); }}
          className="flex-1 h-12 border-[1.5px] border-gray-200 rounded-xl bg-white text-[15px] font-semibold text-gray-500 flex items-center justify-center gap-2 hover:border-red-400 hover:text-red-500 hover:bg-red-50 transition-all"
        >
          👎 Not Interested
        </button>
        <button
          onClick={handleLike}
          className="flex-1 h-12 bg-blue-600 rounded-xl text-[15px] font-semibold text-white flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors"
        >
          👍 Like
        </button>
      </div>

      {/* Dislike modal */}
      {dlOpen && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn"
          onClick={(e) => e.target === e.currentTarget && setDlOpen(false)}
        >
          <div className="bg-white rounded-xl shadow-xl p-7 w-[420px] max-w-[90vw] animate-fadeUp">
            <h3 className="text-[16px] font-bold mb-1.5">What didn&apos;t work for you?</h3>
            <p className="text-[13px] text-gray-500 mb-4 leading-relaxed">
              Your feedback helps us improve match quality for the next batch.
            </p>
            <textarea
              autoFocus
              className="w-full px-3.5 py-3 border border-gray-200 rounded-lg text-[14px] text-gray-900 resize-none outline-none min-h-[96px] leading-relaxed bg-gray-50 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:bg-white transition-all"
              placeholder="e.g. Salary below expectations, role doesn't match..."
              value={dlReason}
              onChange={(e) => setDlReason(e.target.value)}
            />
            <div className="flex gap-2.5 mt-3.5">
              <button
                onClick={() => setDlOpen(false)}
                className="flex-1 h-10 border border-gray-200 rounded-lg text-[14px] font-medium text-gray-500 hover:border-gray-700 hover:text-gray-700 transition-all"
              >
                Cancel
              </button>
              <button
                disabled={!dlReason.trim()}
                onClick={handleDislikeSubmit}
                className={cn(
                  "flex-1 h-10 rounded-lg text-[14px] font-semibold bg-blue-600 text-white transition-all",
                  dlReason.trim() ? "hover:bg-blue-700" : "opacity-30 pointer-events-none"
                )}
              >
                Submit &amp; Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
