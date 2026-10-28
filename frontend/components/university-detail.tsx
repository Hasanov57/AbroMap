"use client";
import { useEffect, useState } from "react";
import { ArrowRight, ExternalLink, MapPin } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { University } from "@/lib/types";
export function UniversityDetail({ slug }: { slug: string }) {
  const t = useTranslations("detail"),
    common = useTranslations("common"),
    country = useTranslations("countryNames");
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
                  {country(
                    item.country as
                      "DE" | "IT" | "HU" | "NL" | "GB" | "US" | "TR" | "PL",
                  )}
                </span>
                <span className="tag demo">{common("demo")}</span>
              </div>
              <h1>{item.name}</h1>
              <p className="row">
                <MapPin size={17} />
                {item.city},{" "}
                {country(
                  item.country as
                    "DE" | "IT" | "HU" | "NL" | "GB" | "US" | "TR" | "PL",
                )}
              </p>
            </div>
            <div className="detail-grid">
              <div>
                <section className="card">
                  <h3>{t("about")}</h3>
                  <p>{item.is_demo ? common("demo") : item.description}</p>
                </section>
                <section className="card">
                  <h3>{t("programs")}</h3>
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
                <p className="small-text muted">{common("demo")}</p>
              </aside>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
