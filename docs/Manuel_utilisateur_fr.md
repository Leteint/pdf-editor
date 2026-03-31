# Manuel utilisateur — PDF Editor

**Version 1.4.1** · 26/03/2026

---

## Table des matières

1. [Présentation](#presentation)
2. [Installation et premier lancement](#installation)
3. [Interface générale](#interface)
4. [Ouvrir et fermer un document](#ouvrir)
5. [Navigation dans le document](#navigation)
6. [Zoom et affichage](#zoom)
7. [Modifier le texte existant](#modifier-texte)
8. [Insérer du texte](#inserer-texte)
9. [Annotations](#annotations)
10. [Insérer une image](#inserer-image)
11. [Formulaires PDF](#formulaires)
12. [Reconnaissance de caractères (OCR)](#ocr)
13. [Gestion des pages — Réorganiser / Fusionner / Fractionner](#pages)
14. [En-têtes et pieds de page](#entetes)
15. [Filigrane](#filigrane)
16. [Tampon texte](#tampon-texte)
17. [Tampon image — logo et signature](#tampon-image)
18. [Intégration Windows — clic droit](#windows)
19. [Métadonnées du document](#metadata)
20. [Compression PDF](#compression)
21. [Protection par mot de passe](#protection)
22. [Signature numérique](#signature)
23. [Recherche de texte](#recherche)
24. [Extraction de contenu](#extraction)
25. [Enregistrer le document](#enregistrer)
26. [Annuler / Rétablir](#annuler)
27. [Thèmes et langue](#langue)
28. [Raccourcis clavier](#raccourcis)

---

> **Nouveautés v1.4.1** : menu contextuel **Combiner dans PDF Editor** (sélection multiple de fichiers → dialogue de réorganisation pré-chargé) · dialogue *Intégration Windows* revu avec deux sections activables séparément.
>
> **Nouveautés v1.4.0** : navigation page suivante/précédente via l'ascenseur et la molette · extraction de texte avec choix de l'intervalle de pages · popup de résumé après extraction · panneau *Outils* aligné sur le menu Outils · *À propos* enrichi.
>
> **v1.3.0** : panneau latéral étendu (onglets *Langue* et *Aide*) · menu *Signature* fusionné dans *Outils* · icônes dans tous les menus · toutes les opérations PDF journalisées (Ctrl+Z).

---

<a name="presentation"></a>
## 1. Présentation

**PDF Editor** est un éditeur PDF open source gratuit qui permet de :

- Lire et naviguer dans n'importe quel fichier PDF
- Modifier le texte existant directement dans le document
- Insérer du texte, des images et des annotations
- Créer et remplir des formulaires PDF
- Appliquer une reconnaissance de caractères (OCR) sur les pages numérisées
- Réorganiser, fusionner et fractionner des documents
- Assembler un nouveau PDF à partir d'images (JPG, PNG, TIFF…)
- Ajouter des en-têtes, pieds de page, filigranes et tampons
- Éditer les métadonnées et compresser le fichier
- Protéger un document par mot de passe
- Signer numériquement avec un certificat `.pfx`

---

<a name="installation"></a>
## 2. Installation et premier lancement

### Application portable

L'application ne nécessite pas d'installation. Double-cliquez sur `PDFEditor.exe` pour la lancer directement.

### Installation via l'installeur

Si vous disposez du fichier `PDFEditor-Setup.exe`, lancez-le et suivez l'assistant.
Une étape propose l'installation automatique de **Tesseract OCR** (nécessaire pour la reconnaissance de caractères).

L'installeur propose également de **définir PDF Editor comme application par défaut** pour l'ouverture des fichiers PDF (option cochée par défaut).

### Premier lancement — Tesseract OCR

Au premier démarrage, si Tesseract n'est pas détecté sur votre poste, une fenêtre s'affiche et propose de le télécharger et l'installer automatiquement (~50 MB).

- **Langue OCR** : sélectionnez la langue principale de vos documents (le système détecte automatiquement la langue de Windows).
- **L'anglais** est toujours inclus comme langue de secours.
- Vous pouvez décliner l'installation ; la fonction OCR sera simplement indisponible jusqu'à ce que Tesseract soit installé manuellement.

---

<a name="interface"></a>
## 3. Interface générale

```
┌─────────────────────────────────────────────────────────────────┐
│  Menu  (Fichier · Édition · Affichage · Langue · Outils · Aide) │
├─────────────────────────────────────────────────────────────────┤
│  Barre principale  (◀ Préc. | N° page / total | Suiv. ▶ | Zoom) │
├─────────────────────────────────────────────────────────────────┤
│  Barre pages  (Réorganiser/Fusionner · Fractionner · Suppr. …)  │
├─────────────────────────────────────────────────────────────────┤
│  Barre annotations  (Sélection · Texte · Surligner · …)         │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                          │
│  Panneau latéral     │         Visionneuse PDF                  │
│  [Pages][Outils]     │         (page courante)                  │
│  [Langue][Aide]      │                                          │
│                      │                                          │
└──────────────────────┴──────────────────────────────────────────┘
│  Barre de statut                                                 │
└─────────────────────────────────────────────────────────────────┘
```

- **Panneau latéral gauche** : quatre onglets — *Pages*, *Outils*, *Langue*, *Aide*. Masquable avec `F4`.
- **Visionneuse** : affiche la page courante ; toutes les interactions (clic, double-clic, glisser) s'y effectuent.
- **Barre de statut** : messages contextuels, numéro de page, indication de modification non enregistrée (`*`).

### Onglets du panneau latéral

| Onglet | Contenu |
|--------|---------|
| **Pages** | Vignettes de navigation — cliquez pour aller à une page |
| **Outils** | Section *Outils* (développée, même ordre que le menu) · section *Annotations* · section *Raccourcis* |
| **Langue** | Sélection de la langue de l'interface (redémarrage requis) |
| **Aide** | Raccourcis clavier · bouton Manuel utilisateur · bouton Intégration Windows |

### Menus de la barre supérieure

| Menu | Contenu principal |
|------|------------------|
| **Fichier** | Ouvrir, Enregistrer, Imprimer, Quitter |
| **Édition** | Annuler, Rétablir, Rechercher |
| **Affichage** | Zoom, Panneau, Thème sombre/clair |
| **Langue** | Choix de la langue de l'interface |
| **Outils** | Toutes les opérations PDF (insertion, organisation, tampons, signature…) |
| **Aide** | Manuel, À propos, Intégration Windows |

---

<a name="ouvrir"></a>
## 4. Ouvrir et fermer un document

| Action | Méthode |
|--------|---------|
| Ouvrir un PDF | *Fichier → 📂 Ouvrir…* ou `Ctrl+O` |
| Ouvrir depuis l'explorateur | Glisser-déposer le fichier sur la fenêtre |
| Ouvrir en ligne de commande | `PDFEditor.exe mon_document.pdf` |
| Fermer le document | *Fichier → ✖ Fermer* ou `Ctrl+W` |

Si le document a des modifications non enregistrées, une confirmation est demandée avant fermeture.

### Documents protégés par mot de passe

Lors de l'ouverture d'un fichier chiffré, une boîte de dialogue demande le mot de passe utilisateur. Pour accéder aux options de modification avancées, le **mot de passe propriétaire** peut être requis.

---

<a name="navigation"></a>
## 5. Navigation dans le document

| Action | Méthode |
|--------|---------|
| Page suivante | Clic sur **Suiv. ▶** ou touche `→` |
| Page précédente | Clic sur **◀ Préc.** ou touche `←` |
| Aller à une page précise | Saisir le numéro dans le champ et appuyer sur `Entrée` |
| Faire défiler dans la page | Molette de la souris ou ascenseur droit |
| Page suivante (molette) | Molette vers le bas en **bas de page** |
| Page précédente (molette) | Molette vers le haut en **haut de page** |
| Page suivante (ascenseur) | Faire glisser l'ascenseur jusqu'en bas |
| Cliquer sur une vignette | Panneau latéral gauche — onglet *Pages* |

---

<a name="zoom"></a>
## 6. Zoom et affichage

| Action | Méthode |
|--------|---------|
| Zoom avant | `Ctrl+=` ou bouton **+** |
| Zoom arrière | `Ctrl+-` ou bouton **−** |
| Ajuster à la page | `Ctrl+0` |
| Ajuster à la largeur | `Ctrl+1` |
| Zoom personnalisé | Saisir un pourcentage dans la liste déroulante |
| Zoom avec la souris | `Ctrl + molette` |

---

<a name="modifier-texte"></a>
## 7. Modifier le texte existant

PDF Editor permet de modifier le texte directement dans le flux du document.

### Étapes

1. Dans la barre d'annotations, sélectionnez l'outil **Modifier texte** (`T`).
2. **Double-cliquez** sur le mot ou le bloc de texte à modifier.
3. Une fenêtre contextuelle s'affiche avec le texte et les options de mise en forme :
   - Police, taille, **Gras**, *Italique*, couleur, espacement des lettres
   - Couleur de fond (transparent par défaut)
4. Modifiez le texte, ajustez la mise en forme, puis cliquez sur **Confirmer** (`Ctrl+Entrée`).

> **Conseil** : l'outil tente d'abord une modification **en place** dans le flux PDF. Si cela n'est pas possible (police inconnue, texte image), il bascule sur une annotation de remplacement.

### Annulation

`Ctrl+Z` pour annuler · `Ctrl+Y` pour rétablir (voir [§26 Annuler / Rétablir](#annuler)).

---

<a name="inserer-texte"></a>
## 8. Insérer du texte

Pour ajouter un nouveau bloc de texte sur une zone vide :

1. Sélectionnez l'outil **Modifier texte** (`T`).
2. **Double-cliquez** sur une zone vide de la page.
3. La fenêtre contextuelle s'ouvre avec un éditeur vide.
4. Saisissez votre texte, choisissez la mise en forme, puis confirmez.

Le texte est inséré comme **annotation FreeText** permanente dans le PDF.

---

<a name="annotations"></a>
## 9. Annotations

La barre d'annotations propose plusieurs outils :

| Outil | Raccourci | Usage |
|-------|-----------|-------|
| Sélection | `S` | Sélectionner et déplacer les annotations existantes |
| Modifier texte | `T` | Éditer le texte du document (voir §7 et §8) |
| Surligner | `H` | Surligner un mot ou une sélection en jaune |
| Commentaire | `C` | Ajouter une note (bulle) sur la page |
| Image | `I` | Insérer une image (voir §10) |
| Effacer | `E` | Supprimer une annotation en cliquant dessus |

Les mêmes outils sont accessibles depuis l'onglet **Outils** du panneau latéral gauche, section *Annotations* (réduite par défaut — cliquez pour dérouler).

### Épaisseur du trait

Dans le panneau *Outils → Annotations*, le champ **Épaisseur** règle l'épaisseur du trait des annotations de dessin (0,5 à 10 pt).

### Redimensionner / déplacer une annotation

En mode **Sélection** (`S`) :
- **Cliquer** sur une annotation pour la sélectionner (poignées visibles).
- **Glisser** pour déplacer · **Glisser une poignée** pour redimensionner.
- Touche `Suppr` pour supprimer l'annotation sélectionnée.

---

<a name="inserer-image"></a>
## 10. Insérer une image

**Méthode 1 — Menu**
1. *Outils → 🖼 Insérer une image…*
2. Choisissez le fichier image (PNG, JPEG, BMP, WebP…).
3. Dessinez la zone de destination sur la page.

**Méthode 2 — Barre d'outils**
1. Cliquez sur **🖼 Insérer image** dans la barre *Pages & Formulaire*.
2. Même procédé.

**Méthode 3 — Panneau Outils**
1. Onglet **Outils** du panneau latéral → *🖼 Insérer une image…*

L'image est intégrée de manière permanente dans le PDF.

---

<a name="formulaires"></a>
## 11. Formulaires PDF

### Activer le mode Design

Cliquez sur **✏ Mode Design** dans la barre *Pages & Formulaire*.
En mode Design, cliquer-glisser sur la page crée un nouveau champ.

### Types de champs disponibles

| Type | Description |
|------|-------------|
| Texte | Champ de saisie libre |
| Case à cocher | Oui / Non |
| Liste déroulante | Choix parmi des options prédéfinies |
| Boutons radio | Sélection exclusive dans un groupe |
| Étiquette | Texte statique non modifiable |

### Remplir un formulaire

En mode normal (Design désactivé), cliquez sur un champ pour le remplir.
Le panneau latéral liste tous les champs avec leurs valeurs.

### Déplacer un champ

*Outils → ↔ Déplacer un bloc de texte* (`M`) puis glissez le champ.

---

<a name="ocr"></a>
## 12. Reconnaissance de caractères (OCR)

**Prérequis** : Tesseract OCR installé (voir [§2](#installation)).

### Lancer l'OCR

1. *Outils → 🔤 Reconnaissance de caractères (OCR)…*
2. Le panneau OCR s'ouvre à droite.
3. Sélectionnez la **langue** du document.
4. Cliquez sur **Lancer l'OCR**.

### Résultat

- Le texte reconnu s'affiche en superposition avec des blocs colorés.
- Ajustez la taille/position de chaque bloc par glisser-déposer.
- Cliquez sur **Incruster dans le PDF** pour rendre le texte permanent.

> Les blocs OCR incrustés sont invisibles à l'écran mais indexés par les lecteurs PDF (`Ctrl+F`, copier-coller…).

---

<a name="pages"></a>
## 13. Gestion des pages — Réorganiser / Fusionner / Fractionner

### Réorganiser et fusionner les pages

*Outils → ⊕ Réorganiser/Fusionner les pages…* (ou bouton **⊕ Réorganiser/Fusionner** dans la barre)

Cet outil polyvalent fonctionne **avec ou sans document ouvert** :

| Situation | Résultat |
|-----------|----------|
| PDF ouvert | Réorganise les pages du document courant |
| Aucun PDF ouvert | Crée un nouveau PDF à partir de zéro |

#### Interface de l'organiseur

- Les pages s'affichent sous forme de **vignettes** réordonnables par glisser-déposer.
- Sélectionnez une ou plusieurs vignettes, puis utilisez les boutons :

| Bouton | Action |
|--------|--------|
| ▲ Monter / ▼ Descendre | Déplacer la sélection |
| ↺ -90° / ↻ +90° / ↕ 180° | Faire pivoter les pages sélectionnées |
| 🗑 Supprimer | Retirer les pages sélectionnées |
| ➕ Ajouter un document… | Insérer des pages depuis un autre document |

#### Ajouter un document

Le bouton **➕ Ajouter un document…** accepte :
- **PDF** — toutes les pages sont ajoutées
- **Images** : JPG, JPEG, PNG, BMP, TIFF (y compris multi-pages), WebP — chaque image devient une page

> **Astuce** : pour **fusionner** plusieurs PDFs, ouvrez l'organiseur sans document ouvert, ajoutez vos fichiers via "Ajouter un document", ordonnez-les, puis cliquez **Appliquer** — un "Enregistrer sous" vous demandera le nom du nouveau PDF.

> Cette opération est **annulable** via `Ctrl+Z`.

### Supprimer la page courante

*Outils → 🗑 Supprimer la page courante* ou `Ctrl+Suppr`.

> Cette opération est **annulable** via `Ctrl+Z`.

### Rotation rapide de la page courante

| Action | Méthode |
|--------|---------|
| Tourner +90° | *Outils → ↻ Tourner la page (+90°)* ou `R` |
| Tourner -90° | *Outils → ↺ Tourner la page (-90°)* ou `Maj+R` |

### Fractionner ce PDF

1. *Outils → ✂ Fractionner ce PDF…*
2. Indiquez le nombre de **pages par fichier** (ex. `1` = un fichier par page, `5` = groupes de 5 pages).
3. Un aperçu indique le nombre de fichiers qui seront créés.
4. Choisissez le dossier de destination et confirmez.

---

<a name="entetes"></a>
## 14. En-têtes et pieds de page

*Outils → ☰ En-têtes et pieds de page…*

Ajoutez du texte automatique en haut et/ou en bas de chaque page.

### Zones de texte

Chaque zone (En-tête et Pied de page) comporte trois colonnes : **Gauche · Centre · Droite**.

### Tokens dynamiques

Insérez des variables qui seront remplacées automatiquement à l'application :

| Token | Valeur insérée |
|-------|---------------|
| `{page}` | Numéro de la page courante |
| `{total}` | Nombre total de pages |
| `{date}` | Date du jour (jj/mm/aaaa) |

Des boutons de raccourci sous chaque champ permettent d'insérer ces tokens en un clic.

### Options communes

| Option | Description |
|--------|-------------|
| Taille de police | De 6 à 36 pt |
| Couleur | Noir, Gris, Rouge, Bleu |
| Marge depuis le bord | Distance en mm depuis le bord de la page |
| Ne pas appliquer sur la 1ère page | Utile pour les pages de garde |

### Modifier ou supprimer

Rouvrez *Outils → ☰ En-têtes et pieds de page…* : les derniers paramètres utilisés sont rechargés.
- **Modifier** : changez les textes et recliquez **Appliquer** — les anciens en-têtes sont remplacés.
- **Supprimer** : videz tous les champs et cliquez **Appliquer** — les en-têtes/pieds sont effacés.

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="filigrane"></a>
## 15. Filigrane

*Outils → ◈ Filigrane…*

Appose un texte en diagonale sur toutes les pages du document.

| Option | Description |
|--------|-------------|
| Texte | Libellé du filigrane (ex. `CONFIDENTIEL`) |
| Taille | De 10 à 150 pt |
| Couleur | Gris, Rouge, Bleu, Vert, Noir |
| Opacité | De 5 % (très transparent) à 100 % (opaque) |

> Le filigrane est intégré dans le contenu PDF — il apparaît à l'impression.

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="tampon-texte"></a>
## 16. Tampon texte

*Outils → 🖊 Tampon texte…*

Appose un tampon style "cachet" (texte encadré) sur une ou plusieurs pages.

### Tampons disponibles

| Tampon | Couleur |
|--------|---------|
| APPROUVÉ | Vert |
| REJETÉ | Rouge |
| À SIGNER | Bleu |
| CONFIDENTIEL | Rouge |
| BROUILLON | Gris |
| URGENT | Orange |
| COPIE | Gris |
| À RÉVISER | Orange |
| Personnalisé… | Au choix (texte libre) |

### Options

| Option | Description |
|--------|-------------|
| Position | Haut-droit, Haut-gauche, Bas-droit, Bas-gauche, Centre |
| Pages | Toutes les pages, Première page, Dernière page |
| Rotation | Horizontal (0°) ou Diagonal (−45°) |
| Opacité | De 10 % à 100 % |

Un **aperçu en temps réel** s'affiche à droite du dialogue.

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="tampon-image"></a>
## 17. Tampon image — logo et signature

*Outils → 🖼 Tampon image…*

Appose une image (logo d'entreprise, signature scannée, cachet…) sur une ou plusieurs pages. Les tampons ajoutés sont **sauvegardés d'une session à l'autre** dans une bibliothèque personnelle.

### Bibliothèque de tampons

La bibliothèque est stockée dans `~/.pdf_editor/stamps/`. Elle est vide au premier lancement.

| Bouton | Action |
|--------|--------|
| ➕ Ajouter… | Importer une image (PNG, JPG, BMP, WebP, TIFF) et lui donner un nom |
| 🗑 Supprimer | Retirer le tampon sélectionné de la bibliothèque |

### Options

| Option | Description |
|--------|-------------|
| Position | Bas-droit, Bas-gauche, Haut-droit, Haut-gauche, Centre |
| Pages | Toutes les pages, Première page, Dernière page |
| Taille | Pourcentage de la largeur de la page (5 % à 100 %) |
| Opacité | De 10 % à 100 % |

> **Transparence** : les images PNG avec fond transparent (signatures, logos) conservent leur transparence dans le PDF.

Un **aperçu en temps réel** s'affiche à droite du dialogue.

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="windows"></a>
## 18. Intégration Windows — clic droit

*Aide → 🖥 Intégration Windows (clic droit)…*

PDF Editor propose deux entrées dans le menu contextuel de l'explorateur Windows, toutes deux **activées automatiquement** au premier lancement. Elles sont gérables via *Aide → 🖥 Intégration Windows (clic droit)…* ou l'onglet **Aide** du panneau latéral.

---

### 18.1 Transformer une image en PDF

Convertit un fichier image en PDF d'un simple clic droit (traitement en arrière-plan, pas d'interface).

**Utilisation**

1. Clic droit sur un fichier image dans l'explorateur.
2. Sélectionnez **Transformer en PDF - PDF EDITOR**.
3. Le PDF est créé dans le **même dossier**, avec le même nom de base (`.pdf`).
4. Une confirmation s'affiche à la fin.

**Formats** : JPG · JPEG · PNG · BMP · TIFF · TIF · WebP

> Si un PDF du même nom existe déjà, un suffixe numérique est ajouté (`fichier_1.pdf`, `fichier_2.pdf`…).

---

### 18.2 Combiner des fichiers dans PDF Editor

Ouvre le dialogue **Réorganiser/Fusionner** avec plusieurs fichiers pré-chargés. Idéal pour assembler rapidement des PDFs et/ou des images en un seul document.

**Utilisation**

1. Dans l'explorateur Windows, **sélectionnez plusieurs fichiers** (Ctrl+clic ou Maj+clic).
2. Faites un **clic droit** sur la sélection.
3. Choisissez **Combiner dans PDF Editor**.
4. PDF Editor s'ouvre et affiche le dialogue de réorganisation avec tous les fichiers pré-chargés sous forme de vignettes.
5. Réordonnez les pages selon vos besoins, puis cliquez **Appliquer** et enregistrez.

**Formats compatibles** : PDF · JPG · JPEG · PNG · BMP · TIFF · TIF · WebP

> L'entrée apparaît aussi lors du clic droit sur un seul fichier compatible.
> Les images sont automatiquement converties en PDF temporaire avant d'être affichées dans le dialogue.

---

<a name="metadata"></a>
## 19. Métadonnées du document

*Outils → ℹ Métadonnées…*

Consultez et modifiez les informations enregistrées dans le fichier PDF :

| Champ | Description |
|-------|-------------|
| Titre | Titre du document |
| Auteur | Nom de l'auteur |
| Sujet | Thème ou description courte |
| Mots-clés | Mots-clés séparés par des virgules |
| Application | Logiciel ayant créé le document |

Ces métadonnées sont visibles dans les propriétés du fichier (explorateur Windows, lecteurs PDF).

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="compression"></a>
## 20. Compression PDF

*Outils → ⚡ Compresser le PDF*

Réduit la taille du fichier en optimisant les flux internes du PDF (compression des objets et recompression des données existantes).

- La compression est appliquée **immédiatement** sur le document ouvert.
- Un message en bas de l'écran indique la réduction obtenue (en Ko ou Mo).
- Pensez à enregistrer (`Ctrl+S`) pour conserver le résultat.

> L'effet est plus marqué sur les PDF non optimisés (exports Word, scans…). Les PDF déjà compressés verront peu de différence.

> Cette opération est **annulable** via `Ctrl+Z`.

---

<a name="protection"></a>
## 21. Protection par mot de passe

### Protéger un document

1. *Outils → 🔒 Protéger par mot de passe…*
2. Saisissez un mot de passe **utilisateur** (lecture) et/ou **propriétaire** (modification).
3. Confirmez — le document sera chiffré et enregistré dans un nouveau fichier.

### Supprimer la protection

1. Ouvrez le document avec le mot de passe propriétaire.
2. *Outils → 🔓 Supprimer la protection…*
3. La protection est retirée et enregistrée dans un nouveau fichier.

---

<a name="signature"></a>
## 22. Signature numérique

PDF Editor permet de signer un document avec un certificat numérique `.pfx` / `.p12`.

### Accès

- Via le menu : *Outils → ✍ Signer le document…*
- Via le panneau latéral : onglet **Outils** → *✍ Signer le document…*

### Signer

1. *Outils → ✍ Signer le document…*
2. Renseignez :
   - **Chemin vers le certificat** : fichier `.pfx` ou `.p12`
   - **Mot de passe** du certificat
   - **Raison** et **Localisation** (optionnel)
   - **Page** où apposer la signature visible
3. Cliquez sur **OK**.

### Vérifier les signatures

*Outils → 🔎 Vérifier les signatures…* (ou bouton *🔎 Vérifier les signatures…* dans le panneau Outils) affiche la liste des signatures et leur statut de validité.

### Obtenir un certificat `.pfx`

*Aide → 🔑 Comment obtenir un certificat .pfx ?* explique les options :
- Certificat auprès d'une Autorité de Certification (Certum, Sectigo, GlobalSign…)
- Certificat auto-signé avec OpenSSL (usage interne uniquement)

---

<a name="recherche"></a>
## 23. Recherche de texte

1. *Édition → 🔍 Rechercher…* ou `Ctrl+F`
2. Saisissez le terme à rechercher.
3. Les occurrences sont surlignées ; utilisez **Précédent / Suivant** pour naviguer.

---

<a name="extraction"></a>
## 24. Extraction de contenu

### Extraire le texte

*Outils → 📄 Extraire le texte…* (ou bouton dans le panneau *Outils*)

Une boîte de dialogue permet de choisir les pages à extraire :

| Option | Description |
|--------|-------------|
| **Toutes les pages** | Extrait le texte de l'intégralité du document |
| **Page courante (N)** | Extrait uniquement la page affichée |
| **Intervalle** | Saisir une plage *De la page X à Y* |

Après confirmation du fichier de destination, un **résumé** s'affiche :
- Pages extraites
- Nombre de caractères, mots et lignes
- Taille du fichier généré

### Extraire les images

*Outils → 🖼 Extraire les images…* → choisir un dossier de destination.

Toutes les images intégrées dans le PDF sont extraites dans le dossier choisi.

---

<a name="enregistrer"></a>
## 25. Enregistrer le document

| Action | Raccourci |
|--------|-----------|
| Enregistrer | `Ctrl+S` |
| Enregistrer sous… | `Ctrl+Maj+S` |

> Le titre de la fenêtre affiche un astérisque `*` lorsque le document a des modifications non enregistrées.

---

<a name="annuler"></a>
## 26. Annuler / Rétablir

PDF Editor dispose d'un historique complet des modifications permettant d'annuler ou rétablir toutes les opérations.

| Raccourci | Action |
|-----------|--------|
| `Ctrl+Z` | Annuler la dernière opération |
| `Ctrl+Y` | Rétablir |

L'historique est également accessible via *Édition → ↩ Annuler* et *Édition → ↪ Rétablir*.

### Opérations annulables

| Opération | Annulable |
|-----------|-----------|
| Ajouter une annotation | ✅ |
| Déplacer un bloc de texte | ✅ |
| Rotation de page | ✅ |
| Filigrane | ✅ |
| En-têtes / pieds de page | ✅ |
| Tampon texte | ✅ |
| Tampon image | ✅ |
| Compression PDF | ✅ |
| Métadonnées | ✅ |
| Réorganiser / fusionner les pages | ✅ |
| Supprimer une page | ✅ |
| Protéger / déprotéger | ❌ (crée un nouveau fichier) |
| Signer | ❌ (opération irréversible) |
| Fractionner | ❌ (crée de nouveaux fichiers) |

> L'historique est effacé à l'ouverture d'un nouveau document.

---

<a name="langue"></a>
## 27. Thèmes et langue

### Thème

*Affichage → 🌙 Thème sombre* ou *Affichage → ☀ Thème clair* — appliqué immédiatement.

### Langue de l'interface

**Méthode rapide** : onglet **Langue** du panneau latéral gauche — cliquez sur la langue souhaitée.

**Via le menu** : *Langue* → Français, English, Deutsch, Español, Italiano, Português, Русский.

Un redémarrage est proposé pour appliquer le changement. Les langues disponibles sont :

| Code | Langue |
|------|--------|
| 🇫🇷 `fr` | Français |
| 🇬🇧 `en` | English |
| 🇩🇪 `de` | Deutsch |
| 🇪🇸 `es` | Español |
| 🇮🇹 `it` | Italiano |
| 🇵🇹 `pt` | Português |
| 🇷🇺 `ru` | Русский |

### Onglet Aide

L'onglet **Aide** du panneau latéral donne un accès rapide à :
- **📖 Manuel utilisateur** (équivalent à `F1`)
- **🖥 Intégration Windows (clic droit)…** (voir [§18](#windows))
- La liste des **raccourcis clavier** principaux

### À propos

*Aide → ℹ À propos* (en bas du menu) affiche la version, les technologies utilisées et le lien vers le support : [pdfeditor.lemonsqueezy.com](https://pdfeditor.lemonsqueezy.com)

---

<a name="raccourcis"></a>
## 28. Raccourcis clavier

### Fichier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+O` | Ouvrir un fichier |
| `Ctrl+S` | Enregistrer |
| `Ctrl+Maj+S` | Enregistrer sous |
| `Ctrl+P` | Imprimer |
| `Ctrl+W` | Fermer le document |
| `Alt+F4` | Quitter |

### Édition

| Raccourci | Action |
|-----------|--------|
| `Ctrl+Z` | Annuler |
| `Ctrl+Y` | Rétablir |
| `Ctrl+F` | Rechercher |

### Navigation

| Raccourci | Action |
|-----------|--------|
| `←` | Page précédente |
| `→` | Page suivante |

### Affichage

| Raccourci | Action |
|-----------|--------|
| `Ctrl+=` | Zoom avant |
| `Ctrl+-` | Zoom arrière |
| `Ctrl+0` | Ajuster à la page |
| `Ctrl+1` | Ajuster à la largeur |
| `F4` | Afficher/masquer le panneau latéral |

### Outils

| Raccourci | Action |
|-----------|--------|
| `S` | Outil Sélection |
| `T` | Outil Modifier texte |
| `H` | Outil Surligner |
| `C` | Outil Commentaire |
| `I` | Outil Image |
| `E` | Outil Effacer |
| `M` | Déplacer un bloc de texte |
| `R` | Tourner la page +90° |
| `Maj+R` | Tourner la page -90° |
| `Ctrl+Suppr` | Supprimer la page courante |
| `F1` | Manuel utilisateur |

---

*Manuel mis à jour le 26/03/2026 — PDF Editor v1.4.1*
*Support : [pdfeditor.lemonsqueezy.com](https://pdfeditor.lemonsqueezy.com)*
