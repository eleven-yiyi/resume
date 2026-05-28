"use client";

import { useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { extractPreferences, savePreferences } from "@/lib/api";
import { useOnboarding } from "@/store/onboarding";
import { PreferenceCard } from "./PreferenceCard";
import type { WorkArrangement, JobType } from "@/types";

// ── Types ─────────────────────────────────────────────────────────────────────
type Message = { id: number; type: "ai" | "user"; content: string };

type PrefSlots = { jf: string; wa: string; loc: string; jt: string; sal: string };

// ── Step definitions ──────────────────────────────────────────────────────────
const STEP_DEFS = [
  { key: "jf",  nextQ: "What's your preferred <strong>work arrangement</strong>?" },
  { key: "wa",  nextQ: "Where would you like to work? Tell me your <strong>preferred location</strong>." },
  { key: "loc", nextQ: "What <strong>job type</strong> are you looking for?" },
  { key: "jt",  nextQ: "Last one — what's your <strong>expected salary range</strong>?" },
  { key: "sal", nextQ: "" },
] as const;

let _id = 2;

// ── Component ─────────────────────────────────────────────────────────────────
export function Preferences() {
  const { resumeId, updatePreferences, setStep } = useOnboarding();
  const msgsEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    { id: 0, type: "ai", content: "Great profile! Now let's set your job preferences so I can find the best matches for you." },
    { id: 1, type: "ai", content: "First up — <strong>what job functions</strong> are you interested in?" },
  ]);
  const [cardStep,   setCardStep]   = useState(1);
  const [cardDone,   setCardDone]   = useState(false);
  const [prefs,      setPrefs]      = useState<PrefSlots>({ jf: "", wa: "", loc: "", jt: "", sal: "" });
  const [extraNotes, setExtraNotes] = useState<string[]>([]);
  const [inputText,  setInputText]  = useState("");
  const [isSaving,   setIsSaving]   = useState(false);

  const filledCount   = Object.values(prefs).filter(Boolean).length;
  const canViewMatches = cardDone || filledCount >= 3;

  // ── Helpers ──────────────────────────────────────────────────────────────────
  function addMsg(type: "ai" | "user", content: string) {
    setMessages((prev) => [...prev, { id: _id++, type, content }]);
    setTimeout(() => msgsEndRef.current?.scrollIntoView({ behavior: "smooth" }), 60);
  }

  function mergePrefs(patch: Partial<PrefSlots>): PrefSlots {
    const next = { ...prefs, ...patch };
    setPrefs(next);
    return next;
  }

  // ── Card callbacks ────────────────────────────────────────────────────────────
  function handleCardSubmit(val: string) {
    if (!val) return;
    const def = STEP_DEFS[cardStep - 1];
    mergePrefs({ [def.key]: val });
    addMsg("user", val);

    if (cardStep < 5) {
      setTimeout(() => { addMsg("ai", def.nextQ); setCardStep((s) => s + 1); }, 200);
    } else {
      setCardDone(true);
      setTimeout(() => addMsg("ai", "🎉 All set! I have everything I need. Ready to see your matches?"), 200);
    }
  }

  function handleCardSkip() {
    addMsg("user", "Skip");
    const def = STEP_DEFS[cardStep - 1];
    if (cardStep < 5) {
      setTimeout(() => { addMsg("ai", def.nextQ); setCardStep((s) => s + 1); }, 200);
    } else {
      setCardDone(true);
      setTimeout(() => addMsg("ai", "🎉 All set! I have everything I need. Ready to see your matches?"), 200);
    }
  }

  function handleCardBack() {
    setCardStep((s) => Math.max(1, s - 1));
  }

  // ── Free-text input ───────────────────────────────────────────────────────────
  async function handleSend() {
    const txt = inputText.trim();
    if (!txt) return;
    setInputText("");
    addMsg("user", txt);

    try {
      const slots = await extractPreferences(txt);
      const updated: string[] = [];
      const patch: Partial<PrefSlots> = {};

      if (slots.job_functions?.length) { patch.jf = slots.job_functions.join(", "); updated.push("job function"); }
      if (slots.work_arrangement)      { patch.wa = slots.work_arrangement; updated.push("work arrangement"); }
      if (slots.location)              { patch.loc = slots.location; updated.push("location"); }
      if (slots.job_type)              { patch.jt = slots.job_type; updated.push("job type"); }
      if (slots.salary_min || slots.salary_max) {
        patch.sal = [slots.salary_min, slots.salary_max].filter(Boolean).join("–");
        updated.push("salary");
      }
      if (slots.extra_notes?.length) setExtraNotes((e) => [...e, ...slots.extra_notes!]);

      const next = mergePrefs(patch);
      const filled = Object.values(next).filter(Boolean).length;
      const ack = updated.length
        ? `Got it — updated your ${updated.join(", ")}.${filled >= 3 ? " You're ready to see matches!" : ""}`
        : "Noted — I'll keep that in mind ✓";
      addMsg("ai", ack);

    } catch {
      setExtraNotes((e) => [...e, txt]);
      addMsg("ai", "Noted — I'll keep that in mind when matching jobs for you ✓");
    }
  }

  // ── Navigate to matches ───────────────────────────────────────────────────────
  async function handleViewMatches() {
    if (!canViewMatches || isSaving) return;
    setIsSaving(true);

    let salMin: number | null = null, salMax: number | null = null, salNeg = false;
    if (prefs.sal === "Negotiable") {
      salNeg = true;
    } else {
      const m = prefs.sal.match(/\$?([\d,]+)\s*[–\-]\s*\$?([\d,]+)/);
      if (m) { salMin = parseInt(m[1].replace(/,/g, "")); salMax = parseInt(m[2].replace(/,/g, "")); }
    }

    const waMap: Record<string, WorkArrangement> = {
      "Onsite": "onsite", "Hybrid": "hybrid", "Remote": "remote", "Open to all": "open",
    };
    const jtMap: Record<string, JobType> = {
      "Full-time": "full-time", "Part-time": "part-time",
      "Contract / Freelance": "contract", "Internship": "internship",
    };

    const payload = {
      job_functions:     prefs.jf ? prefs.jf.split(", ") : [],
      work_arrangement:  waMap[prefs.wa] ?? null,
      location:          prefs.loc || null,
      job_type:          jtMap[prefs.jt] ?? null,
      salary_min:        salMin,
      salary_max:        salMax,
      salary_negotiable: salNeg,
      extra_notes:       extraNotes,
      feedback_reasons:  [] as { reason: string }[],
    };

    updatePreferences(payload);

    if (resumeId) {
      try {
        await savePreferences({ ...payload, resume_id: resumeId });
      } catch { /* proceed anyway */ }
    }

    setStep(3);
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <main
      className="flex-1 overflow-hidden bg-gray-50"
      style={{ height: "calc(100vh - 64px)" }}
    >
      <div className="h-full max-w-[680px] mx-auto flex flex-col">

        {/* Message stream */}
        <div className="flex-1 overflow-y-auto px-6 pt-7 no-scrollbar">
          <div className="flex flex-col pb-2">
            {messages.map((msg, i) => (
              <div key={msg.id}>
                {/* Connector line between bubbles */}
                {i > 0 && (
                  <div className="flex flex-col items-start ml-[22px] my-0.5 gap-0">
                    <div className="w-0 border-l-2 border-dashed border-green-200 h-3.5" />
                    <div className="w-2 h-2 rounded-full border-2 border-green-500 bg-white" />
                  </div>
                )}
                {msg.type === "ai" ? (
                  <div className="flex items-start gap-2.5 mb-1.5 animate-fadeUp">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-0.5">
                      ✦
                    </div>
                    <div
                      className="bg-white border border-gray-200 rounded-[4px] rounded-tr-xl rounded-br-xl rounded-bl-xl px-4 py-3 text-[13px] leading-relaxed max-w-[480px] shadow-sm"
                      dangerouslySetInnerHTML={{ __html: msg.content }}
                    />
                  </div>
                ) : (
                  <div className="flex justify-end mb-1.5 animate-fadeUp">
                    <div className="bg-blue-600 text-white rounded-[4px] rounded-tl-xl rounded-bl-xl rounded-br-xl px-3.5 py-2.5 text-[13px] leading-relaxed max-w-[380px]">
                      {msg.content}
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={msgsEndRef} />
          </div>
        </div>

        {/* Floating preference card */}
        {!cardDone && (
          <div className="flex-shrink-0 px-6 pt-3">
            <PreferenceCard
              step={cardStep}
              onSubmit={handleCardSubmit}
              onSkip={handleCardSkip}
              onBack={handleCardBack}
            />
          </div>
        )}

        {/* AI input bar */}
        <div className="flex-shrink-0 mx-6 mt-2.5 mb-1">
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2 shadow-sm">
            <input
              className="flex-1 border-none outline-none text-[13px] text-gray-900 bg-transparent placeholder:text-gray-300"
              placeholder="Tell me what kind of jobs you are (or aren't) looking for."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button
              onClick={handleSend}
              className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm flex-shrink-0 hover:bg-blue-700 transition-colors"
            >
              ↑
            </button>
          </div>
        </div>
        <p className="flex-shrink-0 text-center text-[11px] text-gray-300 mb-2">
          Boss AI can make mistakes. Check important info.
        </p>

        {/* View Matches button */}
        <div className="flex-shrink-0 px-6 pb-4 flex justify-end">
          <button
            onClick={handleViewMatches}
            className={cn(
              "h-11 px-6 rounded-xl text-[14px] font-semibold bg-blue-600 text-white transition-all",
              canViewMatches && !isSaving
                ? "opacity-100 hover:bg-blue-700"
                : "opacity-30 pointer-events-none"
            )}
          >
            {isSaving ? "Saving…" : "View Matches →"}
          </button>
        </div>
      </div>
    </main>
  );
}
