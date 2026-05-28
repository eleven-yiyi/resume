"use client";

import { cn } from "@/lib/utils";
import { useOnboarding } from "@/store/onboarding";

const STEPS = [
  { id: 1, label: "Resume" },
  { id: 2, label: "Preferences" },
  { id: 3, label: "Matches" },
  { id: 4, label: "Explore" },
] as const;

export function StepNav() {
  const step = useOnboarding((s) => s.step);

  return (
    <nav className="h-16 bg-white border-b border-gray-200 px-12 flex items-center justify-center flex-shrink-0 relative">
      {/* Logo */}
      <div className="absolute left-12 flex items-center font-bold text-lg tracking-tight">
        bossjob
        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mb-2 ml-0.5" />
      </div>

      {/* Steps */}
      <div className="flex items-center gap-1">
        {STEPS.map((s, i) => {
          const isDone = step > s.id;
          const isCur = step === s.id;
          return (
            <div key={s.id} className="flex items-center gap-1">
              <div
                className={cn(
                  "flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-[13px] font-medium border transition-all",
                  isCur && "bg-blue-50 text-blue-600 border-blue-200",
                  isDone && "bg-green-50 text-green-700 border-green-200",
                  !isCur && !isDone && "text-gray-400 border-transparent"
                )}
              >
                <span
                  className={cn(
                    "w-[18px] h-[18px] rounded-full text-[10px] font-bold flex items-center justify-center flex-shrink-0",
                    isCur && "bg-blue-600 text-white",
                    isDone && "bg-green-600 text-white",
                    !isCur && !isDone && "bg-gray-200 text-gray-500"
                  )}
                >
                  {isDone ? "✓" : s.id}
                </span>
                {s.label}
              </div>
              {i < STEPS.length - 1 && (
                <span className="text-gray-300 text-xs px-0.5">›</span>
              )}
            </div>
          );
        })}
      </div>
    </nav>
  );
}
