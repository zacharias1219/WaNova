# Security policy

## Supported versions

Security fixes are applied to the **default branch** (`main` / `master`, whichever is primary in this repo). There is no separate LTS line; run the latest commit on the default branch for the most up-to-date fixes.

## Reporting a vulnerability

**Please do not** open a public GitHub issue for undisclosed security vulnerabilities (that can expose users before a fix exists).

Preferred options:

1. **GitHub private reporting** — If enabled for this repository, use **Security → Report a vulnerability** on GitHub and describe the issue there.
2. **Maintainer contact** — If private reporting is unavailable, contact the repository owner through a **private** channel (e.g. email or GitHub profile if listed) with:
   - A clear description of the issue and impact
   - Steps to reproduce (proof-of-concept if safe)
   - Affected components (e.g. webhook, media download, env handling)

We aim to acknowledge reports within a few business days and coordinate disclosure after a fix is available.

## Scope notes

Out of scope for *this* policy (report to the vendor instead):

- Compromise of third-party services (Groq, Meta, Qdrant, etc.) unless caused by insecure use *in this codebase*
- Social engineering or physical access to devices

## Good-faith research

We welcome coordinated disclosure. Please avoid destructive testing (e.g. mass data deletion, DoS against production without permission).
