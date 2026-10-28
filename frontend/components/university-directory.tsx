"use client";
import { useEffect, useMemo, useState } from "react";
import { Search, ArrowRight } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { University } from "@/lib/types";
export function UniversityDirectory() {
  const t = useTranslations("directory"),
    common = useTranslations("common"),
    country = useTranslations("countryNames");
  const params = useSearchParams();
  const [rows, setRows] = useState<University[]>([]),
    [search, setSearch] = useState(""),
    [filter, setFilter] = useState(params.get("country") || ""),
    [error, setError] = useState(false),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    api
      .universities()
      .then(setRows)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);
  const visible = useMemo(
    () =>
      rows.filter(
        (x) =>
          (!filter || x.country === filter) &&
          x.name.toLowerCase().includes(search.toLowerCase()),
      ),
    [rows, filter, search],
  );
  return (
    <div className="page">
      <div className="container">
        <div className="page-heading">
          <h1>{t("title")}</h1>
          <p>{t("subtitle")}</p>
        </div>
        <div className="filters">
          <div style={{ position: "relative", flex: "1 1 260px" }}>
            <Search
              size={18}
              style={{
                position: "absolute",
                left: 14,
                top: 15,
                color: "#64748b",
              }}
            />
            <input
              className="input"
              style={{ paddingLeft: 42 }}
              placeholder={t("searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            className="input"
            style={{ width: 200 }}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            aria-label={common("country")}
          >
            <option value="">{common("all")}</option>
            {["DE", "IT", "HU", "NL", "GB", "US", "TR", "PL"].map((code) => (
              <option value={code} key={code}>
                {country(
                  code as "DE" | "IT" | "HU" | "NL" | "GB" | "US" | "TR" | "PL",
                )}
              </option>
            ))}
          </select>
        </div>
        {loading ? (
          <div className="result-grid">
            <div className="skeleton" />
            <div className="skeleton" />
          </div>
        ) : error ? (
          <div className="error">{common("error")}</div>
        ) : visible.length === 0 ? (
          <div className="empty">
            <h3>{t("noResults")}</h3>
          </div>
        ) : (
          <div className="result-grid">
            {visible.map((x) => (
              <article className="card" key={x.id}>
                <div className="row space-between">
                  <span className="tag">
                    {country(
                      x.country as
                        "DE" | "IT" | "HU" | "NL" | "GB" | "US" | "TR" | "PL",
                    )}
                  </span>
                  <span className="tag demo">{common("demo")}</span>
                </div>
                <h3>{x.name}</h3>
                <p>{x.city}</p>
                <div className="divider" />
                <p>
                  {x.programs.length} {t("programs")}
                </p>
                <div style={{ marginTop: 20 }}>
                  <Link
                    href={`/universities/${x.slug}`}
                    className="button small"
                  >
                    {t("viewUniversity")}
                    <ArrowRight size={16} />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
