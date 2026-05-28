// ── Resume ────────────────────────────────────────────────────────────────────

export interface ParsedResume {
  name:                string;
  email:               string | null;
  location:            string | null;
  years_of_experience: number | null;
  education: {
    degree: string;
    school: string;
    year:   string | null;
  }[];
  work_experience: {
    title:    string;
    company:  string;
    duration: string;
    bullets:  string[];
  }[];
  skills:    string[];
  languages: string[];
  summary:   string | null;
}

export interface ParseResumeResponse {
  resume_id:   string;
  parsed:      ParsedResume;
  ocr_warning: boolean;
  confidence:  number;
}

// ── Preferences ───────────────────────────────────────────────────────────────

export type WorkArrangement = "onsite" | "hybrid" | "remote" | "open";
export type JobType         = "full-time" | "part-time" | "contract" | "internship";

export interface Preferences {
  resume_id:         string;
  job_functions:     string[];
  work_arrangement:  WorkArrangement | null;
  location:          string | null;
  job_type:          JobType | null;
  salary_min:        number | null;
  salary_max:        number | null;
  salary_negotiable: boolean;
  extra_notes:       string[];
  feedback_reasons:  { jobIdx?: number; jd_id?: string; reason: string }[];
}

export interface ExtractedSlots {
  job_functions:    string[] | null;
  work_arrangement: WorkArrangement | null;
  location:         string | null;
  job_type:         JobType | null;
  salary_min:       number | null;
  salary_max:       number | null;
  extra_notes:      string[];
}

// ── Matches ───────────────────────────────────────────────────────────────────

export interface JobMatch {
  id:               string;
  title:            string;
  company:          string;
  location:         string;
  work_arrangement: WorkArrangement | null;
  salary_min:       number | null;
  salary_max:       number | null;
  currency:         string;
  highlights:       string[];
  tags:             string[];
  match_score:      number;   // 0–100
  why_fit:          string[]; // 2–3 bullets from Llama
}

export interface MatchFeedback {
  resume_id: string;
  jd_id:     string;
  action:    "like" | "dislike";
  reason?:   string;
}
