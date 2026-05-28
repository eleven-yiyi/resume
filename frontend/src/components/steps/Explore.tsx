"use client";

import { useOnboarding } from "@/store/onboarding";

// Placeholder card layouts: [title bar width, sub1 width, sub2 width]
const PLACEHOLDER_CARDS = [
  ["w-[90%]", "w-[72%]", "w-[50%]"],
  ["w-[72%]", "w-[85%]", "w-[40%]"],
  ["w-[50%]", "w-[65%]", "w-[85%]"],
  ["w-[90%]", "w-[40%]", "w-[65%]"],
  ["w-[72%]", "w-[85%]", "w-[40%]"],
  ["w-[50%]", "w-[65%]", "w-[85%]"],
] as const;

export function Explore() {
  const matchData = useOnboarding((s) => s.matchData);

  // Use real count if available, otherwise show placeholder
  const matchCount = matchData.length > 0 ? matchData.length : 142;

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-10 gap-4 text-center bg-gray-50">

      {/* Icon */}
      <div className="text-5xl animate-fadeUp">✦</div>

      {/* Title */}
      <h2
        className="text-[28px] font-bold tracking-tight animate-fadeUp"
        style={{ animationDelay: "50ms" }}
      >
        Start exploring your jobs
      </h2>

      {/* Subtitle */}
      <p
        className="text-[14px] text-gray-500 max-w-[360px] leading-relaxed animate-fadeUp"
        style={{ animationDelay: "100ms" }}
      >
        Based on your profile and preferences, we&apos;ve curated the best matching opportunities for you
      </p>

      {/* Match count badge */}
      <div
        className="px-7 py-2.5 bg-blue-600 rounded-full text-[14px] font-semibold text-white animate-fadeUp"
        style={{ animationDelay: "150ms" }}
      >
        {matchCount} matched jobs found
      </div>

      {/* Setup complete badge */}
      <div
        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-green-50 border border-green-200 text-[13px] text-green-700 font-medium animate-fadeUp"
        style={{ animationDelay: "200ms" }}
      >
        🎉 Setup complete
      </div>

      {/* Placeholder job card grid */}
      <div
        className="grid grid-cols-3 gap-3 w-full max-w-[680px] mt-6 opacity-20 pointer-events-none animate-fadeUp"
        style={{ animationDelay: "250ms" }}
      >
        {PLACEHOLDER_CARDS.map(([t, s1, s2], i) => (
          <div
            key={i}
            className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col gap-2"
          >
            <div className={`h-2.5 rounded-full bg-gray-300 ${t}`} />
            <div className={`h-2 rounded-full bg-gray-200 ${s1}`} />
            <div className={`h-2 rounded-full bg-gray-200 ${s2}`} />
          </div>
        ))}
      </div>
    </main>
  );
}
