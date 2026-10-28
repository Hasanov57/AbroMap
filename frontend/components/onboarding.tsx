"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useRouter } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import {
  BookOpen,
  BriefcaseBusiness,
  GraduationCap,
  Search,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import type { Profile, University } from "@/lib/types";

const fields = [
  "computer_science",
  "artificial_intelligence",
  "data_science",
  "software_engineering",
  "business_administration",
  "economics",
  "medicine",
  "engineering",
  "law",
  "architecture",
  "social_sciences",
  "other",
] as const;
const countries = ["DE", "IT", "HU", "NL", "GB", "US", "TR", "PL"] as const;
const initial: Profile = {
  degree: "master",
  field: "",
  countries: [],
  scholarship_priority: "preferred",
  citizenship: "AZ",
};
const basicSchema = z.object({
  degree: z.enum(["bachelor", "master", "phd"]),
  field: z.string().min(1),
});

export function Onboarding() {
  const t = useTranslations("onboarding"),
    common = useTranslations("common"),
    f = useTranslations("fields"),
    d = useTranslations("degrees"),
    c = useTranslations("countryNames");
  const router = useRouter();
  const { watch, setValue, reset } = useForm<Profile>({
    defaultValues: initial,
  });
  const profile = watch();
  const [step, setStep] = useState(0);
  const [universities, setUniversities] = useState<University[]>([]);
  const [catalogLoaded, setCatalogLoaded] = useState(false);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      const saved = localStorage.getItem("abromap-profile");
      if (saved) reset({ ...initial, ...JSON.parse(saved) });
      const savedStep = Number(localStorage.getItem("abromap-step"));
      if (Number.isInteger(savedStep) && savedStep >= 0 && savedStep < 8)
        setStep(savedStep);
    } catch {}
    setReady(true);
    api
      .universities()
      .then((items) => {
        setUniversities(items);
        setCatalogLoaded(true);
      })
      .catch(() => {});
  }, [reset]);
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
    if (step === 1 && !basicSchema.safeParse(profile).success) {
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
  const availableCount = universities.reduce(
    (count, university) =>
      count +
      ((!profile.countries.length ||
        profile.countries.includes(university.country)) &&
      (!profile.university_id || profile.university_id === university.id)
        ? university.programs.filter(
            (program) =>
              program.degree === profile.degree &&
              program.field === profile.field,
          ).length
        : 0),
    0,
  );
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
              <div className="field">
                <label htmlFor="field">{t("field")}</label>
                <select
                  id="field"
                  value={profile.field}
                  onChange={(e) => update("field", e.target.value)}
                >
                  <option value="">{common("unknown")}</option>
                  {fields.map((x) => (
                    <option key={x} value={x}>
                      {f(x)}
                    </option>
                  ))}
                </select>
              </div>
              {profile.degree !== "bachelor" && (
                <div className="field">
                  <label htmlFor="previous">{t("previousField")}</label>
                  <select
                    id="previous"
                    value={profile.previous_field || ""}
                    onChange={(e) => update("previous_field", e.target.value)}
                  >
                    <option value="">{common("unknown")}</option>
                    {fields.map((x) => (
                      <option key={x} value={x}>
                        {f(x)}
                      </option>
                    ))}
                  </select>
                </div>
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
            </div>
          )}
          {step === 3 && (
            <div className="choice-grid">
              <button
                type="button"
                className={`choice ${profile.countries.length === 0 ? "selected" : ""}`}
                onClick={() => update("countries", [])}
              >
                <Search />
                {t("notSure")}
              </button>
              {countries.map((code) => (
                <button
                  type="button"
                  key={code}
                  className={`choice ${profile.countries.includes(code) ? "selected" : ""}`}
                  onClick={() =>
                    update(
                      "countries",
                      profile.countries.includes(code)
                        ? profile.countries.filter((x) => x !== code)
                        : [...profile.countries, code],
                    )
                  }
                >
                  {c(code)}
                  {profile.countries.includes(code) && (
                    <Check size={18} style={{ marginLeft: "auto" }} />
                  )}
                </button>
              ))}
            </div>
          )}
          {step === 4 && (
            <div className="grid">
              <div className="choice-grid">
                <button
                  type="button"
                  className={`choice ${!profile.university_id ? "selected" : ""}`}
                  onClick={() => update("university_id", undefined)}
                >
                  {t("notSure")}
                </button>
                <button
                  type="button"
                  className={`choice ${profile.university_id ? "selected" : ""}`}
                  onClick={() => update("university_id", universities[0]?.id)}
                >
                  {t("yes")}
                </button>
              </div>
              {!!profile.university_id && (
                <div className="field">
                  <label htmlFor="university">{t("university")}</label>
                  <select
                    id="university"
                    value={profile.university_id}
                    onChange={(e) =>
                      update("university_id", Number(e.target.value))
                    }
                  >
                    {universities.map((x) => (
                      <option key={x.id} value={x.id}>
                        {x.name}
                      </option>
                    ))}
                  </select>
                </div>
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
                    update("budget_eur", numberValue(e.target.value))
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
                  {profile.field
                    ? f(profile.field as (typeof fields)[number])
                    : common("unknown")}
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
                  {profile.ielts
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
                        .map((x) => c(x as (typeof countries)[number]))
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
          {catalogLoaded && profile.field && [1, 3, 4, 7].includes(step) && (
            <div
              className={availableCount ? "note" : "error"}
              style={{ marginTop: 20 }}
            >
              {availableCount
                ? t("catalogCount", { count: availableCount })
                : t("catalogNone")}
            </div>
          )}
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
