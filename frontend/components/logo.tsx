import { Link } from "@/i18n/navigation";
export function Logo() {
  return (
    <Link href="/" className="logo" aria-label="AbroMap">
      <svg
        width="34"
        height="34"
        viewBox="0 0 34 34"
        fill="none"
        aria-hidden="true"
      >
        <rect width="34" height="34" rx="11" fill="#2563EB" />
        <path
          d="M17 5.5c-5.2 0-9 3.9-9 9.1 0 6 9 14 9 14s9-8 9-14c0-5.2-3.8-9.1-9-9.1Z"
          stroke="white"
          strokeWidth="2"
        />
        <path
          d="m11.5 17 5.5-6 5.5 6M17 11v10"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span>
        Abro<span className="logo-accent">Map</span>
      </span>
    </Link>
  );
}
