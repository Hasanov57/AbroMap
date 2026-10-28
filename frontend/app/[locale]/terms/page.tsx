import { useTranslations } from "next-intl";
export default function Terms() {
  const t = useTranslations("legal");
  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 800 }}>
        <div className="page-heading">
          <h1>{t("termsTitle")}</h1>
        </div>
        <div className="card">
          <div className="note">{t("review")}</div>
          <p style={{ marginTop: 20 }}>{t("terms")}</p>
        </div>
      </div>
    </div>
  );
}
