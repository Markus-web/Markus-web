# Repository guide

This public repository renders the GitHub profile for `Markus-web`. Keep it small, factual and safe to publish.

## Source of truth

- `README.md` is the profile shown at <https://github.com/Markus-web>.
- `CONTRIBUTING.md` defines the maintenance and publication checklist.
- `scripts/check_public_profile.py` is the reusable validation entry point.
- `.github/workflows/profile-check.yml` runs the same validation in GitHub Actions.
- `.github/dependabot.yml` keeps pinned GitHub Actions revisions current.

## Editing rules

- Keep Finnish first and the English version inside the existing disclosure block.
- Update both language sections together and preserve equivalent meaning.
- Link only to public, intentionally published work.
- Never add credentials, private URLs, internal hostnames, IP addresses, local paths, customer secrets or infrastructure topology.
- Prefer plain Markdown. Do not add generated statistics, visitor counters, skill-logo walls or decorative animation.
- Do not describe a project, customer relationship or skill unless it can be verified from a public source or by the maintainer.
- Keep scripts dependency-free when the Python standard library is sufficient.
- Facts and wording follow markussilvo.fi and the job-search voice rules (megarepo `Mautic/voice.md`): "IT-osaaja", "web-palvelimet", "vakituista työpaikkaa, mieluiten kokopäiväistä", wishes instead of terms for places. The validator enforces three of them: no em or en dashes (use a colon, comma or period), no speed claims ("nopeasti", "fast"), and no link to the semi-hidden job landing `markussilvo.fi/sivu/tyo` or `/sivu/palaute`.
- When the CV facts change (role, experience, projects), update markussilvo.fi (`markussilvo-website/emdash/seed/seed.json`) and this README in the same pass.

## Verification

Run before every commit:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_public_profile.py --history
python3 scripts/check_public_profile.py --links
```

The first two commands must pass. A link failure must be investigated; do not silently allow a missing page.

## Deployment

There is no separate site build. A push to the default branch deploys the README to the GitHub profile. After pushing, verify the public profile and the `Profile checks` workflow.
