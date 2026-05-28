import type {
  ParseResumeResponse,
  Preferences,
  ExtractedSlots,
  JobMatch,
  MatchFeedback,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Resume ────────────────────────────────────────────────────────────────────

export async function parseResume(file: File): Promise<ParseResumeResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/resume/parse`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Preferences ───────────────────────────────────────────────────────────────

export async function extractPreferences(text: string): Promise<ExtractedSlots> {
  return post("/api/preferences/extract", { text });
}

export async function savePreferences(prefs: Preferences): Promise<{ preference_id: string }> {
  return post("/api/preferences/save", prefs);
}

// ── Matches ───────────────────────────────────────────────────────────────────

export async function searchMatches(
  resume_id: string,
  top_n = 3
): Promise<{ matches: JobMatch[] }> {
  return post("/api/matches/search", { resume_id, top_n });
}

export async function sendFeedback(feedback: MatchFeedback): Promise<void> {
  await post("/api/matches/feedback", feedback);
}
