# Documentation utilisateur multilingue — PDF Editor

Cette page centralise les manuels utilisateur et les captures d'écran de PDF Editor dans toutes les langues supportées.

## Langues disponibles

| Langue | Code | Manuel utilisateur | Captures d'écran |
|--------|------|--------------------|------------------|
| Français | `fr` | [Manuel_utilisateur_fr.md](Manuel_utilisateur_fr.md) | [website/screenshots/fr](../website/screenshots/fr/) |
| English | `en` | [User_Manual_en.md](User_Manual_en.md) | [website/screenshots/en](../website/screenshots/en/) |
| Deutsch | `de` | [User_Manual_de.md](User_Manual_de.md) | [website/screenshots/de](../website/screenshots/de/) |
| Español | `es` | [User_Manual_es.md](User_Manual_es.md) | [website/screenshots/es](../website/screenshots/es/) |
| Italiano | `it` | [User_Manual_it.md](User_Manual_it.md) | [website/screenshots/it](../website/screenshots/it/) |
| Português | `pt` | [User_Manual_pt.md](User_Manual_pt.md) | [website/screenshots/pt](../website/screenshots/pt/) |
| Русский | `ru` | [User_Manual_ru.md](User_Manual_ru.md) | [website/screenshots/ru](../website/screenshots/ru/) |

## Génération des captures d'écran

Les captures d'écran sont générées automatiquement avec le script :

```bash
python generate_screenshots.py demo_PDF_Editor.pdf form.pdf
```

Elles sont stockées dans `website/screenshots/{lang}/`.

## Mise à jour

Lors d'une nouvelle version, pensez à :
1. Mettre à jour `Manuel_utilisateur_fr.md` (source de vérité).
2. Synchroniser les traductions (`User_Manual_*.md`).
3. Relancer `generate_screenshots.py` avec un PDF de démo représentatif.

---

*Dernière mise à jour : 01/07/2026 — PDF Editor v1.5.8*
