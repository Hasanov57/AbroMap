import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Logo } from "./logo";
export function Footer() {
  const t = useTranslations("footer");
  const c = useTranslations("collection");
  return (
    <footer className="footer">
      <div className="container footer-grid">
        <div>
          <Logo />
          <p>{t("tagline")}</p>
        </div>
        <div>
          <strong>{t("explore")}</strong>
          <Link href="/universities">{t("universities")}</Link>
          <Link href="/scholarships">{t("scholarships")}</Link>
          <Link href="/discover">{t("discover")}</Link>
          <Link href="/saved">{c("savedLink")}</Link>
          <Link href="/compare">{c("compareLink")}</Link>
        </div>
        <div>
          <strong>{t("legal")}</strong>
          <Link href="/privacy">{t("privacy")}</Link>
          <Link href="/terms">{t("terms")}</Link>
        </div>
        <div>
          <strong>{t("notice")}</strong>
          <p>{t("disclaimer")}</p>
        </div>
      </div>
      <div className="container footer-bottom">
        © {new Date().getFullYear()} AbroMap
      </div>
    </footer>
  );
}
