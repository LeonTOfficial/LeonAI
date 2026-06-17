# Pull Request

Thank you for helping review or improve LEON AI.

LEON AI is **proprietary source-available software**, not a fully open-source project. Please open an Issue and wait for approval before starting larger code contributions, feature work, rewrites, or architectural changes.

## Summary

- What changed?
- Why is this useful?

## Type of change

- [ ] Bug fix
- [ ] Documentation update
- [ ] Test/QA improvement
- [ ] Small approved code improvement
- [ ] Other

## Checklist

- [ ] I opened or referenced an Issue before larger code work.
- [ ] I did not include secrets, API keys, `.env`, local databases, backups, logs, or private prompts.
- [ ] I updated docs if behavior changed.
- [ ] I added or updated tests if behavior changed.
- [ ] I ran the relevant checks:

```bash
python -m unittest discover -s tests -q
python scripts/leon_doctor.py
npm run check:js
npm run test:browser
git diff --check
```

## Notes for the maintainer

Add any review notes, screenshots, or manual test results here.
