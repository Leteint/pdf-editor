"""English translations — keys are the canonical French strings."""

TRANSLATIONS: dict[str, str] = {
    # ── Menus ──────────────────────────────────────────────────────────────
    "Fichier": "File",
    "Ouvrir…": "Open…",
    "Fichiers récents": "Recent Files",
    "Enregistrer": "Save",
    "Enregistrer sous…": "Save As…",
    "Fermer": "Close",
    "Quitter": "Quit",
    "Édition": "Edit",
    "Annuler": "Undo",
    "Rétablir": "Redo",
    "Affichage": "View",
    "Zoom +": "Zoom In",
    "Zoom -": "Zoom Out",
    "Ajuster à la page": "Fit Page",
    "Ajuster à la largeur": "Fit Width",
    "Afficher/masquer le panneau Pages": "Show/Hide Pages Panel",
    "Afficher/masquer les outils": "Show/Hide Tools",
    "Thème sombre": "Dark Theme",
    "Thème clair": "Light Theme",
    "Langue": "Language",
    "Outils": "Tools",
    "Fusionner des PDFs…": "Merge PDFs…",
    "Découper ce PDF…": "Split this PDF…",
    "Extraire le texte…": "Extract Text…",
    "Extraire les images…": "Extract Images…",
    "Protéger par mot de passe…": "Password Protect…",
    "Supprimer la protection…": "Remove Protection…",
    "Tourner la page (+90°)": "Rotate Page (+90°)",
    "Tourner la page (-90°)": "Rotate Page (-90°)",
    "Signature": "Signature",
    "Signer le document…": "Sign Document…",
    "Vérifier les signatures…": "Verify Signatures…",
    "Aide": "Help",
    "À propos": "About",
    "Comment obtenir un certificat .pfx ?": "How to get a .pfx certificate?",

    # ── Main toolbar ───────────────────────────────────────────────────────
    "Barre principale": "Main Toolbar",
    "Ouvrir": "Open",
    "Ouvrir un fichier PDF": "Open a PDF file",
    "Enr. sous…": "Save As…",
    "◀ Préc.": "◀ Prev.",
    "Suiv. ▶": "Next ▶",
    "Ajuster page": "Fit Page",
    "Ajuster largeur": "Fit Width",

    # ── Annotation toolbar ─────────────────────────────────────────────────
    "Annotations": "Annotations",
    "Sélection": "Select",
    "Modifier texte": "Edit Text",
    "Surligner": "Highlight",
    "Souligner": "Underline",
    "Commentaire": "Comment",
    "Image": "Image",
    "Effacer": "Erase",

    # ── Docks / tabs ───────────────────────────────────────────────────────
    "Pages": "Pages",
    "Recherche": "Search",
    "OCR": "OCR",

    # ── Status bar ─────────────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Welcome to PDF Editor. Open a file to get started.",
    "Ouvert : {name}": "Opened: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [read-only — owner password required to edit]",
    "Fichier enregistré.": "File saved.",
    "Enregistré sous : {path}": "Saved as: {path}",
    "Document fermé.": "Document closed.",
    "Page {page} / {total}": "Page {page} / {total}",
    "Texte copié : « {snippet} »": "Text copied: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "No text found in selection.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Resize / move the image then click ✓ Confirm.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Resize the image then click ✓ Confirm.",
    "Image supprimée.": "Image deleted.",
    "Image remplacée.": "Image replaced.",
    "Aucune annotation dans la sélection.": "No annotation in selection.",
    "{n} annotation(s) effacée(s).": "{n} annotation(s) erased.",
    "Annulé : {desc}": "Undone: {desc}",
    "Rétabli : {desc}": "Redone: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Text edited in place ({method}). Save to keep changes.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Text edited (overlay). Save to keep changes.",
    "Rendu non rafraîchi : {err}": "View not refreshed: {err}",
    "Édition en place échouée : {err}": "In-place edit failed: {err}",
    "Texte exporté : {path}": "Text exported: {path}",
    "PDF protégé enregistré.": "Protected PDF saved.",
    "PDF déprotégé enregistré.": "Unprotected PDF saved.",
    "Document déverrouillé — modifications autorisées.":
        "Document unlocked — editing allowed.",
    "Police : {info}": "Font: {info}",
    "  Gras": "  Bold",
    "  Italique": "  Italic",
    "  Couleur : {color}": "  Color: {color}",

    # ── Dialogs — titles ───────────────────────────────────────────────────
    "Ouvrir un PDF": "Open a PDF",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;All files (*)",
    "Fichier protégé": "Protected File",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "This file is encrypted. Enter the password to open it:",
    "Erreur": "Error",
    "Impossible d'ouvrir le fichier :\n{err}": "Cannot open file:\n{err}",
    "Enregistrer sous…": "Save As…",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Fermer": "Close",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "The document has been modified. Save before closing?",
    "Effacer les annotations": "Erase Annotations",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "Delete {n} selected annotation(s)?",
    "Image PDF": "PDF Image",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Image detected: « {name} »\nWhat would you like to do?",
    "Supprimer": "Delete",
    "Remplacer…": "Replace…",
    "Annuler": "Cancel",
    "Choisir une image à insérer": "Choose an image to insert",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Choose a replacement image",
    "Impossible de lire l'image :\n{err}": "Cannot read image:\n{err}",
    "Exporter le texte": "Export Text",
    "Texte (*.txt)": "Text (*.txt)",
    "{n} image(s) extraite(s).": "{n} image(s) extracted.",
    "Dossier de sortie": "Output Folder",
    "Succès": "Success",
    "Protection": "Protection",
    "Mot de passe :": "Password:",
    "Déverrouillage": "Unlock",
    "Mot de passe requis": "Password Required",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "This document is protected. Enter the password to edit it:",
    "Mot de passe incorrect.": "Incorrect password.",
    "Signatures": "Signatures",
    "Aucune signature trouvée.": "No signature found.",
    "Quitter": "Quit",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "The document has unsaved changes. Quit anyway?",
    "Annuler : {desc}": "Undo: {desc}",
    "Rétablir : {desc}": "Redo: {desc}",

    # ── Language menu ──────────────────────────────────────────────────────
    "Appliquer la langue": "Apply Language",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "Restart to apply language « {lang} »?",
    "La langue sera appliquée au prochain démarrage.":
        "The language will be applied on next startup.",

    # ── Help — pfx ─────────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Getting a .pfx Signing Certificate",
    (
        "<b>Certificat de signature numérique (.pfx / .p12)</b><br><br>"
        "Pour que la signature soit vérifiable par des tiers, il faut un certificat "
        "émis par une <b>Autorité de Certification (CA) reconnue</b>.<br><br>"
        "<b>Fournisseurs courants :</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Coût :</b> 50 – 200 €/an selon le niveau de validation.<br>"
        "Le fournisseur livre directement un fichier <b>.pfx</b> (ou .p12) "
        "protégé par un mot de passe.<br><br>"
        "<i>Pour un usage interne uniquement, vous pouvez générer un certificat "
        "auto-signé avec OpenSSL :<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ): (
        "<b>Digital signing certificate (.pfx / .p12)</b><br><br>"
        "For the signature to be verifiable by third parties, you need a certificate "
        "issued by a <b>recognized Certificate Authority (CA)</b>.<br><br>"
        "<b>Common providers:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Cost:</b> 50 – 200 €/year depending on validation level.<br>"
        "The provider delivers a <b>.pfx</b> (or .p12) file "
        "protected by a password.<br><br>"
        "<i>For internal use only, you can generate a self-signed certificate "
        "with OpenSSL:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),

    # ── About dialog ───────────────────────────────────────────────────────
    "À propos de PDF Editor": "About PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Free open-source PDF editor.<br>"
        "Stack: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "License: MIT"
    ),

    # ── Search panel ───────────────────────────────────────────────────────
    "Rechercher dans le document :": "Search in document:",
    "Terme de recherche…": "Search term…",
    "Chercher": "Search",
    "Respecter la casse": "Case sensitive",
    "Recherche en cours…": "Searching…",
    "Aucun résultat.": "No results.",
    "{n} occurrence(s) trouvée(s).": "{n} match(es) found.",
    "Erreur : {err}": "Error: {err}",

    # ── OCR panel ──────────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR is not installed.\n\n"
        "Download it here:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Then restart the application."
    ),
    "Langue :": "Language:",
    "Lancer l'OCR sur la page courante": "Run OCR on current page",
    "Texte extrait :": "Extracted text:",
    "Copier": "Copy",
    "Exporter .txt": "Export .txt",
    "Erreur OCR": "OCR Error",
    "Exporter le texte": "Export Text",
    "Fichier texte (*.txt)": "Text file (*.txt)",

    # ── Sign dialog ────────────────────────────────────────────────────────
    "Signer le document": "Sign Document",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko is not installed.\n"
        "Install it with: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Path to .pfx / .p12 file",
    "Certificat (.pfx) :": "Certificate (.pfx):",
    "Raison :": "Reason:",
    "Document signé électroniquement": "Electronically signed document",
    "Lieu :": "Location:",
    "Contact :": "Contact:",
    "Page :": "Page:",
    "Sélectionner le certificat": "Select Certificate",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Certificates (*.pfx *.p12);;All files (*)",
    "Sélectionnez un fichier certificat valide.":
        "Please select a valid certificate file.",
    "Enregistrer le PDF signé": "Save Signed PDF",
    "PDF signé sauvegardé :\n{path}": "Signed PDF saved:\n{path}",

    # ── Merge dialog ───────────────────────────────────────────────────────
    "Fusionner des PDFs": "Merge PDFs",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "Files to merge (drag to reorder):",
    "Ajouter…": "Add…",
    "Choisir des PDFs": "Choose PDFs",
    "Supprimer": "Remove",
    "↑ Monter": "↑ Up",
    "↓ Descendre": "↓ Down",
    "Attention": "Warning",
    "Ajoutez au moins 2 fichiers PDF.": "Add at least 2 PDF files.",
    "Enregistrer le PDF fusionné": "Save Merged PDF",
    "PDF fusionné :\n{path}": "Merged PDF:\n{path}",

    # ── Split dialog ───────────────────────────────────────────────────────
    "Découper le PDF": "Split PDF",
    "Mode de découpage": "Split Mode",
    "Une page par fichier (toutes les pages)": "One page per file (all pages)",
    "Extraire une plage de pages :": "Extract a page range:",
    "De": "From",
    "à": "to",
    "{n} fichiers créés dans :\n{dir}": "{n} files created in:\n{dir}",
    "Enregistrer l'extrait": "Save Extract",
    "Extrait sauvegardé :\n{path}": "Extract saved:\n{path}",

    # ── Left panel — PDF tools section (v1.2) ─────────────────────────────
    "🛠  Outils PDF": "🛠  PDF Tools",
    "Réorganiser/Fusionner…": "Reorganize/Merge…",
    "Fractionner…": "Split…",
    "En-têtes / pieds de page…": "Headers / Footers…",

    # ── Additional menus (v1.2) ────────────────────────────────────────────
    "Nouveau formulaire vierge…": "New Blank Form…",
    "Imprimer…": "Print…",
    "Insérer une image…": "Insert Image…",
    "Insérer un bloc de texte…": "Insert Text Block…",
    "Déplacer un bloc de texte": "Move Text Block",
    "Réorganiser/Fusionner les pages…": "Reorganize/Merge Pages…",
    "Fractionner ce PDF…": "Split this PDF…",
    "Supprimer la page courante": "Delete Current Page",
    "Métadonnées…": "Metadata…",
    "En-têtes et pieds de page…": "Headers & Footers…",
    "Filigrane…": "Watermark…",
    "Tampon texte…": "Text Stamp…",
    "Tampon image…": "Image Stamp…",
    "Compresser le PDF": "Compress PDF",
    "Reconnaissance de caractères (OCR)…": "Character Recognition (OCR)…",
    "Rechercher…": "Search…",
    "Manuel utilisateur": "User Manual",
    "Intégration Windows (clic droit)…": "Windows Integration (right-click)…",
    "Formulaire": "Form",

    # ── Pages & Form toolbar (v1.2) ────────────────────────────────────────
    "Pages & Formulaire": "Pages & Form",
    "⊕ Réorganiser/Fusionner": "⊕ Reorganize/Merge",
    "Réorganiser/Fusionner les pages…": "Reorganize/Merge Pages…",
    "✂ Fractionner": "✂ Split",
    "🗑 Suppr. page": "🗑 Del. Page",
    "Supprimer la page courante (Delete)": "Delete Current Page (Delete)",
    "🖼 Insérer image": "🖼 Insert Image",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Draw a zone to insert an image into the PDF",
    "📝 Insérer texte": "📝 Insert Text",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Draw a zone to insert a text block into the PDF",
    "✏ Mode Design": "✏ Design Mode",
    "Activer/désactiver le mode design de formulaire":
        "Enable/disable form design mode",

    # ── Tool panel (v1.3) ─────────────────────────────────────────────────
    "🛠  Outils": "🛠  Tools",
    "✏  Annotations": "✏  Annotations",
    "Couleur :": "Color:",
    "Personnalisé": "Custom",
    "Épaisseur :": "Thickness:",
    "💡 Raccourcis": "💡 Shortcuts",
    "Double-clic → modifier texte": "Double-click → edit text",
    "Clic droit → menu contextuel": "Right-click → context menu",
    "H  Surligner": "H  Highlight",
    "C  Commentaire": "C  Comment",
    "E  Effacer": "E  Erase",
    "M  Déplacer texte": "M  Move Text",

    # ── Text stamp dialog (v1.2) ───────────────────────────────────────────
    "Ajouter un tampon": "Add a Stamp",
    "APPROUVÉ": "APPROVED",
    "REJETÉ": "REJECTED",
    "À SIGNER": "TO SIGN",
    "CONFIDENTIEL": "CONFIDENTIAL",
    "BROUILLON": "DRAFT",
    "URGENT": "URGENT",
    "COPIE": "COPY",
    "À RÉVISER": "TO REVIEW",
    "Personnalisé…": "Custom…",
    "Tampon :": "Stamp:",
    "Votre texte…": "Your text…",
    "Position :": "Position:",
    "Pages :": "Pages:",
    "Horizontal  (0°)": "Horizontal  (0°)",
    "Diagonal  (−45°)": "Diagonal  (−45°)",
    "Rotation :": "Rotation:",
    "Opacité :": "Opacity:",
    "Appliquer": "Apply",
    "Aperçu :": "Preview:",
    "Haut-droit": "Top-right",
    "Haut-gauche": "Top-left",
    "Bas-droit": "Bottom-right",
    "Bas-gauche": "Bottom-left",
    "Centre": "Center",
    "Toutes les pages": "All pages",
    "Première page": "First page",
    "Dernière page": "Last page",

    # ── Image stamp dialog (v1.2) ──────────────────────────────────────────
    "Tampon image": "Image Stamp",
    "Bibliothèque de tampons :": "Stamp library:",
    "Supprimer ce tampon de la bibliothèque": "Remove this stamp from library",
    "Taille :": "Size:",
    " % largeur page": " % page width",
    "Choisir une image": "Choose an Image",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Stamp Name",
    "Donnez un nom à ce tampon :": "Give this stamp a name:",
    "Mon tampon": "My stamp",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "Remove stamp « {n} » from library?",

    # ── Organize dialog (v1.2) ─────────────────────────────────────────────
    "Organiser les pages": "Organize Pages",
    "Ajouter un document…": "Add Document…",
    "Monter": "Move Up",
    "Descendre": "Move Down",
    "Documents supportés": "Supported Documents",
    "Images": "Images",
    "Ajouter un document": "Add Document",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} page(s) total — {orig} original, {removed} removed",
    "Le document ne peut pas être vide.": "The document cannot be empty.",

    # ── Header/footer dialog (v1.2) ────────────────────────────────────────
    "En-têtes et pieds de page": "Headers & Footers",
    "En-tête": "Header",
    "Pied de page": "Footer",
    "Options communes": "Common Options",
    "Taille de police :": "Font size:",
    "Marge depuis le bord :": "Margin from edge:",
    "Ne pas appliquer sur la 1ère page": "Do not apply on 1st page",
    "Gauche": "Left",
    "Droite": "Right",
    "En-tête gauche": "Left header",

    # ── Watermark dialog (v1.2) ────────────────────────────────────────────
    "Ajouter un filigrane": "Add Watermark",
    "Texte :": "Text:",

    # ── Metadata dialog (v1.2) ─────────────────────────────────────────────
    "Métadonnées du document": "Document Metadata",
    "Informations enregistrées dans le fichier PDF :":
        "Information stored in the PDF file:",
    "Titre :": "Title:",
    "Auteur :": "Author:",
    "Sujet :": "Subject:",
    "Mots-clés :": "Keywords:",
    "Application :": "Application:",

    # ── Help dialog (v1.2) ─────────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "User Manual — PDF Editor",
    "Rechercher :": "Search:",
    "Mot-clé…": "Keyword…",
    "Occurrence précédente": "Previous Match",
    "Occurrence suivante": "Next Match",
    "Fichier de documentation introuvable :\n": "Documentation file not found:\n",

    # ── Form panel (v1.2) ──────────────────────────────────────────────────
    "Nouveau formulaire vierge": "New Blank Form",
    "✏  Mode Design — Ajouter des champs": "✏  Design Mode — Add Fields",
    "Aucun formulaire détecté dans ce PDF.": "No form detected in this PDF.",
    "Enregistrer et exporter JSON": "Save and Export JSON",
    "JSON embarqué :": "Embedded JSON:",
    "JSON précédemment embarqué.": "Previously embedded JSON.",
    "Données sauvegardées.": "Data saved.",

    # ── Status bar (v1.2) ─────────────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Form: {n} field(s)",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Pages reorganized — remember to save (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Save New PDF",
    "Nouveau PDF créé et ouvert : {name}": "New PDF created and opened: {name}",
    "En-têtes/pieds de page supprimés.": "Headers/footers removed.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Headers/footers added — remember to save (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Watermark added to all pages — remember to save (Ctrl+S).",
    "toutes les pages": "all pages",
    "la première page": "the first page",
    "la dernière page": "the last page",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Stamp « {t} » added to {n} — remember to save (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Image stamp applied to {n} — remember to save (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Metadata updated — remember to save (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Compression done — estimated gain: {kb} KB. Save to finalize (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "The document is already optimal — no compression gain possible.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} OCR line(s) embedded on the page.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Text modified. Save to keep changes.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Block moved. Save to keep changes.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Block deleted. Save to keep changes.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Text hidden. Save to keep changes.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Text removed from stream. Save to keep changes.",
    "Impossible de supprimer ce texte du flux.":
        "Cannot remove this text from the stream.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Right-click an element to select it, then Del to erase it.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Click directly on an OCR text block to edit it.",
    "Champ « {name} » modifié.": "Field « {name} » modified.",
    "Champ « {name} » ({type}) ajouté.": "Field « {name} » ({type}) added.",
    "Nom de champ vide — champ non créé.": "Empty field name — field not created.",
    "Chemin d'image manquant.": "Missing image path.",

    # ── Dialog prompts (v1.2) ─────────────────────────────────────────────
    "Modifications non enregistrées": "Unsaved Changes",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "The document has been modified. Save before continuing?",
    "Ne pas enregistrer": "Don't Save",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Changes have been made. Save before closing?",
    "Quitter sans enregistrer": "Quit Without Saving",
    "Redémarrer": "Restart",
    "Modifier le texte…": "Edit Text…",
    "Supprimer ce bloc": "Delete This Block",
    "Modifier le champ « {name} »…": "Edit Field « {name} »…",
    "Supprimer le champ « {name} »": "Delete Field « {name} »",
    "Modifier « {t}… »": "Edit « {t}… »",
    "Masquer (rectangle blanc)": "Hide (white rectangle)",
    "Supprimer du flux PDF": "Remove from PDF Stream",
    "Déplacer / redimensionner…": "Move / Resize…",
    "Nom déjà utilisé": "Name Already Used",
    "Un champ nommé « {name} » existe déjà.":
        "A field named « {name} » already exists.",
    "Saisir le commentaire :": "Enter comment:",
    "Modifier le commentaire": "Edit Comment",
    "Modifier le texte": "Edit Text",
    "Remplacer l'image": "Replace Image",
    "Supprimer la page": "Delete Page",
    "Impossible de supprimer l'unique page du document.":
        "Cannot delete the document's only page.",
    "Supprimer la page {n} du document ?": "Delete page {n} from the document?",
    "Page {n} supprimée.": "Page {n} deleted.",

    # ── Windows integration dialog (v1.2) ─────────────────────────────────
    "Intégration Windows — clic droit": "Windows Integration — Right-click",
    "✅ Actif": "✅ Active",
    "❌ Inactif": "❌ Inactive",
    "Statut :": "Status:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "When integration is active, right-clicking an image file "
        "({exts}) in Windows Explorer offers the "
        "<b>Convert to PDF</b> option. The PDF is created in the same folder "
        "as the image."
    ),
    "Désactiver": "Disable",
    "Activer": "Enable",
    "Intégration Windows": "Windows Integration",
    "Clic droit désactivé pour les fichiers images.":
        "Right-click disabled for image files.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "Right-click enabled!\n\n"
        "Right-click any image "
        "({exts}) in Explorer to convert to PDF."
    ),

    # ── Extract text dialog (v1.4) ─────────────────────────────────────────
    "Extraire le texte": "Extract Text",
    "Toutes les pages ({n})": "All pages ({n})",
    "Page courante ({n})": "Current page ({n})",
    "Intervalle :": "Range:",
    "De la page": "From page",
    "Extraction": "Extraction",
    "Pages {a} à {b}": "Pages {a} to {b}",
    "Page {n}": "Page {n}",
    "Extraction réussie ✅": "Extraction successful ✅",
    "Extraction terminée avec succès !": "Extraction completed successfully!",
    "Pages extraites :": "Extracted pages:",
    "Caractères :": "Characters:",
    "Mots :": "Words:",
    "Lignes :": "Lines:",
    "Fichier :": "File:",

    # ── Language panel (v1.4) ──────────────────────────────────────────────
    "Choisir la langue :": "Choose language:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "A restart is required\nto apply the change.",

    # ── Help panel (v1.4) ─────────────────────────────────────────────────
    "Actions rapides :": "Quick actions:",
    "Raccourcis clavier :": "Keyboard shortcuts:",

    # ── License dialog (v1.4) ─────────────────────────────────────────────
    "Activation de PDF Editor": "PDF Editor Activation",
    "Licence…": "License…",
    "Licence — PDF Editor": "License — PDF Editor",
    "Clé de licence :": "License key:",
    "Vérification…": "Checking…",
    "Connexion à Lemon Squeezy…": "Connecting to Lemon Squeezy…",
    "Licence activée avec succès.": "License activated successfully.",
    "Licence valide.": "License valid.",
    "Licence désactivée sur cet ordinateur.": "License deactivated on this computer.",
    "Désactiver cette licence": "Deactivate this license",
    "Désactiver la licence": "Deactivate License",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "Remove the license from this computer?\n\nYou can reactivate it on another machine.",
    "Aucune licence activée sur cet ordinateur.": "No license activated on this computer.",
    "Entrer une clé de licence": "Enter a license key",
    "Clé de licence invalide.": "Invalid license key.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "Cannot validate license (offline for too long).",
    "Pas encore de licence ? ": "No license yet? ",
    "Acheter PDF Editor": "Buy PDF Editor",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Please enter your license key received by email after purchase.\nFormat: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Offline mode — {remaining} day(s) remaining.",
    "Licence": "License",

    # ── Shell integration — combine (v1.4) ────────────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Convert an image to PDF",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Combine files in PDF Editor",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "When integration is active, selecting multiple files "
        "({exts}) in Windows Explorer offers the option "
        "<b>Combine in PDF Editor</b>. The organize dialog "
        "opens with these files pre-loaded."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "Combine enabled!\n\n"
        "Select multiple files ({exts}) in Explorer,\n"
        "right-click and choose «\u202fCombine in PDF Editor\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Right-click «\u202fCombine\u202f» disabled.",
}
