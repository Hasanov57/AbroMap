"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useRouter } from "@/i18n/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  BookOpen,
  BriefcaseBusiness,
  GraduationCap,
  Search,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import { countryName } from "@/lib/countries";
import { SearchCombobox, type ComboOption } from "@/components/search-combobox";
import type { AcademicField, Country, Profile, University } from "@/lib/types";

const initial: Profile = {
  degree: "master",
  field: "",
  countries: [],
  scholarship_priority: "preferred",
  budget_period: "year",
  citizenship: "AZ",
};
const basicSchema = z.object({
  degree: z.enum(["bachelor", "master", "phd"]),
  field: z.string().min(1),
});

export function Onboarding() {
  const locale = useLocale();
  const t = useTranslations("onboarding"),
    common = useTranslations("common"),
    d = useTranslations("degrees");
  const router = useRouter();
  const { watch, setValue, reset } = useForm<Profile>({
    defaultValues: initial,
  });
  const profile = watch();
  const [step, setStep] = useState(0);
  const [countryOptions, setCountryOptions] = useState<Country[]>([]);
  const [countrySearch, setCountrySearch] = useState("");
  const [fieldSelection, setFieldSelection] = useState<AcademicField | null>(null);
  const [previousSelection, setPreviousSelection] = useState<AcademicField | null>(null);
  const [universitySelection, setUniversitySelection] = useState<University | null>(null);
  const [wantsUniversity, setWantsUniversity] = useState(false);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      const saved = localStorage.getItem("abromap-profile");
      if (saved) {
        const restored = { ...initial, ...JSON.parse(saved) } as Profile;
        if (restored.field !== "custom") restored.field = restored.field.replaceAll("_", "-");
        if (restored.previous_field) restored.previous_field = restored.previous_field.replaceAll("_", "-");
        reset(restored);
        setWantsUniversity(Boolean(restored.university_id));
      }
      const savedStep = Number(localStorage.getItem("abromap-step"));
      if (Number.isInteger(savedStep) && savedStep >= 0 && savedStep < 8)
        setStep(savedStep);
    } catch {}
    setReady(true);
  }, [reset]);
  useEffect(() => { api.countries(locale).then(setCountryOptions).catch(() => {}); }, [locale]);
  useEffect(() => {
    if (profile.field && profile.field !== "custom")
      api.fieldSearch(profile.field, locale, 5).then((rows) =>
        setFieldSelection(rows.find((row) => row.slug === profile.field) || null)).catch(() => {});
  }, [profile.field, locale]);
  useEffect(() => {
    if (profile.previous_field)
      api.fieldSearch(profile.previous_field, locale, 5).then((rows) =>
        setPreviousSelection(rows.find((row) => row.slug === profile.previous_field) || null)).catch(() => {});
  }, [profile.previous_field, locale]);
  useEffect(() => {
    if (profile.university_id)
      api.universityById(profile.university_id).then(setUniversitySelection).catch(() => {});
  }, [profile.university_id]);
  useEffect(() => {
    if (ready) localStorage.setItem("abromap-profile", JSON.stringify(profile));
  }, [profile, ready]);
  useEffect(() => {
    if (ready) localStorage.setItem("abromap-step", String(step));
  }, [step, ready]);
  function update<K extends keyof Profile>(key: K, value: Profile[K]) {
    setValue(key, value as never);
    setError("");
  }
  function next() {
    if (step === 1 && (!basicSchema.safeParse(profile).success ||
        (profile.field === "custom" && !profile.custom_field?.trim()))) {
      setError(t("validation"));
      return;
    }
    if (step < 7) {
      setStep(step + 1);
      window.scrollTo(0, 0);
    } else {
      sessionStorage.removeItem("abromap-results");
      router.push("/results");
    }
  }
  function numberValue(value: string) {
    return value === "" ? undefined : Number(value);
  }
  const stepTitles = [
    "step1",
    "step2",
    "step3",
    "step4",
    "step5",
    "step6",
    "step7",
    "step8",
  ] as const;
  const visibleCountries = countryOptions.filter((row) =>
    `${row.name} ${row.iso_code}`.toLocaleLowerCase(locale).includes(countrySearch.toLocaleLowerCase(locale)));
  const fieldOptions = (query: string): Promise<ComboOption[]> =>
    api.fieldSearch(query, locale).then((rows) => rows.map((row) =>
      ({ id: row.slug, label: row.name, secondary: row.category })));
  return (
    <div className="page">
      <div className="container wizard">
        <div className="wizard-top">
          <span>{t("intro")}</span>
          <span>{t("step", { current: step + 1, total: 8 })}</span>
        </div>
        <div className="progress-track">
          <div style={{ width: `${(step + 1) * 12.5}%` }} />
        </div>
        <div className="wizard-card">
          <h1>{t(stepTitles[step])}</h1>
          <p>
            {step === 0
              ? t("introText")
              : step === 2
                ? t("examNote")
                : step === 3
                  ? t("countryNote")
                  : ""}
          </p>
          {step === 0 && (
            <div className="choice-grid">
              {(["bachelor", "master", "phd"] as const).map((degree, i) => (
                <button
                  type="button"
                  className={`choice ${profile.degree === degree ? "selected" : ""}`}
                  key={degree}
                  onClick={() => update("degree", degree)}
                >
                  {
                    [
                      <BookOpen key="a" />,
                      <GraduationCap key="b" />,
                      <BriefcaseBusiness key="c" />,
                    ][i]
                  }
                  {d(degree)}
                  {profile.degree === degree && (
                    <Check size={18} style={{ marginLeft: "auto" }} />
                  )}
                </button>
              ))}
            </div>
          )}
          {step === 1 && (
            <div className="grid">
              <div className="field">
                <label htmlFor="status">{t("status")}</label>
                <select
                  id="status"
                  value={profile.academic_status || ""}
                  onChange={(e) => update("academic_status", e.target.value)}
                >
                  <option value="">{common("unknown")}</option>
                  {(
                    [
                      "statusSchool",
                      "statusSchoolGrad",
                      "statusBachelor",
                      "statusBachelorGrad",
                      "statusMaster",
                      "statusMasterGrad",
                    ] as const
                  ).map((key) => (
                    <option key={key} value={key}>
                      {t(key)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-grid">
                <div className="field">
                  <label htmlFor="gpa">{t("gpa")}</label>
                  <input
                    id="gpa"
                    type="number"
                    min="0"
                    max={profile.gpa_scale || 100}
                    step="0.01"
                    value={profile.gpa ?? ""}
                    onChange={(e) => update("gpa", numberValue(e.target.value))}
                  />
                </div>
                <div className="field">
                  <label htmlFor="scale">{t("gpaScale")}</label>
                  <select
                    id="scale"
                    value={profile.gpa_scale || ""}
                    onChange={(e) =>
                      update("gpa_scale", numberValue(e.target.value))
                    }
                  >
                    <option value="">{common("unknown")}</option>
                    {[4, 5, 10, 100].map((x) => (
                      <option key={x} value={x}>
                        {x}.0
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="note">{t("gpaNote")}</div>
              {profile.field === "custom" ? <div className="field">
                <label htmlFor="customMajor">{t("customMajor")}</label>
                <input id="customMajor" value={profile.custom_field || ""}
                  onChange={(event) => update("custom_field", event.target.value)} />
                <button type="button" className="button secondary small" style={{ marginTop: 10 }}
                  onClick={() => { update("field", ""); update("custom_field", ""); }}>
                  {t("chooseFromCatalog")}
                </button>
              </div> : <>
                <SearchCombobox label={t("field")} placeholder={t("searchMajor")}
                  emptyMessage={t("noMajors")} clearLabel={common("clear")}
                  value={profile.field} selectedLabel={fieldSelection?.name}
                  fetchOptions={fieldOptions}
                  onChange={(id) => { setFieldSelection(null); update("field", id); }} />
                <button type="button" className="button secondary small" onClick={() => update("field", "custom")}
                  style={{ justifySelf: "start" }}>{t("cannotFindMajor")}</button>
              </>}
              {profile.degree !== "bachelor" && (
                <SearchCombobox label={t("previousField")} placeholder={t("searchMajor")}
                  emptyMessage={t("noMajors")} clearLabel={common("clear")}
                  value={profile.previous_field || ""} selectedLabel={previousSelection?.name}
                  fetchOptions={fieldOptions}
                  onChange={(id) => { setPreviousSelection(null); update("previous_field", id); }} />
              )}
              {profile.degree === "phd" && (
                <div className="field">
                  <label htmlFor="research">{t("research")}</label>
                  <textarea
                    id="research"
                    value={profile.research_interests || ""}
                    onChange={(e) =>
                      update("research_interests", e.target.value)
                    }
                  />
                </div>
              )}
            </div>
          )}
          {step === 2 && (
            <div className="grid three">
              {(profile.degree === "bachelor"
                ? ["IELTS", "TOEFL", "SAT"]
                : ["IELTS", "TOEFL", "GRE", "GMAT"]
              ).map((test) => {
                const key = test.toLowerCase() as
                  "ielts" | "toefl" | "sat" | "gre" | "gmat";
                return (
                  <div className="field" key={key}>
                    <label htmlFor={key}>{test}</label>
                    <input
                      id={key}
                      type="number"
                      min="0"
                      step={key === "ielts" ? "0.5" : "1"}
                      placeholder={t("notTaken")}
                      value={profile[key] ?? ""}
                      onChange={(e) => update(key, numberValue(e.target.value))}
                    />
                    <small>{t("notTaken")}</small>
                  </div>
                );
              })}
              <div className="field">
                <label htmlFor="hskLevel">{t("hskLevel")}</label>
                <input id="hskLevel" type="number" min="1" max="9"
                  placeholder={t("notTaken")} value={profile.hsk_level ?? ""}
                  onChange={(e) => update("hsk_level", numberValue(e.target.value))} />
              </div>
              <div className="field">
                <label htmlFor="hskScore">{t("hskScore")}</label>
                <input id="hskScore" type="number" min="0" max="300"
                  placeholder={t("notTaken")} value={profile.hsk_score ?? ""}
                  onChange={(e) => update("hsk_score", numberValue(e.target.value))} />
              </div>
              <div className="field">
                <label htmlFor="englishCefr">{t("englishCefr")}</label>
                <select id="englishCefr" value={profile.english_cefr || ""}
                  onChange={(e) => update("english_cefr", e.target.value)}>
                  <option value="">{common("unknown")}</option>
                  {["A1", "A2", "B1", "B2", "C1", "C2"].map((level) =>
                    <option key={level} value={level}>{level}</option>)}
                </select>
              </div>
            </div>
          )}
          {step === 3 && (
            <div className="grid">
              <div className="field"><label htmlFor="countrySearch">{t("searchCountry")}</label>
                <input id="countrySearch" value={countrySearch}
                  onChange={(event) => setCountrySearch(event.target.value)}
                  placeholder={t("searchCountry")} /></div>
              <div className="choice-grid country-options-scroll">
              <button
                type="button"
                className={`choice ${profile.countries.length === 0 ? "selected" : ""}`}
                onClick={() => update("countries", [])}
              >
                <Search />
                {t("notSure")}
              </button>
              {visibleCountries.map((row) => (
                <button
                  type="button"
                  key={row.iso_code}
                  className={`choice ${profile.countries.includes(row.iso_code) ? "selected" : ""}`}
                  onClick={() =>
                    update(
                      "countries",
                      profile.countries.includes(row.iso_code)
                        ? profile.countries.filter((x) => x !== row.iso_code)
                        : [...profile.countries, row.iso_code],
                    )
                  }
                >
                  <span>{row.name}<small className="country-availability">
                    {t("countryAvailability", { universities: row.university_count, programs: row.verified_program_count })}
                  </small></span>
                  {profile.countries.includes(row.iso_code) && (
                    <Check size={18} style={{ marginLeft: "auto" }} />
                  )}
                </button>
              ))}
              </div>
            </div>
          )}
          {step === 4 && (
            <div className="grid">
              <div className="choice-grid">
                <button
                  type="button"
                  className={`choice ${!wantsUniversity ? "selected" : ""}`}
                  onClick={() => { setWantsUniversity(false); update("university_id", undefined); }}
                >
                  {t("notSure")}
                </button>
                <button
                  type="button"
                  className={`choice ${wantsUniversity ? "selected" : ""}`}
                  onClick={() => setWantsUniversity(true)}
                >
                  {t("yes")}
                </button>
              </div>
              {wantsUniversity && (
                <SearchCombobox label={t("university")} placeholder={t("searchUniversity")}
                  emptyMessage={t("noUniversities")} clearLabel={common("clear")}
                  value={profile.university_id ? String(profile.university_id) : ""}
                  selectedLabel={universitySelection?.name}
                  fetchOptions={(query) => api.universitiesPage({ search: query,
                    country: profile.countries.length === 1 ? profile.countries[0] : undefined,
                    page_size: 12 }).then((page) => page.items.map((row) =>
                    ({ id: String(row.id), label: row.name,
                       secondary: `${row.city}, ${countryName(row.country, locale)}` })))}
                  onChange={(id) => { setUniversitySelection(null); update("university_id", id ? Number(id) : undefined); }} />
              )}
            </div>
          )}
          {step === 5 && (
            <div className="grid">
              <div className="field">
                <label>{t("budgetOptions")}</label>
                <div className="choice-grid">
                  {[
                    ["fullOnly", 0, "required"],
                    ["budgetLow", 3000, "preferred"],
                    ["budgetMid", 7000, "preferred"],
                    ["budgetHigh", 15000, "preferred"],
                    ["budgetPlus", 30000, "preferred"],
                    ["budgetUnknown", undefined, "preferred"],
                  ].map(([key, amount, priority]) => (
                    <button
                      type="button"
                      key={String(key)}
                      className={`choice ${profile.budget_eur === amount ? "selected" : ""}`}
                      onClick={() => {
                        update("budget_eur", amount as number | undefined);
                        update("budget_period", "year");
                        update("scholarship_priority", String(priority));
                      }}
                    >
                      {t(String(key))}
                    </button>
                  ))}
                </div>
              </div>
              <div className="field">
                <label htmlFor="budget">{t("budget")}</label>
                <input
                  id="budget"
                  type="number"
                  min="0"
                  value={profile.budget_eur ?? ""}
                  onChange={(e) =>
                    (update("budget_eur", numberValue(e.target.value)), update("budget_period", "year"))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="scholarship">{t("scholarship")}</label>
                <select
                  id="scholarship"
                  value={profile.scholarship_priority}
                  onChange={(e) =>
                    update("scholarship_priority", e.target.value)
                  }
                >
                  <option value="required">{t("scholarshipRequired")}</option>
                  <option value="partial">{t("scholarshipPartial")}</option>
                  <option value="preferred">{t("scholarshipPreferred")}</option>
                  <option value="none">{t("scholarshipNone")}</option>
                </select>
              </div>
              <div className="note">{t("costNote")}</div>
            </div>
          )}
          {step === 6 && (
            <div className="field-grid">
              <div className="field">
                <label htmlFor="teachingLanguage">
                  {t("teachingLanguage")}
                </label>
                <select
                  id="teachingLanguage"
                  value={profile.teaching_language || ""}
                  onChange={(e) => update("teaching_language", e.target.value)}
                >
                  <option value="">{common("all")}</option>
                  <option>English</option>
                  <option>German</option>
                  <option>Italian</option>
                  <option>Hungarian</option>
                  <option>Chinese</option>
                  <option>Chinese and English</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="intake">{t("intake")}</label>
                <input
                  id="intake"
                  type="number"
                  min="2025"
                  max="2100"
                  value={profile.intake_year ?? ""}
                  onChange={(e) =>
                    update("intake_year", numberValue(e.target.value))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="semester">{t("semester")}</label>
                <select
                  id="semester"
                  value={profile.semester || ""}
                  onChange={(e) => update("semester", e.target.value)}
                >
                  <option value="">{common("unknown")}</option>
                  <option value="autumn">{t("autumn")}</option>
                  <option value="spring">{t("spring")}</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="citizenship">{t("citizenship")}</label>
                <input
                  id="citizenship"
                  maxLength={2}
                  value={profile.citizenship}
                  onChange={(e) =>
                    update("citizenship", e.target.value.toUpperCase())
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="studyFormat">{t("studyFormat")}</label>
                <select
                  id="studyFormat"
                  value={profile.study_format || ""}
                  onChange={(e) => update("study_format", e.target.value)}
                >
                  <option value="">{common("all")}</option>
                  <option value="on_campus">{t("onCampus")}</option>
                  <option value="online">{t("online")}</option>
                </select>
              </div>
            </div>
          )}
          {step === 7 && (
            <div className="detail-list">
              <div>
                <small>{common("degree")}</small>
                <strong>{d(profile.degree)}</strong>
              </div>
              <div>
                <small>{common("field")}</small>
                <strong>
                  {profile.field === "custom" ? profile.custom_field || common("unknown")
                    : fieldSelection?.name || profile.field.replaceAll("-", " ") || common("unknown")}
                </strong>
              </div>
              <div>
                <small>{t("yourGpa")}</small>
                <strong>
                  {profile.gpa !== undefined
                    ? `${profile.gpa}/${profile.gpa_scale || "?"}`
                    : common("unknown")}
                </strong>
              </div>
              <div>
                <small>{t("yourTests")}</small>
                <strong>
                  {profile.hsk_level
                    ? `HSK ${profile.hsk_level}${profile.hsk_score ? ` (${profile.hsk_score})` : ""}`
                    : profile.ielts
                    ? `IELTS ${profile.ielts}`
                    : profile.toefl
                      ? `TOEFL ${profile.toefl}`
                      : common("unknown")}
                </strong>
              </div>
              <div>
                <small>{t("yourCountries")}</small>
                <strong>
                  {profile.countries.length
                    ? profile.countries
                        .map((x) => countryOptions.find((row) => row.iso_code === x)?.name || countryName(x, locale))
                        .join(", ")
                    : t("notSure")}
                </strong>
              </div>
              <div>
                <small>{t("yourBudget")}</small>
                <strong>
                  {profile.budget_eur !== undefined
                    ? `€${profile.budget_eur.toLocaleString()}`
                    : t("budgetUnknown")}
                </strong>
              </div>
            </div>
          )}
          {profile.field && [1, 3, 4, 7].includes(step) &&
            <div className="note" style={{ marginTop: 20 }}>{t("catalogAvailabilityNote")}</div>}
          {error && (
            <div className="error" style={{ marginTop: 20 }}>
              {error}
            </div>
          )}
          <div className="wizard-actions">
            <button
              className="button secondary"
              type="button"
              disabled={step === 0}
              onClick={() => {
                setStep(step - 1);
                window.scrollTo(0, 0);
              }}
            >
              {common("back")}
            </button>
            <button className="button" type="button" onClick={next}>
              {step === 7 ? t("find") : common("next")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
