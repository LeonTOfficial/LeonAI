# Contributing to LEON AI

LEON AI is proprietary source-available software. The code, design, architecture, and intellectual property are owned by Leon.

This repository is open for feedback, bug reports, documentation suggestions, and approved contributions. It is not an open-source project where code can be freely copied, modified, redistributed, or reused without permission.

## What You Can Do

- Report bugs via GitHub Issues with clear reproduction steps.
- Suggest features via GitHub Issues with a clear use case.
- Ask questions via GitHub Issues or Discussions.
- Review the source code for learning, evaluation, and feedback.
- Provide feedback on usability, documentation, design, project structure, and reliability.

## What Requires Permission

Prior written permission from Leon is required before you:

- Copy, modify, redistribute, rebrand, publish, or self-host the source code.
- Use LEON AI code or architecture in another project or product.
- Create commercial products or services based on LEON AI.
- Submit large code changes or feature pull requests.
- Use the code to train AI or machine-learning models.

For details, see [LICENSE](LICENSE).

## Code Contributions

Code contributions may be considered, but they require approval before work starts.

1. Open an Issue first.
2. Describe the problem, improvement, or feature idea.
3. Explain the user benefit and expected behavior.
4. Wait for explicit approval before submitting code.
5. Include tests and documentation updates when relevant.

Unapproved large feature pull requests may be closed even if the idea is interesting.

## Bug Reports

Good bug reports should include:

- A clear title.
- Platform: macOS, Windows, or Linux.
- Python version.
- Browser.
- Steps to reproduce.
- Expected behavior.
- Actual behavior.
- Relevant safe log excerpts from `data/logs/leon.log`, if available.
- Screenshots if useful and safe to share.

Do not include passwords, API keys, tokens, personal prompts, private data, full logs, databases, or `.env` content in public Issues.

## Feature Suggestions

Helpful feature suggestions include:

- The problem or workflow you want to improve.
- Why the feature would be useful.
- How you expect it to behave.
- Any examples, sketches, or references.
- Whether it affects privacy, security, local data, or generated code execution.

## Security Issues

Do not report security vulnerabilities publicly with exploit details. Follow the process in [SECURITY.md](SECURITY.md).

If a security finding is urgent and no private channel is available, open a minimal public Issue saying only:

```text
Security contact requested.
```

## Before Opening A Pull Request

Run the checks that apply to your change:

```bash
python -m unittest discover -s tests -q
node --check static/js/api.js
node --check static/js/ui.js
node --check static/js/artifacts.js
node --check static/js/chat.js
git diff --check
```

Also confirm that no local runtime files are staged:

- `.env`
- `data/`
- `backup/`
- `venv/`
- databases
- logs
- tokens or credentials

## Code Of Conduct

- Be respectful and constructive.
- Stay focused on the project and the technical issue.
- Give actionable feedback, not personal attacks.
- Do not spam, harass, or pressure maintainers.

## Questions

Open a GitHub Issue with the label `question` or start a GitHub Discussion.
