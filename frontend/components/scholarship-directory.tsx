"use client";
import { useEffect, useState } from "react";
import { ExternalLink, Wallet } from "lucide-react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";
import type { Scholarship } from "@/lib/types";
export function ScholarshipDirectory() {
  const t = useTranslations("scholarships"),
    common = useTranslations("common");
  const [rows, setRows] = useState<Scholarship[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(false);
  useEffect(() => {
    api
      .scholarships()
      .then(setRows)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);
  return (
    <div className="page">
      <div className="container">
        <div className="page-heading">
          <h1>{t("title")}</h1>
          <p>{t("subtitle")}</p>
        </div>
        <div className="note" style={{ marginBottom: 24 }}>
          {t("warning")}
        </div>
        {loading ? (
          <div className="skeleton" />
        ) : error ? (
          <div className="error">{common("error")}</div>
        ) : rows.length === 0 ? (
          <div className="empty">
            <Wallet size={38} />
            <h3>{t("empty")}</h3>
          </div>
        ) : (
          <div className="result-grid">
            {rows.map((x) => (
              <article className="card" key={x.id}>
                <div className="row space-between">
                  <span className="tag">
                    {t("coverage")}:{" "}
                    {x.coverage === "full" ? t("full") : t("partial")}
                  </span>
                  <span className="tag demo">{common("demo")}</span>
                </div>
                <h3>{x.name}</h3>
                <p>{x.is_demo ? common("demo") : x.description}</p>
                <div className="divider" />
                {x.source_url ? (
                  <a
                    href={x.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="button secondary small"
                  >
                    {common("source")} <ExternalLink size={15} />
                  </a>
                ) : (
                  <span className="muted small-text">{common("noSource")}</span>
                )}
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
