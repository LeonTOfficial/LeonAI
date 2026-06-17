# LeonAI-DE Repository Plan

The main repository is English-first. German documentation should live in a separate repository named:

```text
LeonTOfficial/LeonAI-DE
```

## Goal

`LeonAI-DE` should be a German documentation mirror for users who prefer German explanations, setup help, and project background.

## Suggested Files

```text
LeonAI-DE/
├── README.md
├── SECURITY.md
├── TESTING.md
├── STRUKTUR.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Rules For The German Repository

- Link back to the English main repository: `https://github.com/LeonTOfficial/LeonAI`.
- Keep German docs in German only.
- Keep the main repository English only.
- Do not duplicate secrets, local databases, logs, backups, or runtime files.
- Keep license wording consistent with the main repository.

## First Setup Steps

```bash
git clone https://github.com/LeonTOfficial/LeonAI-DE.git
cd LeonAI-DE
```

Then add the German documentation files and link clearly back to the main repository.
