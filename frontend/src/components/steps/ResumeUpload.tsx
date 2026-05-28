"use client";

import { useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { parseResume } from "@/lib/api";
import { useOnboarding } from "@/store/onboarding";
import type { ParsedResume } from "@/types";

type UploadState = "idle" | "loading" | "done" | "error";

export function ResumeUpload() {
  const { setResume, setStep } = useOnboarding();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [parsedTags, setParsedTags] = useState<string[]>([]);

  async function handleFile(file: File) {
    if (uploadState !== "idle") return;
    setUploadState("loading");
    setErrorMsg("");

    try {
      const data = await parseResume(file);
      const tags = buildTags(data.parsed);
      setParsedTags(tags);
      setResume(data.resume_id, data.parsed);
      setUploadState("done");
      setTimeout(() => setStep(2), 900);
    } catch (err) {
      setUploadState("error");
      setErrorMsg(err instanceof Error ? err.message : "Upload failed");
    }
  }

  function buildTags(p: ParsedResume): string[] {
    const tags: string[] = [];
    if (p.years_of_experience) tags.push(`${p.years_of_experience} yrs exp`);
    if (p.education?.[0]) {
      const deg = p.education[0].degree?.split(" ").slice(-2).join(" ");
      if (deg) tags.push(deg);
    }
    p.skills?.slice(0, 3).forEach((s) => tags.push(s));
    return tags.filter(Boolean);
  }

  return (
    <main className="flex-1 flex items-center justify-center p-10 bg-gray-50">
      <div className="w-full max-w-[480px] flex flex-col gap-0 animate-[fadeUp_0.4s_ease]">

        {/* AI intro row */}
        <div className="flex items-center gap-3.5 mb-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center text-white text-xl shadow-[0_6px_16px_rgba(0,102,255,0.28)] flex-shrink-0">
            ✦
          </div>
          <div>
            <div className="text-[15px] font-bold">Boss AI</div>
            <div className="text-xs text-gray-500">Your personal career assistant</div>
          </div>
        </div>

        {/* AI speech bubble */}
        <div className="bg-white border border-gray-200 rounded-xl px-5 py-5 shadow-sm mb-5">
          <div className="text-[18px] font-bold mb-3.5 tracking-tight">
            Hi, I&apos;m Boss AI 👋
          </div>
          <div className="flex flex-col gap-2.5">
            {[
              { icon: "📄", text: "Parse your resume automatically" },
              { icon: "🎯", text: "Understand your job preferences" },
              { icon: "✨", text: "Surface best-matched roles for you" },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-2.5 text-gray-500 leading-relaxed">
                <span className="text-base w-6 text-center flex-shrink-0">{icon}</span>
                {text}
              </div>
            ))}
          </div>
        </div>

        {/* Action cards */}
        <div className="flex flex-col gap-3 mb-4">
          {/* Upload card */}
          <button
            className={cn(
              "flex items-center gap-4 bg-gray-50 border border-gray-200 rounded-xl p-5 text-left transition-all",
              uploadState === "idle" && "hover:border-blue-500 hover:bg-blue-50 cursor-pointer",
              uploadState === "loading" && "opacity-70 pointer-events-none",
              uploadState === "done" && "border-green-300 bg-green-50",
              uploadState === "error" && "border-red-300 bg-red-50"
            )}
            onClick={() => uploadState === "idle" && fileInputRef.current?.click()}
          >
            <div className="w-11 h-11 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0 text-lg font-bold">
              {uploadState === "loading" ? "⏳" : uploadState === "done" ? "✓" : uploadState === "error" ? "✗" : "↑"}
            </div>

            <div className="flex-1 min-w-0">
              {uploadState === "idle" && (
                <>
                  <div className="text-[15px] font-semibold mb-1">Upload a resume file</div>
                  <div className="text-[13px] text-gray-500">Supported: PDF, DOC, DOCX (up to 30MB)</div>
                </>
              )}
              {uploadState === "loading" && (
                <>
                  <div className="text-[15px] font-semibold text-blue-600">Parsing your resume...</div>
                  <div className="text-[13px] text-gray-500">Reading experience, skills, and education</div>
                </>
              )}
              {uploadState === "done" && (
                <>
                  <div className="text-[15px] font-semibold text-green-700">✓ Resume parsed successfully</div>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {parsedTags.map((tag) => (
                      <span key={tag} className="px-2.5 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-600">
                        {tag}
                      </span>
                    ))}
                  </div>
                </>
              )}
              {uploadState === "error" && (
                <>
                  <div className="text-[15px] font-semibold text-red-600">✗ Upload failed</div>
                  <div className="text-[13px] text-gray-500">{errorMsg}. Please try again.</div>
                </>
              )}
            </div>

            {uploadState === "idle" && (
              <span className="text-xl text-gray-800 flex-shrink-0">›</span>
            )}
          </button>

          {/* Fill online card — not yet implemented */}
          <div className="flex items-center gap-4 bg-gray-50 border border-gray-200 rounded-xl p-5 opacity-50 cursor-not-allowed">
            <div className="w-11 h-11 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0 text-lg">
              ✏
            </div>
            <div className="flex-1">
              <div className="text-[15px] font-semibold mb-1">Fill out your resume online</div>
              <div className="text-[13px] text-gray-500">Coming soon</div>
            </div>
            <span className="text-xl text-gray-400 flex-shrink-0">›</span>
          </div>
        </div>

        {/* Retry button */}
        {uploadState === "error" && (
          <button
            className="text-sm text-blue-600 underline text-center"
            onClick={() => { setUploadState("idle"); fileInputRef.current?.click(); }}
          >
            Try again
          </button>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
      />
    </main>
  );
}
