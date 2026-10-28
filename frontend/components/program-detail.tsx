"use client";
import { useEffect, useState } from "react";
import { Bookmark, ExternalLink, MessageCircle, Send } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { Program, University } from "@/lib/types";
export function ProgramDetail({ id }: { id: number }) {
  const locale = useLocale(),
    t = useTranslations("detail"),
    common = useTranslations("common"),
    fields = useTranslations("fields"),
    degrees = useTranslations("degrees"),
    country = useTranslations("countryNames");
  const [item, setItem] = useState<Program | null>(null),
    [university, setUniversity] = useState<University | null>(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(false),
    [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState(""),
    [asking, setAsking] = useState(false),
    [saved, setSaved] = useState(false);
  useEffect(() => {
    Promise.all([api.program(id), api.universities()])
      .then(([program, universities]) => {
        setItem(program);
        setUniversity(
          universities.find((u) => u.programs.some((p) => p.id === id)) || null,
        );
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
    try {
      setSaved(
        (
          JSON.parse(localStorage.getItem("abromap-saved") || "[]") as number[]
        ).includes(id),
      );
    } catch {}
  }, [id]);
  function save() {
    const existing = JSON.parse(
      localStorage.getItem("abromap-saved") || "[]",
    ) as number[];
    const next = saved ? existing.filter((x) => x !== id) : [...existing, id];
    localStorage.setItem("abromap-saved", JSON.stringify(next));
    setSaved(!saved);
  }
  async function ask() {
    if (!question.trim()) return;
    setAsking(true);
    try {
      const data = await api.chat(question, id, locale);
      setAnswer(data.answer);
    } catch {
      setAnswer(common("error"));
    } finally {
      setAsking(false);
    }
  }
  const req = item?.requirements[0];
  const historical = req
    ? Number(req.academic_year.slice(5)) <= new Date().getFullYear()
    : false;
  return (
    <div className="page">
      <div className="container">
        {loading ? (
          <div className="skeleton" />
        ) : error || !item ? (
          <div className="error">{common("error")}</div>
        ) : (
          <>
            <div className="page-heading">
              <div className="row">
                <span className="tag">
                  {degrees(item.degree as "bachelor" | "master" | "phd")}
                </span>
                <span className="tag demo">{common("demo")}</span>
              </div>
              <h1>{item.name}</h1>
              <p>
                {university ? (
                  <>
                    <Link href={`/universities/${university.slug}`}>
                      {university.name}
                    </Link>{" "}
                    · {university.city},{" "}
                    {country(
                      university.country as
                        "DE" | "IT" | "HU" | "NL" | "GB" | "US" | "TR" | "PL",
                    )}
                  </>
                ) : (
                  fields(item.field as "computer_science")
                )}
              </p>
            </div>
            <div className="detail-grid">
              <div>
                <section className="card">
                  <h3>{t("requirements")}</h3>
                  <p>{t("requirementsNote")}</p>
                  {req ? (
                    <>
                      <div className="row" style={{ margin: "18px 0" }}>
                        <span className="tag warn">
                          {historical ? common("historical") : common("year")} ·{" "}
                          {req.academic_year}
                        </span>
                        <span className="tag demo">
                          {req.status === "verified_current"
                            ? common("verifiedCurrent")
                            : req.status === "verified_historical"
                              ? common("verifiedHistorical")
                              : common("unverified")}
                        </span>
                      </div>
                      <div className="detail-list">
                        <div>
                          <small>{t("gpa")}</small>
                          <strong>
                            {req.min_gpa === null
                              ? common("unknown")
                              : `${req.min_gpa}/${req.gpa_scale}`}
                          </strong>
                        </div>
                        <div>
                          <small>{t("ielts")}</small>
                          <strong>{req.ielts_min ?? common("unknown")}</strong>
                        </div>
                        <div>
                          <small>{t("toefl")}</small>
                          <strong>{req.toefl_min ?? common("unknown")}</strong>
                        </div>
                        <div>
                          <small>{t("previousField")}</small>
                          <strong>
                            {req.previous_field
                              ? fields(req.previous_field as "computer_science")
                              : common("unknown")}
                          </strong>
                        </div>
                      </div>
                      {req.verified_at && (
                        <p className="small-text muted">
                          {common("verifiedAt", { date: req.verified_at })}
                        </p>
                      )}
                      <div className="divider" />
                      {req.source_url ? (
                        <a
                          href={req.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="button secondary small"
                        >
                          {common("source")} <ExternalLink size={15} />
                        </a>
                      ) : (
                        <p className="small-text">{common("noSource")}</p>
                      )}
                    </>
                  ) : (
                    <div className="note">{t("noRequirements")}</div>
                  )}
                </section>
                <section className="card">
                  <h3>{t("askAI")}</h3>
                  <div className="row">
                    <input
                      className="input"
                      style={{ flex: "1 1 250px" }}
                      placeholder={t("aiQuestion")}
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") ask();
                      }}
                    />
                    <button
                      className="button small"
                      onClick={ask}
                      disabled={asking}
                    >
                      <Send size={16} />
                      {asking ? common("loading") : t("send")}
                    </button>
                  </div>
                  {answer && (
                    <div className="note" style={{ marginTop: 16 }}>
                      <MessageCircle size={17} />
                      <p>{answer}</p>
                    </div>
                  )}
                  <p className="small-text muted" style={{ marginTop: 14 }}>
                    {t("aiFallback")}
                  </p>
                </section>
              </div>
              <aside>
                <div className="card">
                  <div
                    className="detail-list"
                    style={{ gridTemplateColumns: "1fr" }}
                  >
                    <div>
                      <small>{common("tuition")}</small>
                      <strong>
                        {item.tuition_eur === null
                          ? common("unknown")
                          : `€${item.tuition_eur.toLocaleString()}`}
                      </strong>
                    </div>
                    <div>
                      <small>{common("language")}</small>
                      <strong>{item.teaching_language}</strong>
                    </div>
                    <div>
                      <small>{t("duration")}</small>
                      <strong>
                        {item.duration_months
                          ? t("months", { count: item.duration_months })
                          : common("unknown")}
                      </strong>
                    </div>
                  </div>
                  <div className="divider" />
                  <div className="grid">
                    <button className="button" onClick={save}>
                      <Bookmark size={16} fill={saved ? "white" : "none"} />
                      {t("save")}
                    </button>
                    <Link
                      href={`/roadmap?program=${id}`}
                      className="button secondary"
                    >
                      {t("roadmap")}
                    </Link>
                    {item.official_url && (
                      <a
                        className="button secondary"
                        href={item.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {t("official")} <ExternalLink size={16} />
                      </a>
                    )}
                  </div>
                  <p className="small-text muted" style={{ marginTop: 16 }}>
                    {common("demo")}
                  </p>
                </div>
              </aside>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
