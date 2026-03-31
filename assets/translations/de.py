"""Deutsche Übersetzungen — Schlüssel sind die kanonischen französischen Zeichenketten."""

TRANSLATIONS: dict[str, str] = {
    # ── Menüs ──────────────────────────────────────────────────────────────
    "Fichier": "Datei",
    "Ouvrir…": "Öffnen…",
    "Fichiers récents": "Zuletzt geöffnet",
    "Enregistrer": "Speichern",
    "Enregistrer sous…": "Speichern unter…",
    "Fermer": "Schließen",
    "Quitter": "Beenden",
    "Édition": "Bearbeiten",
    "Annuler": "Rückgängig",
    "Rétablir": "Wiederholen",
    "Affichage": "Ansicht",
    "Zoom +": "Vergrößern",
    "Zoom -": "Verkleinern",
    "Ajuster à la page": "Seite anpassen",
    "Ajuster à la largeur": "Breite anpassen",
    "Afficher/masquer le panneau Pages": "Seitenbereich ein-/ausblenden",
    "Afficher/masquer les outils": "Werkzeuge ein-/ausblenden",
    "Thème sombre": "Dunkles Design",
    "Thème clair": "Helles Design",
    "Langue": "Sprache",
    "Outils": "Werkzeuge",
    "Fusionner des PDFs…": "PDFs zusammenführen…",
    "Découper ce PDF…": "PDF aufteilen…",
    "Extraire le texte…": "Text extrahieren…",
    "Extraire les images…": "Bilder extrahieren…",
    "Protéger par mot de passe…": "Mit Passwort schützen…",
    "Supprimer la protection…": "Schutz entfernen…",
    "Tourner la page (+90°)": "Seite drehen (+90°)",
    "Tourner la page (-90°)": "Seite drehen (-90°)",
    "Signature": "Signatur",
    "Signer le document…": "Dokument signieren…",
    "Vérifier les signatures…": "Signaturen prüfen…",
    "Aide": "Hilfe",
    "À propos": "Über",
    "Comment obtenir un certificat .pfx ?": "Wie erhält man ein .pfx-Zertifikat?",

    # ── Hauptleiste ────────────────────────────────────────────────────────
    "Barre principale": "Hauptleiste",
    "Ouvrir": "Öffnen",
    "Ouvrir un fichier PDF": "Eine PDF-Datei öffnen",
    "Enr. sous…": "Speich. unter…",
    "◀ Préc.": "◀ Zurück",
    "Suiv. ▶": "Weiter ▶",
    "Ajuster page": "Seite anpassen",
    "Ajuster largeur": "Breite anpassen",

    # ── Anmerkungsleiste ───────────────────────────────────────────────────
    "Annotations": "Anmerkungen",
    "Sélection": "Auswahl",
    "Modifier texte": "Text bearbeiten",
    "Surligner": "Hervorheben",
    "Souligner": "Unterstreichen",
    "Commentaire": "Kommentar",
    "Image": "Bild",
    "Effacer": "Löschen",

    # ── Bereiche / Reiter ──────────────────────────────────────────────────
    "Pages": "Seiten",
    "Recherche": "Suche",
    "OCR": "OCR",

    # ── Statusleiste ───────────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Willkommen beim PDF Editor. Öffnen Sie eine Datei, um zu beginnen.",
    "Ouvert : {name}": "Geöffnet: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [schreibgeschützt — Besitzerpasswort erforderlich]",
    "Fichier enregistré.": "Datei gespeichert.",
    "Enregistré sous : {path}": "Gespeichert unter: {path}",
    "Document fermé.": "Dokument geschlossen.",
    "Page {page} / {total}": "Seite {page} / {total}",
    "Texte copié : « {snippet} »": "Text kopiert: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "Kein Text in der Auswahl gefunden.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Bild skalieren / verschieben, dann ✓ Bestätigen klicken.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Bild skalieren, dann ✓ Bestätigen klicken.",
    "Image supprimée.": "Bild gelöscht.",
    "Image remplacée.": "Bild ersetzt.",
    "Aucune annotation dans la sélection.": "Keine Anmerkung in der Auswahl.",
    "{n} annotation(s) effacée(s).": "{n} Anmerkung(en) gelöscht.",
    "Annulé : {desc}": "Rückgängig: {desc}",
    "Rétabli : {desc}": "Wiederholt: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Text direkt bearbeitet ({method}). Speichern, um Änderungen zu behalten.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Text bearbeitet (Overlay). Speichern, um Änderungen zu behalten.",
    "Rendu non rafraîchi : {err}": "Ansicht nicht aktualisiert: {err}",
    "Édition en place échouée : {err}": "Direkte Bearbeitung fehlgeschlagen: {err}",
    "Texte exporté : {path}": "Text exportiert: {path}",
    "PDF protégé enregistré.": "Geschütztes PDF gespeichert.",
    "PDF déprotégé enregistré.": "Ungeschütztes PDF gespeichert.",
    "Document déverrouillé — modifications autorisées.":
        "Dokument entsperrt — Bearbeitung erlaubt.",
    "Police : {info}": "Schrift: {info}",
    "  Gras": "  Fett",
    "  Italique": "  Kursiv",
    "  Couleur : {color}": "  Farbe: {color}",

    # ── Dialoge ────────────────────────────────────────────────────────────
    "Ouvrir un PDF": "PDF öffnen",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;Alle Dateien (*)",
    "Fichier protégé": "Geschützte Datei",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "Diese Datei ist verschlüsselt. Passwort zum Öffnen eingeben:",
    "Erreur": "Fehler",
    "Impossible d'ouvrir le fichier :\n{err}": "Datei kann nicht geöffnet werden:\n{err}",
    "Enregistrer sous…": "Speichern unter…",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "Das Dokument wurde geändert. Vor dem Schließen speichern?",
    "Effacer les annotations": "Anmerkungen löschen",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "{n} ausgewählte Anmerkung(en) löschen?",
    "Image PDF": "PDF-Bild",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Bild erkannt: « {name} »\nWas möchten Sie tun?",
    "Supprimer": "Löschen",
    "Remplacer…": "Ersetzen…",
    "Annuler": "Abbrechen",
    "Choisir une image à insérer": "Bild zum Einfügen auswählen",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Bilder (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Ersatzbild auswählen",
    "Impossible de lire l'image :\n{err}": "Bild kann nicht gelesen werden:\n{err}",
    "Exporter le texte": "Text exportieren",
    "Texte (*.txt)": "Text (*.txt)",
    "{n} image(s) extraite(s).": "{n} Bild(er) extrahiert.",
    "Dossier de sortie": "Ausgabeordner",
    "Succès": "Erfolg",
    "Protection": "Schutz",
    "Mot de passe :": "Passwort:",
    "Déverrouillage": "Entsperren",
    "Mot de passe requis": "Passwort erforderlich",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "Dieses Dokument ist geschützt. Passwort zum Bearbeiten eingeben:",
    "Mot de passe incorrect.": "Falsches Passwort.",
    "Signatures": "Signaturen",
    "Aucune signature trouvée.": "Keine Signatur gefunden.",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "Das Dokument hat ungespeicherte Änderungen. Trotzdem beenden?",
    "Annuler : {desc}": "Rückgängig: {desc}",
    "Rétablir : {desc}": "Wiederholen: {desc}",

    # ── Sprachmenü ─────────────────────────────────────────────────────────
    "Appliquer la langue": "Sprache anwenden",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "Neu starten, um die Sprache « {lang} » anzuwenden?",
    "La langue sera appliquée au prochain démarrage.":
        "Die Sprache wird beim nächsten Start angewendet.",

    # ── Hilfe — pfx ────────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Ein .pfx-Signaturzertifikat erhalten",
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
        "<b>Digitales Signaturzertifikat (.pfx / .p12)</b><br><br>"
        "Damit die Signatur von Dritten verifiziert werden kann, benötigen Sie ein "
        "Zertifikat einer <b>anerkannten Zertifizierungsstelle (CA)</b>.<br><br>"
        "<b>Gängige Anbieter:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Kosten:</b> 50 – 200 €/Jahr je nach Validierungsstufe.<br>"
        "Der Anbieter liefert direkt eine <b>.pfx</b>-Datei (oder .p12), "
        "die mit einem Passwort geschützt ist.<br><br>"
        "<i>Nur für den internen Gebrauch können Sie ein selbstsigniertes "
        "Zertifikat mit OpenSSL erstellen:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),

    # ── Über-Dialog ────────────────────────────────────────────────────────
    "À propos de PDF Editor": "Über PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Kostenloser Open-Source-PDF-Editor.<br>"
        "Stack: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Lizenz: MIT"
    ),

    # ── Suchpanel ──────────────────────────────────────────────────────────
    "Rechercher dans le document :": "Im Dokument suchen:",
    "Terme de recherche…": "Suchbegriff…",
    "Chercher": "Suchen",
    "Respecter la casse": "Groß-/Kleinschreibung",
    "Recherche en cours…": "Suche läuft…",
    "Aucun résultat.": "Keine Ergebnisse.",
    "{n} occurrence(s) trouvée(s).": "{n} Treffer gefunden.",
    "Erreur : {err}": "Fehler: {err}",

    # ── OCR-Panel ──────────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR ist nicht installiert.\n\n"
        "Hier herunterladen:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Dann die Anwendung neu starten."
    ),
    "Langue :": "Sprache:",
    "Lancer l'OCR sur la page courante": "OCR auf aktueller Seite ausführen",
    "Texte extrait :": "Extrahierter Text:",
    "Copier": "Kopieren",
    "Exporter .txt": "Exportieren .txt",
    "Erreur OCR": "OCR-Fehler",
    "Fichier texte (*.txt)": "Textdatei (*.txt)",

    # ── Signaturdialog ─────────────────────────────────────────────────────
    "Signer le document": "Dokument signieren",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko ist nicht installiert.\n"
        "Installieren mit: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Pfad zur .pfx / .p12-Datei",
    "Certificat (.pfx) :": "Zertifikat (.pfx):",
    "Raison :": "Grund:",
    "Document signé électroniquement": "Elektronisch signiertes Dokument",
    "Lieu :": "Ort:",
    "Contact :": "Kontakt:",
    "Page :": "Seite:",
    "Sélectionner le certificat": "Zertifikat auswählen",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Zertifikate (*.pfx *.p12);;Alle Dateien (*)",
    "Sélectionnez un fichier certificat valide.":
        "Bitte eine gültige Zertifikatsdatei auswählen.",
    "Enregistrer le PDF signé": "Signiertes PDF speichern",
    "PDF signé sauvegardé :\n{path}": "Signiertes PDF gespeichert:\n{path}",

    # ── Zusammenführen-Dialog ──────────────────────────────────────────────
    "Fusionner des PDFs": "PDFs zusammenführen",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "Zusammenzuführende Dateien (ziehen zum Neuanordnen):",
    "Ajouter…": "Hinzufügen…",
    "Choisir des PDFs": "PDFs auswählen",
    "↑ Monter": "↑ Nach oben",
    "↓ Descendre": "↓ Nach unten",
    "Attention": "Achtung",
    "Ajoutez au moins 2 fichiers PDF.": "Mindestens 2 PDF-Dateien hinzufügen.",
    "Enregistrer le PDF fusionné": "Zusammengeführtes PDF speichern",
    "PDF fusionné :\n{path}": "PDF zusammengeführt:\n{path}",

    # ── Aufteilen-Dialog ───────────────────────────────────────────────────
    "Découper le PDF": "PDF aufteilen",
    "Mode de découpage": "Aufteilungsmodus",
    "Une page par fichier (toutes les pages)": "Eine Seite pro Datei (alle Seiten)",
    "Extraire une plage de pages :": "Seitenbereich extrahieren:",
    "De": "Von",
    "à": "bis",
    "{n} fichiers créés dans :\n{dir}": "{n} Datei(en) erstellt in:\n{dir}",
    "Enregistrer l'extrait": "Extrakt speichern",
    "Extrait sauvegardé :\n{path}": "Extrakt gespeichert:\n{path}",

    # ── Linkes Bedienfeld — PDF-Werkzeuge (v1.2) ──────────────────────────
    "🛠  Outils PDF": "🛠  PDF-Werkzeuge",
    "Réorganiser/Fusionner…": "Neu anordnen/Zusammenführen…",
    "Fractionner…": "Aufteilen…",
    "En-têtes / pieds de page…": "Kopf- / Fußzeilen…",

    # ── Zusätzliche Menüs (v1.2) ───────────────────────────────────────────
    "Nouveau formulaire vierge…": "Neues leeres Formular…",
    "Imprimer…": "Drucken…",
    "Insérer une image…": "Bild einfügen…",
    "Insérer un bloc de texte…": "Textblock einfügen…",
    "Déplacer un bloc de texte": "Textblock verschieben",
    "Réorganiser/Fusionner les pages…": "Seiten neu anordnen/zusammenführen…",
    "Fractionner ce PDF…": "Diese PDF aufteilen…",
    "Supprimer la page courante": "Aktuelle Seite löschen",
    "Métadonnées…": "Metadaten…",
    "En-têtes et pieds de page…": "Kopf- und Fußzeilen…",
    "Filigrane…": "Wasserzeichen…",
    "Tampon texte…": "Textstempel…",
    "Tampon image…": "Bildstempel…",
    "Compresser le PDF": "PDF komprimieren",
    "Reconnaissance de caractères (OCR)…": "Zeichenerkennung (OCR)…",
    "Rechercher…": "Suchen…",
    "Manuel utilisateur": "Benutzerhandbuch",
    "Intégration Windows (clic droit)…": "Windows-Integration (Rechtsklick)…",
    "Formulaire": "Formular",

    # ── Seiten & Formular-Leiste (v1.2) ───────────────────────────────────
    "Pages & Formulaire": "Seiten & Formular",
    "⊕ Réorganiser/Fusionner": "⊕ Neu anordnen/Zusammenführen",
    "Réorganiser/Fusionner les pages…": "Seiten neu anordnen/zusammenführen…",
    "✂ Fractionner": "✂ Aufteilen",
    "🗑 Suppr. page": "🗑 Seite löschen",
    "Supprimer la page courante (Delete)": "Aktuelle Seite löschen (Entf)",
    "🖼 Insérer image": "🖼 Bild einfügen",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Bereich zeichnen, um ein Bild in die PDF einzufügen",
    "📝 Insérer texte": "📝 Text einfügen",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Bereich zeichnen, um einen Textblock in die PDF einzufügen",
    "✏ Mode Design": "✏ Design-Modus",
    "Activer/désactiver le mode design de formulaire":
        "Formular-Design-Modus ein-/ausschalten",

    # ── Werkzeugbereich (v1.2) ─────────────────────────────────────────────
    "✏  Annotations": "✏  Anmerkungen",
    "Couleur :": "Farbe:",
    "Personnalisé": "Benutzerdefiniert",
    "Épaisseur :": "Stärke:",
    "💡 Raccourcis": "💡 Tastenkürzel",
    "Double-clic → modifier texte": "Doppelklick → Text bearbeiten",
    "Clic droit → menu contextuel": "Rechtsklick → Kontextmenü",
    "H  Surligner": "H  Hervorheben",
    "C  Commentaire": "C  Kommentar",
    "E  Effacer": "E  Löschen",
    "M  Déplacer texte": "M  Text verschieben",

    # ── Textstempel-Dialog (v1.2) ──────────────────────────────────────────
    "Ajouter un tampon": "Stempel hinzufügen",
    "APPROUVÉ": "GENEHMIGT",
    "REJETÉ": "ABGELEHNT",
    "À SIGNER": "ZU UNTERZEICHNEN",
    "CONFIDENTIEL": "VERTRAULICH",
    "BROUILLON": "ENTWURF",
    "URGENT": "DRINGEND",
    "COPIE": "KOPIE",
    "À RÉVISER": "ZU ÜBERARBEITEN",
    "Personnalisé…": "Benutzerdefiniert…",
    "Tampon :": "Stempel:",
    "Votre texte…": "Ihr Text…",
    "Position :": "Position:",
    "Pages :": "Seiten:",
    "Horizontal  (0°)": "Horizontal  (0°)",
    "Diagonal  (−45°)": "Diagonal  (−45°)",
    "Rotation :": "Drehung:",
    "Opacité :": "Deckkraft:",
    "Appliquer": "Anwenden",
    "Aperçu :": "Vorschau:",
    "Haut-droit": "Oben rechts",
    "Haut-gauche": "Oben links",
    "Bas-droit": "Unten rechts",
    "Bas-gauche": "Unten links",
    "Centre": "Mitte",
    "Toutes les pages": "Alle Seiten",
    "Première page": "Erste Seite",
    "Dernière page": "Letzte Seite",

    # ── Bildstempel-Dialog (v1.2) ──────────────────────────────────────────
    "Tampon image": "Bildstempel",
    "Bibliothèque de tampons :": "Stempelbibliothek:",
    "Supprimer ce tampon de la bibliothèque": "Diesen Stempel aus der Bibliothek entfernen",
    "Taille :": "Größe:",
    " % largeur page": " % Seitenbreite",
    "Choisir une image": "Bild auswählen",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Bilder (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Stempelname",
    "Donnez un nom à ce tampon :": "Geben Sie diesem Stempel einen Namen:",
    "Mon tampon": "Mein Stempel",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "Stempel « {n} » aus der Bibliothek entfernen?",

    # ── Seiten-Organisieren-Dialog (v1.2) ──────────────────────────────────
    "Organiser les pages": "Seiten organisieren",
    "Ajouter un document…": "Dokument hinzufügen…",
    "Monter": "Nach oben",
    "Descendre": "Nach unten",
    "Documents supportés": "Unterstützte Dokumente",
    "Images": "Bilder",
    "Ajouter un document": "Dokument hinzufügen",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} Seite(n) insgesamt — {orig} original, {removed} gelöscht",
    "Le document ne peut pas être vide.": "Das Dokument darf nicht leer sein.",

    # ── Kopf-/Fußzeilen-Dialog (v1.2) ──────────────────────────────────────
    "En-têtes et pieds de page": "Kopf- und Fußzeilen",
    "En-tête": "Kopfzeile",
    "Pied de page": "Fußzeile",
    "Options communes": "Allgemeine Optionen",
    "Taille de police :": "Schriftgröße:",
    "Marge depuis le bord :": "Abstand vom Rand:",
    "Ne pas appliquer sur la 1ère page": "Nicht auf der 1. Seite anwenden",
    "Gauche": "Links",
    "Droite": "Rechts",
    "En-tête gauche": "Linke Kopfzeile",

    # ── Wasserzeichen-Dialog (v1.2) ────────────────────────────────────────
    "Ajouter un filigrane": "Wasserzeichen hinzufügen",
    "Texte :": "Text:",

    # ── Metadaten-Dialog (v1.2) ────────────────────────────────────────────
    "Métadonnées du document": "Dokumentmetadaten",
    "Informations enregistrées dans le fichier PDF :":
        "Im PDF-Dokument gespeicherte Informationen:",
    "Titre :": "Titel:",
    "Auteur :": "Autor:",
    "Sujet :": "Betreff:",
    "Mots-clés :": "Schlüsselwörter:",
    "Application :": "Anwendung:",

    # ── Hilfe-Dialog (v1.2) ────────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "Benutzerhandbuch — PDF Editor",
    "Rechercher :": "Suchen:",
    "Mot-clé…": "Stichwort…",
    "Occurrence précédente": "Vorheriger Treffer",
    "Occurrence suivante": "Nächster Treffer",
    "Fichier de documentation introuvable :\n": "Dokumentationsdatei nicht gefunden:\n",

    # ── Formular-Bereich (v1.2) ────────────────────────────────────────────
    "Nouveau formulaire vierge": "Neues leeres Formular",
    "✏  Mode Design — Ajouter des champs": "✏  Design-Modus — Felder hinzufügen",
    "Aucun formulaire détecté dans ce PDF.": "Kein Formular in dieser PDF gefunden.",
    "Enregistrer et exporter JSON": "Speichern und als JSON exportieren",
    "JSON embarqué :": "Eingebettetes JSON:",
    "JSON précédemment embarqué.": "Zuvor eingebettetes JSON.",
    "Données sauvegardées.": "Daten gespeichert.",

    # ── Statusleiste (v1.2) ────────────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Formular: {n} Feld(er)",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Seiten neu angeordnet — bitte speichern (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Neue PDF speichern",
    "Nouveau PDF créé et ouvert : {name}": "Neue PDF erstellt und geöffnet: {name}",
    "En-têtes/pieds de page supprimés.": "Kopf-/Fußzeilen entfernt.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Kopf-/Fußzeilen hinzugefügt — bitte speichern (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Wasserzeichen auf allen Seiten hinzugefügt — bitte speichern (Ctrl+S).",
    "toutes les pages": "alle Seiten",
    "la première page": "die erste Seite",
    "la dernière page": "die letzte Seite",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Stempel « {t} » auf {n} hinzugefügt — bitte speichern (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Bildstempel auf {n} angewendet — bitte speichern (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Metadaten aktualisiert — bitte speichern (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Komprimierung abgeschlossen — geschätzter Gewinn: {kb} KB. Speichern zum Abschließen (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "Das Dokument ist bereits optimal — kein Komprimierungsgewinn möglich.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} OCR-Zeile(n) auf der Seite eingebettet.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Text geändert. Speichern, um Änderungen zu behalten.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Block verschoben. Speichern, um Änderungen zu behalten.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Block gelöscht. Speichern, um Änderungen zu behalten.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Text ausgeblendet. Speichern, um Änderungen zu behalten.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Text aus dem Stream entfernt. Speichern, um Änderungen zu behalten.",
    "Impossible de supprimer ce texte du flux.":
        "Dieser Text kann nicht aus dem Stream entfernt werden.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Rechtsklick auf ein Element zum Auswählen, dann Entf zum Löschen.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Klicken Sie direkt auf einen OCR-Textblock, um ihn zu bearbeiten.",
    "Champ « {name} » modifié.": "Feld « {name} » geändert.",
    "Champ « {name} » ({type}) ajouté.": "Feld « {name} » ({type}) hinzugefügt.",
    "Nom de champ vide — champ non créé.": "Feldname leer — Feld nicht erstellt.",
    "Chemin d'image manquant.": "Bildpfad fehlt.",

    # ── Dialogfelder (v1.2) ────────────────────────────────────────────────
    "Modifications non enregistrées": "Nicht gespeicherte Änderungen",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "Das Dokument wurde geändert. Vor dem Fortfahren speichern?",
    "Ne pas enregistrer": "Nicht speichern",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Es wurden Änderungen vorgenommen. Vor dem Schließen speichern?",
    "Quitter sans enregistrer": "Ohne Speichern beenden",
    "Redémarrer": "Neu starten",
    "Modifier le texte…": "Text bearbeiten…",
    "Supprimer ce bloc": "Diesen Block löschen",
    "Modifier le champ « {name} »…": "Feld « {name} » bearbeiten…",
    "Supprimer le champ « {name} »": "Feld « {name} » löschen",
    "Modifier « {t}… »": "Bearbeiten « {t}… »",
    "Masquer (rectangle blanc)": "Ausblenden (weißes Rechteck)",
    "Supprimer du flux PDF": "Aus PDF-Stream entfernen",
    "Déplacer / redimensionner…": "Verschieben / Größe ändern…",
    "Nom déjà utilisé": "Name bereits vergeben",
    "Un champ nommé « {name} » existe déjà.":
        "Ein Feld mit dem Namen « {name} » existiert bereits.",
    "Saisir le commentaire :": "Kommentar eingeben:",
    "Modifier le commentaire": "Kommentar bearbeiten",
    "Modifier le texte": "Text bearbeiten",
    "Remplacer l'image": "Bild ersetzen",
    "Supprimer la page": "Seite löschen",
    "Impossible de supprimer l'unique page du document.":
        "Die einzige Seite des Dokuments kann nicht gelöscht werden.",
    "Supprimer la page {n} du document ?": "Seite {n} aus dem Dokument löschen?",
    "Page {n} supprimée.": "Seite {n} gelöscht.",

    # ── Windows-Integration (v1.2) ─────────────────────────────────────────
    "Intégration Windows — clic droit": "Windows-Integration — Rechtsklick",
    "✅ Actif": "✅ Aktiv",
    "❌ Inactif": "❌ Inaktiv",
    "Statut :": "Status:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "Wenn die Integration aktiv ist, bietet ein Rechtsklick auf eine Bilddatei "
        "({exts}) im Windows-Explorer die Option "
        "<b>In PDF umwandeln</b>. Die PDF wird im gleichen Ordner "
        "wie das Bild erstellt."
    ),
    "Désactiver": "Deaktivieren",
    "Activer": "Aktivieren",
    "Intégration Windows": "Windows-Integration",
    "Clic droit désactivé pour les fichiers images.":
        "Rechtsklick für Bilddateien deaktiviert.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "Rechtsklick aktiviert!\n\n"
        "Klicken Sie mit der rechten Maustaste auf ein beliebiges Bild "
        "({exts}) im Explorer, um es in PDF umzuwandeln."
    ),

    # ── Textextraktions-Dialog (v1.4) ──────────────────────────────────────
    "🛠  Outils": "🛠  Werkzeuge",
    "Extraire le texte": "Text extrahieren",
    "Toutes les pages ({n})": "Alle Seiten ({n})",
    "Page courante ({n})": "Aktuelle Seite ({n})",
    "Intervalle :": "Bereich:",
    "De la page": "Von Seite",
    "Extraction": "Extraktion",
    "Pages {a} à {b}": "Seiten {a} bis {b}",
    "Page {n}": "Seite {n}",
    "Extraction réussie ✅": "Extraktion erfolgreich ✅",
    "Extraction terminée avec succès !": "Extraktion erfolgreich abgeschlossen!",
    "Pages extraites :": "Extrahierte Seiten:",
    "Caractères :": "Zeichen:",
    "Mots :": "Wörter:",
    "Lignes :": "Zeilen:",
    "Fichier :": "Datei:",

    # ── Sprachpanel (v1.4) ─────────────────────────────────────────────────
    "Choisir la langue :": "Sprache wählen:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "Ein Neustart ist erforderlich,\num die Änderung anzuwenden.",

    # ── Hilfepanel (v1.4) ─────────────────────────────────────────────────
    "Actions rapides :": "Schnellaktionen:",
    "Raccourcis clavier :": "Tastaturkürzel:",

    # ── Lizenzdialog (v1.4) ───────────────────────────────────────────────
    "Activation de PDF Editor": "PDF Editor Aktivierung",
    "Licence…": "Lizenz…",
    "Licence — PDF Editor": "Lizenz — PDF Editor",
    "Clé de licence :": "Lizenzschlüssel:",
    "Vérification…": "Prüfung…",
    "Connexion à Lemon Squeezy…": "Verbindung zu Lemon Squeezy…",
    "Licence activée avec succès.": "Lizenz erfolgreich aktiviert.",
    "Licence valide.": "Lizenz gültig.",
    "Licence désactivée sur cet ordinateur.": "Lizenz auf diesem Computer deaktiviert.",
    "Désactiver cette licence": "Diese Lizenz deaktivieren",
    "Désactiver la licence": "Lizenz deaktivieren",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "Lizenz von diesem Computer entfernen?\n\nSie können sie auf einem anderen Gerät reaktivieren.",
    "Aucune licence activée sur cet ordinateur.": "Keine Lizenz auf diesem Computer aktiviert.",
    "Entrer une clé de licence": "Lizenzschlüssel eingeben",
    "Clé de licence invalide.": "Ungültiger Lizenzschlüssel.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "Lizenz kann nicht validiert werden (zu lange offline).",
    "Pas encore de licence ? ": "Noch keine Lizenz? ",
    "Acheter PDF Editor": "PDF Editor kaufen",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Bitte geben Sie Ihren Lizenzschlüssel ein, den Sie nach dem Kauf per E-Mail erhalten haben.\nFormat: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Offline-Modus — noch {remaining} Tag(e).",
    "Licence": "Lizenz",

    # ── Shell-Integration — Zusammenführen (v1.4) ──────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Bild in PDF umwandeln",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Dateien in PDF Editor zusammenführen",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "Wenn die Integration aktiv ist, bietet eine Mehrfachauswahl von Dateien "
        "({exts}) im Windows-Explorer die Option "
        "<b>In PDF Editor zusammenführen</b>. Der Organisationsdialog "
        "öffnet sich mit diesen vorgeladenen Dateien."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "Zusammenführen aktiviert!\n\n"
        "Wählen Sie mehrere Dateien ({exts}) im Explorer aus,\n"
        "klicken Sie mit der rechten Maustaste und wählen Sie "
        "«\u202fIn PDF Editor zusammenführen\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Rechtsklick «\u202fZusammenführen\u202f» deaktiviert.",
}
