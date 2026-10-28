"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
const keys = [
  "transcript",
  "diploma",
  "language",
  "motivation",
  "references",
  "requirements",
  "scholarship",
  "apply",
] as const;
export function Roadmap() {
  const t = useTranslations("roadmap");
  const params = useSearchParams();
  const id = params.get("program");
  const storageKey = `abromap-roadmap-${id}`;
  const [done, setDone] = useState<string[]>([]);
  useEffect(() => {
    try {
      setDone(JSON.parse(localStorage.getItem(storageKey) || "[]"));
    } catch {}
  }, [storageKey]);
  function toggle(key: string) {
    const next = done.includes(key)
      ? done.filter((x) => x !== key)
      : [...done, key];
    setDone(next);
    localStorage.setItem(storageKey, JSON.stringify(next));
  }
  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 780 }}>
        <div className="page-heading">
          <h1>{t("title")}</h1>
          <p>{t("subtitle")}</p>
        </div>
        {!id ? (
          <div className="empty">
            <h3>{t("noProgram")}</h3>
            <Link href="/universities" className="button">
              {t("title")}
            </Link>
          </div>
        ) : (
          <div className="card">
            <div className="row space-between">
              <h3>{t("documents")}</h3>
              <span className="tag">
                {t("progress", { done: done.length, total: keys.length })}
              </span>
            </div>
            <div className="progress-track">
              <div style={{ width: `${(done.length / keys.length) * 100}%` }} />
            </div>
            <div className="checklist">
              {keys.map((key) => (
                <label key={key}>
                  <input
                    type="checkbox"
                    checked={done.includes(key)}
                    onChange={() => toggle(key)}
                  />
                  <span>{t(key)}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
