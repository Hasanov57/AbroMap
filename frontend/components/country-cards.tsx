"use client";
import { useEffect, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
const codes = ["DE", "IT", "HU", "NL", "GB", "US", "TR", "PL"] as const;
export function CountryCards() {
  const t = useTranslations("countryNames"),
    l = useTranslations("landing");
  const [counts, setCounts] = useState<Record<string, number>>({});
  useEffect(() => {
    api
      .countries()
      .then((rows) =>
        setCounts(
          Object.fromEntries(rows.map((x) => [x.code, x.program_count])),
        ),
      )
      .catch(() => {});
  }, []);
  return (
    <div className="grid four">
      {codes.map((code) => (
        <Link
          key={code}
          className="country-card"
          href={`/universities?country=${code}`}
        >
          <div>
            <strong>{t(code)}</strong>
            <small>
              {counts[code]
                ? `${counts[code]} ${l("programs")}`
                : l("noPrograms")}
            </small>
          </div>
          <ArrowUpRight size={18} color="#2563eb" />
        </Link>
      ))}
    </div>
  );
}
