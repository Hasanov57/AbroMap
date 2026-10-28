"use client";
import { useEffect, useState } from "react";
import { Search, ArrowRight } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import { countryName } from "@/lib/countries";
import type { Country, UniversityPage } from "@/lib/types";

export function UniversityDirectory() {
  const locale = useLocale(), t = useTranslations("directory"), common = useTranslations("common");
  const params = useSearchParams();
  const [data, setData] = useState<UniversityPage | null>(null);
  const [countries, setCountries] = useState<Country[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState(params.get("country") || "");
  const [page, setPage] = useState(1);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  useEffect(() => { api.countries(locale).then(setCountries).catch(() => {}); }, [locale]);
  useEffect(() => {
    let live = true;
    const timer = window.setTimeout(() => {
      setLoading(true);
      setError(false);
      api.universitiesPage({ page, page_size: 20, search, country: filter })
        .then((rows) => { if (live) setData(rows); })
        .catch(() => { if (live) setError(true); })
        .finally(() => { if (live) setLoading(false); });
    }, 250);
    return () => { live = false; window.clearTimeout(timer); };
  }, [search, filter, page]);
  return (
    <div className="page"><div className="container">
      <div className="page-heading"><h1>{t("title")}</h1><p>{t("subtitle")}</p></div>
      <div className="filters">
        <div style={{ position: "relative", flex: "1 1 260px" }}>
          <Search size={18} style={{ position: "absolute", left: 14, top: 15, color: "#64748b" }} />
          <input className="input" style={{ paddingLeft: 42 }} placeholder={t("searchPlaceholder")}
            value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} />
        </div>
        <select className="input" style={{ width: 220 }} value={filter}
          onChange={(event) => { setFilter(event.target.value); setPage(1); }} aria-label={common("country")}>
          <option value="">{common("all")}</option>
          {countries.filter((row) => row.university_count > 0).map((row) =>
            <option value={row.iso_code} key={row.iso_code}>{row.name}</option>)}
        </select>
      </div>
      {loading ? <div className="result-grid"><div className="skeleton" /><div className="skeleton" /></div>
      : error ? <div className="error">{common("error")}</div>
      : !data?.items.length ? <div className="empty"><h3>{t("noResults")}</h3></div>
      : <>
        <div className="result-grid">{data.items.map((row) =>
          <article className="card" key={row.id}>
            <span className="tag">{countryName(row.country, locale)}</span>
            <h3>{row.name}</h3><p>{row.city}</p>
            <div className="divider" />
            <p>{row.program_count ? `${row.program_count} ${t("programs")}` : t("catalogOnly")}</p>
            <div style={{ marginTop: 20 }}><Link href={`/universities/${row.slug}`} className="button small">
              {t("viewUniversity")}<ArrowRight size={16} />
            </Link></div>
          </article>)}</div>
        <div className="row" style={{ justifyContent: "center", marginTop: 24 }}>
          <button type="button" className="button secondary small" disabled={page <= 1}
            onClick={() => setPage(page - 1)}>{common("back")}</button>
          <span className="muted small-text">{page} / {data.total_pages}</span>
          <button type="button" className="button secondary small" disabled={page >= data.total_pages}
            onClick={() => setPage(page + 1)}>{t("nextPage")}</button>
        </div>
      </>}
    </div></div>
  );
}
