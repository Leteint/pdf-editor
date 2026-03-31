# Générer l'installeur PDF Editor

## Prérequis

| Outil | Obligatoire | Lien |
|---|---|---|
| Python 3.11+ (64-bit) | Oui | python.org |
| PyInstaller | Oui | `pip install pyinstaller` |
| Inno Setup 6 | Non (installeur seul) | jrsoftware.org/isdl.php |
| Tesseract-OCR | Non (OCR intégré) | github.com/UB-Mannheim/tesseract |
| UPX (compression) | Non | upx.github.io |

## Lancer le build

```bat
cd c:\temp\PDF_Editor
build_installer.bat
```

Étapes automatiques :
1. Installe les dépendances (`requirements.txt`)
2. **PyInstaller** empaquète → `dist\PDFEditor\`
3. **Inno Setup** crée l'installeur

## Résultat

```
dist\PDFEditor\              ← application portable (ZIP-able)
installer\
  PDFEditor-1.4.1-Setup.exe  ← installeur Windows
```

## Options avancées

### Bundler Tesseract dans l'installeur

Par défaut Tesseract n'est **pas** bundlé (l'utilisateur l'installe séparément,
l'app le détecte automatiquement).

Pour l'intégrer (~100 MB de plus) :

```bat
set TESSERACT_DIR=C:\Program Files\Tesseract-OCR
build_installer.bat
```

### Icône personnalisée

Placez un fichier `assets\icon.ico` (256×256 recommandé).
Si absent, commentez la ligne `icon=` dans `build.spec`.

### Signature du binaire (recommandé pour diffusion publique)

```bat
signtool sign /f cert.pfx /p motdepasse /t http://timestamp.digicert.com ^
    dist\PDFEditor\PDFEditor.exe
```

Puis relancer Inno Setup pour que l'installeur embarque le binaire signé.

## Contenu de l'installeur

- Installe dans `%ProgramFiles%\PDF Editor`
- Raccourcis Bureau (optionnel) et Menu Démarrer
- Association de fichier `.pdf` (optionnel, coché par défaut)
- **Association PDF par défaut** (v1.4) : une case à cocher propose de définir
  PDF Editor comme application par défaut pour les fichiers `.pdf`.
  Utilise `HKCU\Software\Classes\.pdf` (pas de droits admin requis) et
  enregistre les Capabilities dans le panneau « Applications par défaut »
  de Windows. Notification immédiate via `SHChangeNotify`.
- Désinstalleur intégré (`Paramètres → Applications`)
- Détecte une version précédente et propose de la désinstaller

## Taille approximative

| Composant | Taille |
|---|---|
| PySide6 runtime | ~120 MB |
| pdfium (rendu PDF) | ~30 MB |
| pikepdf + libs | ~20 MB |
| Application + assets | ~5 MB |
| **Total compressé** | **~80 MB** |

Avec Tesseract bundlé : +80-100 MB.

## Historique des versions

| Version | Date | Changements |
|---|---|---|
| 1.4.1 | 26/03/2026 | Menu contextuel «Combiner dans PDF Editor» (multi-sélection → OrganizeDialog pré-chargé), dialogue Intégration Windows revu (2 sections) |
| 1.4.0 | 25/03/2026 | Navigation page par ascenseur, extraction texte multi-pages, popup résumé extraction, panneau Outils aligné sur le menu, À propos enrichi, association PDF par défaut, annuler/rétablir étendu |
| 1.3.0 | — | Panneau Outils gauche, onglets Langue et Aide, icônes menus, support russe, déplacement Signature → Outils |
| 1.2.0 | — | Formulaires, OCR, tampons, filigrane, métadonnées, en-têtes/pieds de page, compression |
| 1.0.0 | — | Version initiale |
