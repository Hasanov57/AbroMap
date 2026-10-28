"use client";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { Program } from "@/lib/types";
export function Collection({ mode }: { mode: "saved" | "compare" }) {
  const t = useTranslations("collection"),
    common = useTranslations("common");
  const key = mode === "saved" ? "abromap-saved" : "abromap-compare";
  const [ids, setIds] = useState<number[]>([]),
    [programs, setPrograms] = useState<Program[]>([]),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    let chosen: number[] = [];
    try {
      chosen = JSON.parse(localStorage.getItem(key) || "[]");
    } catch {}
    setIds(chosen);
    api
      .programs()
      .then((rows) => setPrograms(rows.filter((p) => chosen.includes(p.id))))
      .finally(() => setLoading(false));
  }, [key]);
  function remove(id: number) {
    const next = ids.filter((x) => x !== id);
    setIds(next);
    setPrograms((rows) => rows.filter((x) => x.id !== id));
    localStorage.setItem(key, JSON.stringify(next));
  }
  return (
    <div className="page">
      <div className="container">
        <div className="page-heading">
          <h1>{mode === "saved" ? t("savedTitle") : t("compareTitle")}</h1>
        </div>
        {loading ? (
          <div className="skeleton" />
        ) : programs.length === 0 ? (
          <div className="empty">
            <h3>{mode === "saved" ? t("emptySaved") : t("emptyCompare")}</h3>
            <Link href="/universities" className="button">
              {t("explore")}
            </Link>
          </div>
        ) : (
          <div className="result-grid">
            {programs.map((p) => (
              <article className="card" key={p.id}>
                <span className="tag demo">{common("demo")}</span>
                <h3>{p.name}</h3>
                <div className="detail-list">
                  <div>
                    <small>{common("degree")}</small>
                    <strong>{p.degree}</strong>
                  </div>
                  <div>
                    <small>{common("language")}</small>
                    <strong>{p.teaching_language}</strong>
                  </div>
                  <div>
                    <small>{common("tuition")}</small>
                    <strong>
                      {p.tuition_eur === null
                        ? common("unknown")
                        : `€${p.tuition_eur.toLocaleString()}`}
                    </strong>
                  </div>
                  <div>
                    <small>{common("year")}</small>
                    <strong>
                      {p.requirements[0]?.academic_year || common("unknown")}
                    </strong>
                  </div>
                </div>
                <div className="row" style={{ marginTop: 20 }}>
                  <Link href={`/programs/${p.id}`} className="button small">
                    {common("view")}
                  </Link>
                  <button
                    className="button secondary small"
                    onClick={() => remove(p.id)}
                  >
                    {t("remove")}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
