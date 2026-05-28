import { create } from "zustand";
import type { ParsedResume, Preferences, JobMatch } from "@/types";

type Step = 1 | 2 | 3 | 4;

interface OnboardingState {
  step: Step;
  resumeId: string | null;
  parsedResume: ParsedResume | null;
  preferences: Partial<Omit<Preferences, "resume_id">>;
  matchData: JobMatch[];
  feedbackReasons: { jobIdx: number; reason: string }[];

  setStep: (step: Step) => void;
  setResume: (id: string, parsed: ParsedResume) => void;
  updatePreferences: (p: Partial<Omit<Preferences, "resume_id">>) => void;
  setMatchData: (matches: JobMatch[]) => void;
  addFeedbackReason: (item: { jobIdx: number; reason: string }) => void;
}

export const useOnboarding = create<OnboardingState>((set) => ({
  step: 1,
  resumeId: null,
  parsedResume: null,
  preferences: {},
  matchData: [],
  feedbackReasons: [],

  setStep: (step) => set({ step }),
  setResume: (resumeId, parsedResume) => set({ resumeId, parsedResume }),
  updatePreferences: (p) =>
    set((s) => ({ preferences: { ...s.preferences, ...p } })),
  setMatchData: (matchData) => set({ matchData }),
  addFeedbackReason: (item) =>
    set((s) => ({ feedbackReasons: [...s.feedbackReasons, item] })),
}));
