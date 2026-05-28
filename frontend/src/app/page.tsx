"use client";

import { useOnboarding } from "@/store/onboarding";
import { StepNav } from "@/components/layout/StepNav";
import { ResumeUpload } from "@/components/steps/ResumeUpload";
import { Preferences } from "@/components/steps/Preferences";
import { Matches } from "@/components/steps/Matches";
import { Explore } from "@/components/steps/Explore";

export default function Home() {
  const step = useOnboarding((s) => s.step);

  return (
    <div className="flex flex-col min-h-screen">
      <StepNav />
      {step === 1 && <ResumeUpload />}
      {step === 2 && <Preferences />}
      {step === 3 && <Matches />}
      {step === 4 && <Explore />}
    </div>
  );
}
