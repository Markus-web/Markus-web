# Maintaining the profile

This repository is intentionally small. Contributions should improve the accuracy, clarity or safe maintenance of the public GitHub profile.

## Update workflow

1. Confirm each new claim and link from a public source or directly with the maintainer.
2. Edit the Finnish and English sections together.
3. Check the staged diff for private operational details and personal data that was not already intentionally public.
4. Run the tests and validation commands documented in `AGENTS.md`.
5. Keep one focused commit and push it to `main`.
6. Verify the rendered profile and the GitHub Actions result.

## Public-information boundary

Safe content includes public websites, public repositories, deliberately published contact details and broad professional skills.

Do not publish credentials, tokens, cookies, private keys, customer data, non-public email addresses, local filesystem paths, private network addresses, internal domains, server names, backup locations or security-control details. When uncertain, omit the detail and ask the maintainer.

The validator catches common high-confidence mistakes, but it does not replace a human review of the diff.

## Style

- Use concise, natural prose and descriptive links.
- Keep headings in a logical order and avoid heading-level jumps.
- Do not use images for text or add decoration that competes with the content.
- Prefer stable project pages over campaign or tracking URLs.
