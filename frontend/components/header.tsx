"use client";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { Logo } from "./logo";
export function Header() {
  const t = useTranslations("nav");
  const locale = useLocale();
  const router = useRouter();
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const links = [
    { href: "/" as const, label: t("home") },
    { href: "/universities" as const, label: t("universities") },
    { href: "/scholarships" as const, label: t("scholarships") },
    { href: "/#how" as const, label: t("how") },
  ];
  return (
    <header className="header">
      <div className="container nav">
        <Logo />
        <nav
          className={open ? "nav-links open" : "nav-links"}
          aria-label={t("navigation")}
        >
          {links.map((x) => (
            <Link key={x.href} href={x.href} onClick={() => setOpen(false)}>
              {x.label}
            </Link>
          ))}
        </nav>
        <div className="nav-actions">
          <div className="language" aria-label={t("language")}>
            {(["az", "en", "ru"] as const).map((l) => (
              <button
                key={l}
                aria-current={locale === l ? "true" : undefined}
                onClick={() => router.replace(path, { locale: l })}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
          <Link href="/discover" className="button small">
            {t("start")}
          </Link>
        </div>
        <button
          className="menu-button"
          onClick={() => setOpen(!open)}
          aria-label={t("navigation")}
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>
    </header>
  );
}
