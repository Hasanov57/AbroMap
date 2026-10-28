import {
  ArrowRight,
  BadgeCheck,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Compass,
  FileCheck2,
  Globe2,
  GraduationCap,
  MapPin,
  Search,
  Sparkles,
  Wallet,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { CountryCards } from "@/components/country-cards";

export default function Home() {
  const h = useTranslations("hero");
  const l = useTranslations("landing");
  const steps = [
    <GraduationCap key="1" />,
    <Search key="2" />,
    <Wallet key="3" />,
    <FileCheck2 key="4" />,
  ];
  const features = [
    <Compass key="1" />,
    <Wallet key="2" />,
    <BrainCircuit key="3" />,
    <FileCheck2 key="4" />,
    <BadgeCheck key="5" />,
  ];
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow">
              <Sparkles size={14} />
              {h("eyebrow")}
            </span>
            <h1>{h("title")}</h1>
            <p>{h("subtitle")}</p>
            <div className="hero-actions">
              <Link href="/discover" className="button">
                {h("primary")} <ArrowRight size={17} />
              </Link>
              <a href="#how" className="button secondary">
                {h("secondary")}
              </a>
            </div>
            <div className="hero-trust">
              <CheckCircle2 size={17} color="#14b8a6" />
              {h("trust")}
            </div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="orbit" />
            <div className="globe">
              <Globe2 size={180} strokeWidth={0.8} />
            </div>
            <div className="floating-card one">
              <span className="mini-icon">
                <GraduationCap />
              </span>
              {h("card1")}
            </div>
            <div className="floating-card two">
              <span className="mini-icon">
                <BookOpen />
              </span>
              {h("card2")}
            </div>
            <div className="floating-card three">
              <span className="mini-icon">
                <MapPin />
              </span>
              {h("card3")}
            </div>
          </div>
        </div>
      </section>
      <section className="section" id="how">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{l("howEyebrow")}</span>
            <h2>{l("howTitle")}</h2>
            <p>{l("howText")}</p>
          </div>
          <div className="grid four">
            {steps.map((icon, i) => (
              <div className="card" key={i}>
                <span className="step-num">0{i + 1}</span>
                <div className="icon-box" style={{ marginTop: 15 }}>
                  {icon}
                </div>
                <h3>{l(`step${i + 1}`)}</h3>
                <p>{l(`step${i + 1}Text`)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="section alt">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{l("featureEyebrow")}</span>
            <h2>{l("featureTitle")}</h2>
            <p>{l("featureText")}</p>
          </div>
          <div className="grid three">
            {features.map((icon, i) => (
              <div className="card" key={i}>
                <div className="icon-box">{icon}</div>
                <h3>{l(`feature${i + 1}`)}</h3>
                <p>{l(`feature${i + 1}Text`)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{l("countriesEyebrow")}</span>
            <h2>{l("countriesTitle")}</h2>
            <p>{l("countriesText")}</p>
          </div>
          <CountryCards />
        </div>
      </section>
      <section className="section alt">
        <div className="container">
          <div className="cta-panel">
            <div>
              <h2>{l("ctaTitle")}</h2>
              <p>{l("ctaText")}</p>
            </div>
            <Link href="/discover" className="button">
              {l("ctaButton")} <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
