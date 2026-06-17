# Mithelfen und Feedback geben

LEON AI ist **proprietäre Source-Available-Software**. Das bedeutet: Feedback, Bug Reports, Doku-Hinweise und genehmigte Beiträge sind willkommen. Der Code darf aber nicht frei kopiert, verändert, weiterverbreitet oder kommerziell genutzt werden, ohne vorherige schriftliche Genehmigung von Leon.

## Wie du helfen kannst

| Möglichkeit | Wo? |
| --- | --- |
| Bug melden | [Issues im Hauptrepo](https://github.com/LeonTOfficial/LeonAI/issues) |
| Feature vorschlagen | [Feature Request](https://github.com/LeonTOfficial/LeonAI/issues) |
| Allgemeines Feedback geben | GitHub Issue oder Discussion im Hauptrepo |
| Doku verbessern | Erst Issue öffnen, dann Änderung abstimmen |
| Sicherheitsproblem melden | Siehe [`SECURITY.md`](SECURITY.md) |

## Gutes Feedback enthält

- Was du getestet hast.
- Auf welchem System du getestet hast.
- Was funktioniert hat.
- Was unklar war.
- Was du verbessern würdest.
- Falls ein Fehler passiert ist: kurze Schritte zum Nachstellen.

Bitte keine privaten Daten posten:

- keine Passwörter
- keine API-Schlüssel
- keine Tokens
- keine vollständigen Logs
- keine `.env`
- keine lokalen Datenbanken
- keine privaten Prompts

## Code-Beiträge

Größere Code-Beiträge bitte nicht einfach ungefragt als Pull Request einreichen.

Empfohlener Ablauf:

1. Issue öffnen.
2. Idee oder Problem beschreiben.
3. Nutzen erklären.
4. Auf Rückmeldung warten.
5. Erst danach Code ändern.
6. Tests und Doku anpassen, wenn Verhalten geändert wird.

## Vor einem Pull Request

Im Hauptrepo sollten passende Checks laufen:

```bash
python -m unittest discover -s tests -q
python scripts/leon_doctor.py
npm run check:js
npm run test:browser
git diff --check
```

## Umgangston

- respektvoll
- konkret
- ehrlich
- hilfreich
- technisch nachvollziehbar

Kritik ist willkommen, solange sie hilft, das Projekt besser zu machen.
