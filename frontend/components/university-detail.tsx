"use client";
import { useEffect, useState } from "react";
import { ArrowRight, ExternalLink, MapPin } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import { countryName } from "@/lib/countries";
import type { University } from "@/lib/types";
export function UniversityDetail({ slug }: { slug: string }) {
  const locale = useLocale(), t = useTranslations("detail"), common = useTranslations("common");
  const [item, setItem] = useState<University | null>(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(false);
  useEffect(() => {
    api
      .university(slug)
      .then(setItem)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [slug]);
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
                  {countryName(item.country, locale)}
                </span>
              </div>
              <h1>{item.name}</h1>
              <p className="row">
                <MapPin size={17} />
                {item.city},{" "}
                {countryName(item.country, locale)}
              </p>
            </div>
            <div className="detail-grid">
              <div>
                <section className="card">
                  <h3>{t("about")}</h3>
                  <p>{item.description || t("institutionCatalogInfo")}</p>
                </section>
                <section className="card">
                  <h3>{t("programs")}</h3>
                  {item.programs.length === 0 && <p className="note">{t("catalogOnly")}</p>}
                  <div className="grid">
                    {item.programs.map((p) => (
                      <Link
                        href={`/programs/${p.id}`}
                        key={p.id}
                        className="country-card"
                      >
                        <div>
                          <strong>{p.name}</strong>
                          <small>
                            {p.teaching_language} ·{" "}
                            {p.tuition_eur === null
                              ? common("unknown")
                              : `€${p.tuition_eur.toLocaleString()}`}
                          </small>
                        </div>
                        <ArrowRight size={18} />
                      </Link>
                    ))}
                  </div>
                </section>
              </div>
              <aside className="card">
                <h3>{common("source")}</h3>
                {item.website ? (
                  <a
                    href={item.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="button secondary small"
                  >
                    {t("official")}
                    <ExternalLink size={15} />
                  </a>
                ) : (
                  <p>{common("noSource")}</p>
                )}
                <div className="divider" />
                {item.ror_id && <p className="small-text muted">
                  {t("institutionSource")}: <a href={item.ror_id} target="_blank" rel="noopener noreferrer">ROR</a>
                </p>}
              </aside>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
