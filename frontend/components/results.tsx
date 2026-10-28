"use client";
import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  Bookmark,
  GitCompareArrows,
  SlidersHorizontal,
} from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import { countryName } from "@/lib/countries";
import type { Match, Profile } from "@/lib/types";
export function Results() {
  const locale = useLocale(), t = useTranslations("results"),
    common = useTranslations("common"),
    notes = useTranslations("matchNotes");
  const [rows, setRows] = useState<Match[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(false),
    [noMatchReason, setNoMatchReason] = useState<string | null>(null),
    [page, setPage] = useState(1),
    [total, setTotal] = useState(0),
    [filter, setFilter] = useState(""),
    [category, setCategory] = useState(""),
    [saved, setSaved] = useState<number[]>([]),
    [compared, setCompared] = useState<number[]>([]);
  useEffect(() => {
    try {
      setSaved(JSON.parse(localStorage.getItem("abromap-saved") || "[]"));
      setCompared(JSON.parse(localStorage.getItem("abromap-compare") || "[]"));
      const p = JSON.parse(
        localStorage.getItem("abromap-profile") || "null",
      ) as Profile | null;
      if (!p || !p.field) {
        setLoading(false);
        return;
      }
      api
        .match(p, page)
        .then((data) => {
          setRows((previous) => page === 1 ? data.results : [...previous, ...data.results]);
          setNoMatchReason(data.no_match_reason);
          setTotal(data.total);
        })
        .catch(() => setError(true))
        .finally(() => setLoading(false));
    } catch {
      setLoading(false);
      setError(true);
    }
  }, [page]);
  const visible = useMemo(
    () =>
      rows.filter(
        (x) =>
          (!filter || x.university.country === filter) &&
          (!category || x.category === category),
      ),
    [rows, filter, category],
  );
  function toggle(
    key: "abromap-saved" | "abromap-compare",
    id: number,
    current: number[],
    setter: (x: number[]) => void,
  ) {
    const next = current.includes(id)
      ? current.filter((x) => x !== id)
      : [...current, id];
    setter(next);
    localStorage.setItem(key, JSON.stringify(next));
  }
  return (
    <div className="page">
      <div className="container">
        <div className="row space-between page-heading">
          <div>
            <h1>{t("title")}</h1>
            <p>{t("subtitle")}</p>
          </div>
          <Link href="/discover" className="button secondary">
            {t("edit")}
          </Link>
        </div>
        {loading ? (
          <div className="result-grid">
            <div className="skeleton" />
            <div className="skeleton" />
          </div>
        ) : error ? (
          <div className="error">
            {common("error")}{" "}
            <button onClick={() => location.reload()}>{common("retry")}</button>
          </div>
        ) : (
          <>
            <div className="filters">
              <span className="row">
                <SlidersHorizontal size={18} />
                {t("filters")}
              </span>
              <select
                className="input"
                style={{ width: 180 }}
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                aria-label={common("country")}
              >
                <option value="">{common("all")}</option>
                {[...new Set(rows.map((x) => x.university.country))].map(
                  (x) => (
                    <option value={x} key={x}>
                      {countryName(x, locale)}
                    </option>
                  ),
                )}
              </select>
              <select
                className="input"
                style={{ width: 230 }}
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                aria-label={t("filters")}
              >
                <option value="">{common("all")}</option>
                {[
                  "strong_match",
                  "good_match",
                  "possible_match",
                  "requirements_not_met",
                  "insufficient_information",
                ].map((x) => (
                  <option key={x} value={x}>
                    {t(x)}
                  </option>
                ))}
              </select>
              <span className="muted small-text">
                {t("showing", { count: visible.length })}
              </span>
            </div>
            {visible.length === 0 ? (
              <div className="empty">
                <AlertCircle size={38} />
                <h3>{t("empty")}</h3>
                <p>
                  {rows.length === 0
                    ? t(noMatchReason || "emptyHelp")
                    : t("filters_empty")}
                </p>
                <div className="row" style={{ justifyContent: "center" }}>
                  {rows.length > 0 ? (
                    <button
                      className="button"
                      onClick={() => {
                        setFilter("");
                        setCategory("");
                      }}
                    >
                      {t("clearFilters")}
                    </button>
                  ) : (
                    <>
                      <Link href="/discover" className="button">
                        {t("edit")}
                      </Link>
                      <Link href="/universities" className="button secondary">
                        {t("browse")}
                      </Link>
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="result-grid">
                {visible.map((x) => (
                  <article className="card result-card" key={x.program.id}>
                    <div className="row space-between">
                      <span
                        className={`tag ${x.category === "requirements_not_met" ? "bad" : x.category === "insufficient_information" ? "warn" : "good"}`}
                      >
                        {t(x.category)}
                      </span>
                      <span className="tag">{t(x.subject_match === "exact" ? "exactSubject" : "relatedSubject")}</span>
                    </div>
                    <div>
                      <h3>{x.program.name}</h3>
                      <p>
                        {x.university.name} · {x.university.city},{" "}
                        {countryName(x.university.country, locale)}
                      </p>
                    </div>
                    <div className="row space-between">
                      <span className="score">
                        {t("score", { score: x.score })}
                      </span>
                      <span className="muted small-text">
                        {x.program.tuition_eur === null
                          ? common("unknown")
                          : `${x.program.tuition_currency || "EUR"} ${x.program.tuition_eur.toLocaleString()}${x.program.tuition_period ? ` / ${x.program.tuition_period}` : ""}`}
                      </span>
                    </div>
                    {x.uncertainty.length > 0 && (
                      <div className="note">
                        <strong>{t("uncertainty")}</strong>
                        <div>
                          {x.uncertainty.map((code) => notes.has(code)
                            ? notes(code as "requirements_unverified") : code.replaceAll("_", " ")).join(" ")}
                        </div>
                      </div>
                    )}
                    <div className="row">
                      <Link
                        href={`/programs/${x.program.id}`}
                        className="button small"
                      >
                        {t("details")} <ArrowRight size={15} />
                      </Link>
                      <button
                        className="button secondary small"
                        onClick={() =>
                          toggle("abromap-saved", x.program.id, saved, setSaved)
                        }
                        aria-pressed={saved.includes(x.program.id)}
                      >
                        <Bookmark
                          size={15}
                          fill={
                            saved.includes(x.program.id) ? "#2563eb" : "none"
                          }
                        />
                        {t("saved")}
                      </button>
                      <button
                        className="button secondary small"
                        onClick={() =>
                          toggle(
                            "abromap-compare",
                            x.program.id,
                            compared,
                            setCompared,
                          )
                        }
                        aria-pressed={compared.includes(x.program.id)}
                      >
                        <GitCompareArrows size={15} />
                        {t("compare")}
                      </button>
                    </div>
                    <p className="small-text muted">{t("requirementConfidence")}: {t(`confidence_${x.requirement_confidence}` as "confidence_verified")}</p>
                  </article>
                ))}
              </div>
            )}
            {rows.length < total && <div className="row" style={{ justifyContent: "center", marginTop: 24 }}>
              <button type="button" className="button secondary" onClick={() => setPage(page + 1)}>{t("loadMore")}</button>
            </div>}
          </>
        )}
      </div>
    </div>
  );
}
