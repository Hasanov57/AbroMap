import type {
  MatchResponse,
  Profile,
  Program,
  Scholarship,
  University,
} from "./types";
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1${path}`, {
    cache: "no-store",
    ...init,
  });
  if (!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}
export const api = {
  countries: () =>
    request<{ code: string; program_count: number }[]>("/countries"),
  universities: (query = "") => request<University[]>(`/universities${query}`),
  university: (slug: string) => request<University>(`/universities/${slug}`),
  programs: (query = "") => request<Program[]>(`/programs${query}`),
  program: (id: number) => request<Program>(`/programs/${id}`),
  scholarships: (query = "") => request<Scholarship[]>(`/scholarships${query}`),
  match: (profile: Profile) =>
    request<MatchResponse>("/matching/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    }),
  chat: (message: string, program_id?: number, locale = "az") =>
    request<{ answer: string; sources: string[]; configured: boolean }>(
      "/ai/chat",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, program_id, locale }),
      },
    ),
};
