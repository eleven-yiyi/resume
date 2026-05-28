"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

// ── Static data ───────────────────────────────────────────────────────────────
const JOB_FUNCTIONS = [
  "Product Management", "Software Engineering", "Data Science",
  "UX / Design", "Marketing", "Operations", "Sales", "Finance",
];
const WORK_ARRANGEMENTS = [
  "🏢 Onsite — full in-office",
  "🔀 Hybrid — flexible schedule",
  "🌐 Remote — fully distributed",
  "💼 Open to all",
];
const JOB_TYPES = ["Full-time", "Part-time", "Contract / Freelance", "Internship"];
const LOCATION_SUGS = [
  "Singapore", "Kuala Lumpur, Malaysia", "Jakarta, Indonesia",
  "Manila, Philippines", "Remote (Anywhere)",
];
const STEP_TITLES = [
  "Job Function", "Work Arrangement", "Desired Location", "Job Type", "Expected Salary",
];

// ── Props ─────────────────────────────────────────────────────────────────────
interface Props {
  step:     number;
  onSubmit: (value: string) => void;
  onSkip:   () => void;
  onBack:   () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────
export function PreferenceCard({ step, onSubmit, onSkip, onBack }: Props) {
  const [chips,     setChips]     = useState<string[]>([]);
  const [radioOpt,  setRadioOpt]  = useState("");
  const [locInput,  setLocInput]  = useState("");
  const [salFrom,   setSalFrom]   = useState("");
  const [salTo,     setSalTo]     = useState("");
  const [salPeriod, setSalPeriod] = useState("Monthly");
  const [salNeg,    setSalNeg]    = useState(false);

  // Reset local state on each step change
  useEffect(() => {
    setChips([]); setRadioOpt(""); setLocInput("");
    setSalFrom(""); setSalTo(""); setSalNeg(false);
  }, [step]);

  const canSubmit =
    step === 1 ? chips.length > 0 :
    step === 2 ? !!radioOpt :
    step === 3 ? locInput.trim().length > 0 :
    step === 4 ? !!radioOpt :
    /* 5 */      !!(salFrom || salTo || salNeg);

  function getValue(): string {
    if (step === 1) return chips.join(", ");
    if (step === 2) return radioOpt.replace(/^\S+\s/, "").split("—")[0].trim();
    if (step === 3) return locInput.trim();
    if (step === 4) return radioOpt;
    // step 5
    if (salNeg && !salFrom && !salTo) return "Negotiable";
    if (salFrom && salTo)
      return `$${salFrom} – $${salTo} / ${salPeriod === "Monthly" ? "mo" : "yr"}`;
    return "Flexible";
  }

  // ── Radio row shared component ──────────────────────────────────────────────
  function RadioOpt({ label }: { label: string }) {
    const sel = radioOpt === label;
    return (
      <button
        className="flex items-center gap-2.5 py-2.5 border-b border-gray-50 last:border-0 w-full text-left"
        onClick={() => setRadioOpt(label)}
      >
        <div className={cn(
          "w-[18px] h-[18px] rounded-full border-[1.5px] flex-shrink-0 flex items-center justify-center transition-all",
          sel ? "border-blue-600 bg-blue-600" : "border-gray-300"
        )}>
          {sel && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
        </div>
        <span className={cn("text-[13px]", sel && "text-blue-600 font-medium")}>{label}</span>
      </button>
    );
  }

  return (
    // key=step forces re-mount → restarts animation on every step change
    <div key={step} className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden animate-slideUp">

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-gray-200">
        <span className="text-[14px] font-bold">{STEP_TITLES[step - 1]}</span>
        <div className="flex items-center gap-2 text-[13px] text-gray-500 font-medium">
          <button
            disabled={step === 1}
            onClick={onBack}
            className="w-6 h-6 rounded-full border border-gray-200 flex items-center justify-center hover:border-blue-500 hover:text-blue-600 disabled:opacity-30 transition-colors"
          >‹</button>
          <span>{step} / 5</span>
          <button disabled className="w-6 h-6 rounded-full border border-gray-200 flex items-center justify-center opacity-30 cursor-default">›</button>
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-4">

        {/* Step 1 — Job Function chips */}
        {step === 1 && (
          <>
            <p className="text-[13px] font-semibold mb-3">Select all that apply</p>
            <div className="flex flex-wrap gap-2">
              {JOB_FUNCTIONS.map((jf) => (
                <button
                  key={jf}
                  className={cn(
                    "px-3.5 py-2 rounded-full border text-[13px] font-medium transition-all",
                    chips.includes(jf)
                      ? "border-blue-600 bg-blue-50 text-blue-600"
                      : "border-gray-200 text-gray-500 hover:border-blue-400 hover:text-blue-500"
                  )}
                  onClick={() =>
                    setChips((prev) =>
                      prev.includes(jf) ? prev.filter((c) => c !== jf) : [...prev, jf]
                    )
                  }
                >
                  {jf}
                </button>
              ))}
            </div>
          </>
        )}

        {/* Step 2 — Work Arrangement */}
        {step === 2 && (
          <>
            <p className="text-[13px] font-semibold mb-1">Choose one</p>
            <div className="flex flex-col">
              {WORK_ARRANGEMENTS.map((opt) => <RadioOpt key={opt} label={opt} />)}
            </div>
          </>
        )}

        {/* Step 3 — Location */}
        {step === 3 && (
          <>
            <p className="text-[13px] font-semibold mb-2">City or region</p>
            <input
              autoFocus
              className="w-full h-9 px-3.5 border border-gray-200 rounded-full text-[13px] outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 mb-2.5 placeholder:text-gray-300"
              placeholder="Type a city or region..."
              value={locInput}
              onChange={(e) => setLocInput(e.target.value)}
            />
            <div className="flex flex-wrap gap-1.5">
              {LOCATION_SUGS.map((s) => (
                <button
                  key={s}
                  className="px-3 py-1 rounded-full border border-gray-200 text-xs text-gray-500 hover:border-blue-400 hover:text-blue-500 transition-all"
                  onClick={() => setLocInput(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </>
        )}

        {/* Step 4 — Job Type */}
        {step === 4 && (
          <>
            <p className="text-[13px] font-semibold mb-1">Choose one</p>
            <div className="flex flex-col">
              {JOB_TYPES.map((opt) => <RadioOpt key={opt} label={opt} />)}
            </div>
          </>
        )}

        {/* Step 5 — Salary */}
        {step === 5 && (
          <>
            <p className="text-[13px] font-semibold mb-3">Salary</p>
            <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden mb-3">
              <div className="px-3 h-10 bg-gray-50 border-r border-gray-200 flex items-center text-[13px] font-semibold flex-shrink-0 text-gray-700">
                USD
              </div>
              <input
                type="number"
                placeholder="Min"
                className="flex-1 h-10 px-3 text-[13px] border-none outline-none min-w-0"
                value={salFrom}
                onChange={(e) => setSalFrom(e.target.value)}
              />
              <span className="px-2 text-gray-300 flex-shrink-0">—</span>
              <input
                type="number"
                placeholder="Max"
                className="flex-1 h-10 px-3 text-[13px] border-none outline-none min-w-0"
                value={salTo}
                onChange={(e) => setSalTo(e.target.value)}
              />
              <div className="h-10 px-2 border-l border-gray-200 bg-gray-50 flex items-center flex-shrink-0">
                <select
                  className="border-none bg-transparent text-[13px] outline-none cursor-pointer text-gray-700"
                  value={salPeriod}
                  onChange={(e) => setSalPeriod(e.target.value)}
                >
                  <option>Monthly</option>
                  <option>Annually</option>
                </select>
              </div>
            </div>
            <button
              className="flex items-center gap-2 cursor-pointer"
              onClick={() => setSalNeg(!salNeg)}
            >
              <div className={cn(
                "w-4 h-4 border-[1.5px] rounded flex items-center justify-center transition-all flex-shrink-0",
                salNeg ? "bg-blue-600 border-blue-600" : "border-gray-300"
              )}>
                {salNeg && <span className="text-white text-[10px] font-bold leading-none">✓</span>}
              </div>
              <span className="text-[13px] text-gray-800">Negotiable</span>
            </button>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50">
        <button
          disabled={step === 1}
          onClick={onBack}
          className="h-8 px-4 border border-gray-200 rounded-lg text-[13px] font-medium text-gray-500 disabled:opacity-30 hover:border-gray-700 hover:text-gray-700 transition-all"
        >
          Back
        </button>
        <div className="flex gap-2">
          <button
            onClick={onSkip}
            className="h-8 px-4 border border-gray-200 rounded-lg text-[13px] font-medium text-gray-500 hover:border-gray-700 hover:text-gray-700 transition-all"
          >
            Skip
          </button>
          <button
            disabled={!canSubmit}
            onClick={() => canSubmit && onSubmit(getValue())}
            className={cn(
              "h-8 px-5 rounded-lg text-[13px] font-semibold transition-all bg-blue-600 text-white",
              canSubmit ? "hover:bg-blue-700" : "opacity-35 pointer-events-none"
            )}
          >
            {step === 5 ? "Submit →" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}
