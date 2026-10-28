# AbroMap next steps

## Data and trust

- Replace synthetic institutions and program facts with sourced real records. Review requirements by academic year and preserve historical versions.
- Expand catalog coverage across the listed fields and countries; show sourced availability before students begin onboarding.
- Build a robots-aware source ingestion pipeline with change detection and a human verification queue.
- Add source URLs, verification dates, and official language versions for every published requirement.
- Model scholarship eligibility, citizenship, deadlines, and living expenses only when supported by sources.

## Accounts and operations

- Add Supabase Auth with email and optional Google OAuth, protected dashboard, and profile deletion.
- Add backend-enforced admin CRUD and review UI. Current admin endpoint only provides a protected summary.
- Add rate limits to public matching and AI routes, and production logging/monitoring without personal data.

## Product

- Expand comparison to a side-by-side table and add program search beyond the initial demo catalog.
- Add sourced application periods, document requirements, and calendar reminders.
- Add structured scholarship matching and persist user data securely after account sign-in.
- Validate the configured AI integration against live keys and add retrieval from verified sources.
- Add end-to-end browser tests and accessibility audit for all three locales.
