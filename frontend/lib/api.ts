import type {
  MatchResponse,
  Profile,
  Program,
  Scholarship,
  University,
  UniversityPage,
  Country,
  AcademicField,
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
  countries: (locale = "az") =>
    request<Country[]>(`/countries?locale=${encodeURIComponent(locale)}`),
  fieldSearch: (q: string, locale = "az", limit = 10) =>
    request<AcademicField[]>(`/academic-fields/search?q=${encodeURIComponent(q)}&locale=${encodeURIComponent(locale)}&limit=${limit}`),
  universities: (query = "") => request<University[]>(`/universities${query}`),
  universitiesPage: (params: { page?: number; page_size?: number; search?: string; country?: string; city?: string } = {}) =>
    request<UniversityPage>(`/universities?${new URLSearchParams({ page: String(params.page || 1), page_size: String(params.page_size || 20), ...(params.search ? { search: params.search } : {}), ...(params.country ? { country: params.country } : {}), ...(params.city ? { city: params.city } : {}) }).toString()}`),
  university: (slug: string) => request<University>(`/universities/${slug}`),
  universityById: (id: number) => request<University>(`/universities/by-id/${id}`),
  programs: (query = "") => request<Program[]>(`/programs${query}`),
  program: (id: number) => request<Program>(`/programs/${id}`),
  scholarships: (query = "") => request<Scholarship[]>(`/scholarships${query}`),
  match: (profile: Profile, page = 1) =>
    request<MatchResponse>(`/matching/evaluate?page=${page}`, {
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
