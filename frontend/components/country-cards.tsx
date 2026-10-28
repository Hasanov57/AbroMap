"use client";
import { useEffect, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { Country } from "@/lib/types";
export function CountryCards() {
  const locale = useLocale(), l = useTranslations("landing");
  const [countries, setCountries] = useState<Country[]>([]);
  useEffect(() => {
    api.countries(locale).then((rows) => setCountries(rows.filter((row) => row.university_count > 0)
      .sort((a, b) => b.university_count - a.university_count).slice(0, 8))).catch(() => {});
  }, [locale]);
  return (
    <div className="grid four">
      {countries.map((row) => (
        <Link
          key={row.iso_code}
          className="country-card"
          href={`/universities?country=${row.iso_code}`}
        >
          <div>
            <strong>{row.name}</strong>
            <small>
              {row.verified_program_count
                ? `${row.verified_program_count} ${l("programs")}`
                : l("noPrograms")}
            </small>
          </div>
          <ArrowUpRight size={18} color="#2563eb" />
        </Link>
      ))}
    </div>
  );
}
