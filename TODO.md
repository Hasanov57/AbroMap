# AbroMap next steps

## Data and trust

- Expand source-checked degree coverage beyond the four master's programs. Prioritize bachelor's and PhD programs across supported countries; never infer a program from a ROR institution record.
- Review the nine same-name ROR candidates and build an admin UI for merge decisions. Add periodic ROR release refreshes, inactive/withdrawn record handling and change monitoring.
- Translate and review the remaining specific-major labels and aliases in Azerbaijani and Russian.
- Support multiple applicant categories per program and academic year, with eligibility and requirements reviewed separately.
- Add source-backed scholarship eligibility, citizenship rules, deadlines and living expenses only where explicit sources exist.

## Accounts and operations

- Add Supabase Auth with email and optional Google OAuth, protected dashboard, and profile deletion.
- Add backend-enforced admin CRUD and review UI. Current admin endpoint only provides a protected summary and review candidates are database records.
- Add rate limits to public matching and AI routes, and production logging/monitoring without personal data.

## Product

- Expand comparison to a side-by-side table and add program search across a larger verified catalog.
- Add sourced application periods, document requirements, and calendar reminders.
- Add structured scholarship matching and persist user data securely after account sign-in.
- Validate the configured AI integration against live keys and add retrieval from verified sources.
- Add end-to-end browser tests and accessibility audit for all three locales.
