"""Traduzioni italiane — le chiavi sono le stringhe canoniche in francese."""

TRANSLATIONS: dict[str, str] = {
    # ── Menu ───────────────────────────────────────────────────────────────
    "Fichier": "File",
    "Ouvrir…": "Apri…",
    "Fichiers récents": "File recenti",
    "Enregistrer": "Salva",
    "Enregistrer sous…": "Salva come…",
    "Fermer": "Chiudi",
    "Quitter": "Esci",
    "Édition": "Modifica",
    "Annuler": "Annulla",
    "Rétablir": "Ripristina",
    "Affichage": "Visualizza",
    "Zoom +": "Zoom +",
    "Zoom -": "Zoom -",
    "Ajuster à la page": "Adatta alla pagina",
    "Ajuster à la largeur": "Adatta alla larghezza",
    "Afficher/masquer le panneau Pages": "Mostra/nascondi pannello pagine",
    "Afficher/masquer les outils": "Mostra/nascondi strumenti",
    "Thème sombre": "Tema scuro",
    "Thème clair": "Tema chiaro",
    "Langue": "Lingua",
    "Outils": "Strumenti",
    "Fusionner des PDFs…": "Unisci PDF…",
    "Découper ce PDF…": "Dividi questo PDF…",
    "Extraire le texte…": "Estrai testo…",
    "Extraire les images…": "Estrai immagini…",
    "Protéger par mot de passe…": "Proteggi con password…",
    "Supprimer la protection…": "Rimuovi protezione…",
    "Tourner la page (+90°)": "Ruota pagina (+90°)",
    "Tourner la page (-90°)": "Ruota pagina (-90°)",
    "Signature": "Firma",
    "Signer le document…": "Firma documento…",
    "Vérifier les signatures…": "Verifica firme…",
    "Aide": "Aiuto",
    "À propos": "Informazioni",
    "Comment obtenir un certificat .pfx ?": "Come ottenere un certificato .pfx?",

    # ── Barra degli strumenti ──────────────────────────────────────────────
    "Barre principale": "Barra principale",
    "Ouvrir": "Apri",
    "Ouvrir un fichier PDF": "Apri un file PDF",
    "Enr. sous…": "Salva come…",
    "◀ Préc.": "◀ Prec.",
    "Suiv. ▶": "Succ. ▶",
    "Ajuster page": "Adat. pagina",
    "Ajuster largeur": "Adat. largh.",
    "Annotations": "Annotazioni",
    "Sélection": "Selezione",
    "Modifier texte": "Modifica testo",
    "Surligner": "Evidenzia",
    "Souligner": "Sottolinea",
    "Commentaire": "Commento",
    "Image": "Immagine",
    "Effacer": "Cancella",

    # ── Pannelli / schede ──────────────────────────────────────────────────
    "Pages": "Pagine",
    "Recherche": "Ricerca",
    "OCR": "OCR",

    # ── Barra di stato ─────────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Benvenuto in PDF Editor. Apri un file per iniziare.",
    "Ouvert : {name}": "Aperto: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [sola lettura — password proprietario richiesta per modificare]",
    "Fichier enregistré.": "File salvato.",
    "Enregistré sous : {path}": "Salvato come: {path}",
    "Document fermé.": "Documento chiuso.",
    "Page {page} / {total}": "Pagina {page} / {total}",
    "Texte copié : « {snippet} »": "Testo copiato: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "Nessun testo trovato nella selezione.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Ridimensiona / sposta l'immagine poi clicca ✓ Conferma.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Ridimensiona l'immagine poi clicca ✓ Conferma.",
    "Image supprimée.": "Immagine eliminata.",
    "Image remplacée.": "Immagine sostituita.",
    "Aucune annotation dans la sélection.": "Nessuna annotazione nella selezione.",
    "{n} annotation(s) effacée(s).": "{n} annotazione/i cancellata/e.",
    "Annulé : {desc}": "Annullato: {desc}",
    "Rétabli : {desc}": "Ripristinato: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Testo modificato in loco ({method}). Salva per conservare le modifiche.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Testo modificato (overlay). Salva per conservare le modifiche.",
    "Rendu non rafraîchi : {err}": "Vista non aggiornata: {err}",
    "Édition en place échouée : {err}": "Modifica in loco fallita: {err}",
    "Texte exporté : {path}": "Testo esportato: {path}",
    "PDF protégé enregistré.": "PDF protetto salvato.",
    "PDF déprotégé enregistré.": "PDF non protetto salvato.",
    "Document déverrouillé — modifications autorisées.":
        "Documento sbloccato — modifiche consentite.",
    "  Gras": "  Grassetto",
    "  Italique": "  Corsivo",

    # ── Finestre di dialogo ────────────────────────────────────────────────
    "Ouvrir un PDF": "Apri un PDF",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;Tutti i file (*)",
    "Fichier protégé": "File protetto",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "Questo file è crittografato. Inserisci la password per aprirlo:",
    "Erreur": "Errore",
    "Impossible d'ouvrir le fichier :\n{err}": "Impossibile aprire il file:\n{err}",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "Il documento è stato modificato. Salvare prima di chiudere?",
    "Effacer les annotations": "Cancella annotazioni",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "Eliminare {n} annotazione/i selezionata/e?",
    "Image PDF": "Immagine PDF",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Immagine rilevata: « {name} »\nCosa vuoi fare?",
    "Supprimer": "Elimina",
    "Remplacer…": "Sostituisci…",
    "Choisir une image à insérer": "Scegli un'immagine da inserire",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Immagini (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Scegli immagine sostitutiva",
    "Impossible de lire l'image :\n{err}": "Impossibile leggere l'immagine:\n{err}",
    "Exporter le texte": "Esporta testo",
    "Texte (*.txt)": "Testo (*.txt)",
    "{n} image(s) extraite(s).": "{n} immagine/i estratta/e.",
    "Dossier de sortie": "Cartella di output",
    "Succès": "Successo",
    "Protection": "Protezione",
    "Mot de passe :": "Password:",
    "Déverrouillage": "Sblocca",
    "Mot de passe requis": "Password richiesta",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "Questo documento è protetto. Inserisci la password per modificarlo:",
    "Mot de passe incorrect.": "Password errata.",
    "Signatures": "Firme",
    "Aucune signature trouvée.": "Nessuna firma trovata.",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "Il documento ha modifiche non salvate. Uscire comunque?",
    "Annuler : {desc}": "Annulla: {desc}",
    "Rétablir : {desc}": "Ripristina: {desc}",

    # ── Menu lingua ────────────────────────────────────────────────────────
    "Appliquer la langue": "Applica lingua",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "Riavviare per applicare la lingua « {lang} »?",
    "La langue sera appliquée au prochain démarrage.":
        "La lingua verrà applicata al prossimo avvio.",

    # ── Aiuto — pfx ────────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Ottenere un certificato di firma .pfx",
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
        "<b>Certificato di firma digitale (.pfx / .p12)</b><br><br>"
        "Perché la firma sia verificabile da terze parti, è necessario un certificato "
        "emesso da una <b>Autorità di Certificazione (CA) riconosciuta</b>.<br><br>"
        "<b>Provider comuni:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Costo:</b> 50 – 200 €/anno a seconda del livello di validazione.<br>"
        "Il provider consegna direttamente un file <b>.pfx</b> (o .p12) "
        "protetto da password.<br><br>"
        "<i>Solo per uso interno, puoi generare un certificato auto-firmato "
        "con OpenSSL:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),
    "À propos de PDF Editor": "Informazioni su PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Versione 1.0.0<br><br>"
        "Editor PDF open source gratuito.<br>"
        "Stack: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licenza: MIT"
    ),

    # ── Pannello di ricerca ────────────────────────────────────────────────
    "Rechercher dans le document :": "Cerca nel documento:",
    "Terme de recherche…": "Termine di ricerca…",
    "Chercher": "Cerca",
    "Respecter la casse": "Rispetta maiuscole",
    "Recherche en cours…": "Ricerca in corso…",
    "Aucun résultat.": "Nessun risultato.",
    "{n} occurrence(s) trouvée(s).": "{n} occorrenza/e trovata/e.",
    "Erreur : {err}": "Errore: {err}",

    # ── Pannello OCR ───────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR non è installato.\n\n"
        "Scaricalo qui:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Poi riavvia l'applicazione."
    ),
    "Langue :": "Lingua:",
    "Lancer l'OCR sur la page courante": "Esegui OCR sulla pagina corrente",
    "Texte extrait :": "Testo estratto:",
    "Copier": "Copia",
    "Exporter .txt": "Esporta .txt",
    "Erreur OCR": "Errore OCR",
    "Fichier texte (*.txt)": "File di testo (*.txt)",

    # ── Finestra di dialogo firma ──────────────────────────────────────────
    "Signer le document": "Firma documento",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko non è installato.\n"
        "Installalo con: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Percorso al file .pfx / .p12",
    "Certificat (.pfx) :": "Certificato (.pfx):",
    "Raison :": "Motivo:",
    "Document signé électroniquement": "Documento firmato elettronicamente",
    "Lieu :": "Luogo:",
    "Contact :": "Contatto:",
    "Page :": "Pagina:",
    "Sélectionner le certificat": "Seleziona certificato",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Certificati (*.pfx *.p12);;Tutti i file (*)",
    "Sélectionnez un fichier certificat valide.":
        "Seleziona un file certificato valido.",
    "Enregistrer le PDF signé": "Salva PDF firmato",
    "PDF signé sauvegardé :\n{path}": "PDF firmato salvato:\n{path}",

    # ── Finestra di dialogo unione ─────────────────────────────────────────
    "Fusionner des PDFs": "Unisci PDF",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "File da unire (trascina per riordinare):",
    "Ajouter…": "Aggiungi…",
    "Choisir des PDFs": "Scegli PDF",
    "↑ Monter": "↑ Su",
    "↓ Descendre": "↓ Giù",
    "Attention": "Attenzione",
    "Ajoutez au moins 2 fichiers PDF.": "Aggiungi almeno 2 file PDF.",
    "Enregistrer le PDF fusionné": "Salva PDF unito",
    "PDF fusionné :\n{path}": "PDF unito:\n{path}",

    # ── Finestra di dialogo divisione ──────────────────────────────────────
    "Découper le PDF": "Dividi PDF",
    "Mode de découpage": "Modalità di divisione",
    "Une page par fichier (toutes les pages)": "Una pagina per file (tutte le pagine)",
    "Extraire une plage de pages :": "Estrai un intervallo di pagine:",
    "De": "Da",
    "à": "a",
    "{n} fichiers créés dans :\n{dir}": "{n} file creati in:\n{dir}",
    "Enregistrer l'extrait": "Salva estratto",
    "Extrait sauvegardé :\n{path}": "Estratto salvato:\n{path}",

    # ── Pannello sinistro — strumenti PDF (v1.2) ──────────────────────────
    "🛠  Outils PDF": "🛠  Strumenti PDF",
    "Réorganiser/Fusionner…": "Riorganizza/Unisci…",
    "Fractionner…": "Dividi…",
    "En-têtes / pieds de page…": "Intestazioni / piè di pagina…",

    # ── Menu aggiuntivi (v1.2) ─────────────────────────────────────────────
    "Nouveau formulaire vierge…": "Nuovo modulo vuoto…",
    "Imprimer…": "Stampa…",
    "Insérer une image…": "Inserisci immagine…",
    "Insérer un bloc de texte…": "Inserisci blocco di testo…",
    "Déplacer un bloc de texte": "Sposta blocco di testo",
    "Réorganiser/Fusionner les pages…": "Riorganizza/Unisci pagine…",
    "Fractionner ce PDF…": "Dividi questo PDF…",
    "Supprimer la page courante": "Elimina pagina corrente",
    "Métadonnées…": "Metadati…",
    "En-têtes et pieds de page…": "Intestazioni e piè di pagina…",
    "Filigrane…": "Filigrana…",
    "Tampon texte…": "Timbro testo…",
    "Tampon image…": "Timbro immagine…",
    "Compresser le PDF": "Comprimi PDF",
    "Reconnaissance de caractères (OCR)…": "Riconoscimento caratteri (OCR)…",
    "Rechercher…": "Cerca…",
    "Manuel utilisateur": "Manuale utente",
    "Intégration Windows (clic droit)…": "Integrazione Windows (clic destro)…",
    "Formulaire": "Modulo",

    # ── Barra Pagine & Modulo (v1.2) ───────────────────────────────────────
    "Pages & Formulaire": "Pagine & Modulo",
    "⊕ Réorganiser/Fusionner": "⊕ Riorganizza/Unisci",
    "Réorganiser/Fusionner les pages…": "Riorganizza/Unisci pagine…",
    "✂ Fractionner": "✂ Dividi",
    "🗑 Suppr. page": "🗑 Elim. pagina",
    "Supprimer la page courante (Delete)": "Elimina pagina corrente (Canc)",
    "🖼 Insérer image": "🖼 Inserisci immagine",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Disegna un'area per inserire un'immagine nel PDF",
    "📝 Insérer texte": "📝 Inserisci testo",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Disegna un'area per inserire un blocco di testo nel PDF",
    "✏ Mode Design": "✏ Modalità progetto",
    "Activer/désactiver le mode design de formulaire":
        "Attiva/disattiva la modalità di progetto del modulo",

    # ── Pannello strumenti (v1.2) ──────────────────────────────────────────
    "✏  Annotations": "✏  Annotazioni",
    "Couleur :": "Colore:",
    "Personnalisé": "Personalizzato",
    "Épaisseur :": "Spessore:",
    "💡 Raccourcis": "💡 Scorciatoie",
    "Double-clic → modifier texte": "Doppio clic → modifica testo",
    "Clic droit → menu contextuel": "Clic destro → menu contestuale",
    "H  Surligner": "H  Evidenzia",
    "C  Commentaire": "C  Commento",
    "E  Effacer": "E  Cancella",
    "M  Déplacer texte": "M  Sposta testo",

    # ── Dialogo timbro testo (v1.2) ────────────────────────────────────────
    "Ajouter un tampon": "Aggiungi un timbro",
    "APPROUVÉ": "APPROVATO",
    "REJETÉ": "RIFIUTATO",
    "À SIGNER": "DA FIRMARE",
    "CONFIDENTIEL": "RISERVATO",
    "BROUILLON": "BOZZA",
    "URGENT": "URGENTE",
    "COPIE": "COPIA",
    "À RÉVISER": "DA RIVEDERE",
    "Personnalisé…": "Personalizzato…",
    "Tampon :": "Timbro:",
    "Votre texte…": "Il vostro testo…",
    "Position :": "Posizione:",
    "Pages :": "Pagine:",
    "Horizontal  (0°)": "Orizzontale  (0°)",
    "Diagonal  (−45°)": "Diagonale  (−45°)",
    "Rotation :": "Rotazione:",
    "Opacité :": "Opacità:",
    "Appliquer": "Applica",
    "Aperçu :": "Anteprima:",
    "Haut-droit": "In alto a destra",
    "Haut-gauche": "In alto a sinistra",
    "Bas-droit": "In basso a destra",
    "Bas-gauche": "In basso a sinistra",
    "Centre": "Centro",
    "Toutes les pages": "Tutte le pagine",
    "Première page": "Prima pagina",
    "Dernière page": "Ultima pagina",

    # ── Dialogo timbro immagine (v1.2) ─────────────────────────────────────
    "Tampon image": "Timbro immagine",
    "Bibliothèque de tampons :": "Libreria timbri:",
    "Supprimer ce tampon de la bibliothèque": "Rimuovi questo timbro dalla libreria",
    "Taille :": "Dimensione:",
    " % largeur page": " % larghezza pagina",
    "Choisir une image": "Scegli un'immagine",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Immagini (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Nome del timbro",
    "Donnez un nom à ce tampon :": "Dai un nome a questo timbro:",
    "Mon tampon": "Il mio timbro",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "Rimuovere il timbro « {n} » dalla libreria?",

    # ── Dialogo organizza (v1.2) ───────────────────────────────────────────
    "Organiser les pages": "Organizza pagine",
    "Ajouter un document…": "Aggiungi documento…",
    "Monter": "Su",
    "Descendre": "Giù",
    "Documents supportés": "Documenti supportati",
    "Images": "Immagini",
    "Ajouter un document": "Aggiungi documento",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} pagina/e totali — {orig} originale/i, {removed} eliminata/e",
    "Le document ne peut pas être vide.": "Il documento non può essere vuoto.",

    # ── Dialogo intestazioni/piè (v1.2) ────────────────────────────────────
    "En-têtes et pieds de page": "Intestazioni e piè di pagina",
    "En-tête": "Intestazione",
    "Pied de page": "Piè di pagina",
    "Options communes": "Opzioni comuni",
    "Taille de police :": "Dimensione font:",
    "Marge depuis le bord :": "Margine dal bordo:",
    "Ne pas appliquer sur la 1ère page": "Non applicare alla 1ª pagina",
    "Gauche": "Sinistra",
    "Droite": "Destra",
    "En-tête gauche": "Intestazione sinistra",

    # ── Dialogo filigrana (v1.2) ───────────────────────────────────────────
    "Ajouter un filigrane": "Aggiungi filigrana",
    "Texte :": "Testo:",

    # ── Dialogo metadati (v1.2) ────────────────────────────────────────────
    "Métadonnées du document": "Metadati del documento",
    "Informations enregistrées dans le fichier PDF :":
        "Informazioni salvate nel file PDF:",
    "Titre :": "Titolo:",
    "Auteur :": "Autore:",
    "Sujet :": "Oggetto:",
    "Mots-clés :": "Parole chiave:",
    "Application :": "Applicazione:",

    # ── Dialogo guida (v1.2) ───────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "Manuale utente — PDF Editor",
    "Rechercher :": "Cerca:",
    "Mot-clé…": "Parola chiave…",
    "Occurrence précédente": "Corrispondenza precedente",
    "Occurrence suivante": "Corrispondenza successiva",
    "Fichier de documentation introuvable :\n": "File di documentazione non trovato:\n",

    # ── Pannello modulo (v1.2) ─────────────────────────────────────────────
    "Nouveau formulaire vierge": "Nuovo modulo vuoto",
    "✏  Mode Design — Ajouter des champs": "✏  Modalità progetto — Aggiungi campi",
    "Aucun formulaire détecté dans ce PDF.": "Nessun modulo rilevato in questo PDF.",
    "Enregistrer et exporter JSON": "Salva ed esporta JSON",
    "JSON embarqué :": "JSON incorporato:",
    "JSON précédemment embarqué.": "JSON precedentemente incorporato.",
    "Données sauvegardées.": "Dati salvati.",

    # ── Barra di stato (v1.2) ──────────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Modulo: {n} campo/i",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Pagine riorganizzate — ricorda di salvare (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Salva nuovo PDF",
    "Nouveau PDF créé et ouvert : {name}": "Nuovo PDF creato e aperto: {name}",
    "En-têtes/pieds de page supprimés.": "Intestazioni/piè di pagina rimossi.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Intestazioni/piè di pagina aggiunti — ricorda di salvare (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Filigrana aggiunta a tutte le pagine — ricorda di salvare (Ctrl+S).",
    "toutes les pages": "tutte le pagine",
    "la première page": "la prima pagina",
    "la dernière page": "l'ultima pagina",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Timbro « {t} » aggiunto su {n} — ricorda di salvare (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Timbro immagine applicato su {n} — ricorda di salvare (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Metadati aggiornati — ricorda di salvare (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Compressione eseguita — guadagno stimato: {kb} KB. Salva per finalizzare (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "Il documento è già ottimale — nessun guadagno di compressione possibile.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} riga/e OCR incorporata/e nella pagina.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Testo modificato. Salva per mantenere le modifiche.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Blocco spostato. Salva per mantenere le modifiche.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Blocco eliminato. Salva per mantenere le modifiche.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Testo nascosto. Salva per mantenere le modifiche.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Testo rimosso dal flusso. Salva per mantenere le modifiche.",
    "Impossible de supprimer ce texte du flux.":
        "Impossibile rimuovere questo testo dal flusso.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Clic destro su un elemento per selezionarlo, poi Canc per cancellarlo.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Fai clic direttamente su un blocco di testo OCR per modificarlo.",
    "Champ « {name} » modifié.": "Campo « {name} » modificato.",
    "Champ « {name} » ({type}) ajouté.": "Campo « {name} » ({type}) aggiunto.",
    "Nom de champ vide — champ non créé.": "Nome campo vuoto — campo non creato.",
    "Chemin d'image manquant.": "Percorso immagine mancante.",

    # ── Finestre di dialogo (v1.2) ─────────────────────────────────────────
    "Modifications non enregistrées": "Modifiche non salvate",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "Il documento è stato modificato. Salvare prima di continuare?",
    "Ne pas enregistrer": "Non salvare",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Sono state apportate modifiche. Salvare prima di chiudere?",
    "Quitter sans enregistrer": "Esci senza salvare",
    "Redémarrer": "Riavvia",
    "Modifier le texte…": "Modifica testo…",
    "Supprimer ce bloc": "Elimina questo blocco",
    "Modifier le champ « {name} »…": "Modifica campo « {name} »…",
    "Supprimer le champ « {name} »": "Elimina campo « {name} »",
    "Modifier « {t}… »": "Modifica « {t}… »",
    "Masquer (rectangle blanc)": "Nascondi (rettangolo bianco)",
    "Supprimer du flux PDF": "Rimuovi dal flusso PDF",
    "Déplacer / redimensionner…": "Sposta / ridimensiona…",
    "Nom déjà utilisé": "Nome già utilizzato",
    "Un champ nommé « {name} » existe déjà.":
        "Esiste già un campo denominato « {name} ».",
    "Saisir le commentaire :": "Inserisci commento:",
    "Modifier le commentaire": "Modifica commento",
    "Modifier le texte": "Modifica testo",
    "Remplacer l'image": "Sostituisci immagine",
    "Supprimer la page": "Elimina pagina",
    "Impossible de supprimer l'unique page du document.":
        "Impossibile eliminare l'unica pagina del documento.",
    "Supprimer la page {n} du document ?": "Eliminare la pagina {n} del documento?",
    "Page {n} supprimée.": "Pagina {n} eliminata.",

    # ── Integrazione Windows (v1.2) ────────────────────────────────────────
    "Intégration Windows — clic droit": "Integrazione Windows — clic destro",
    "✅ Actif": "✅ Attivo",
    "❌ Inactif": "❌ Inattivo",
    "Statut :": "Stato:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "Quando l'integrazione è attiva, facendo clic destro su un file immagine "
        "({exts}) in Esplora risorse di Windows appare l'opzione "
        "<b>Converti in PDF</b>. Il PDF viene creato nella stessa cartella "
        "dell'immagine."
    ),
    "Désactiver": "Disattiva",
    "Activer": "Attiva",
    "Intégration Windows": "Integrazione Windows",
    "Clic droit désactivé pour les fichiers images.":
        "Clic destro disattivato per i file immagine.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "Clic destro attivato!\n\n"
        "Fai clic destro su qualsiasi immagine "
        "({exts}) in Esplora risorse per convertire in PDF."
    ),

    # ── Dialogo estrazione testo (v1.4) ────────────────────────────────────
    "🛠  Outils": "🛠  Strumenti",
    "Extraire le texte": "Estrai testo",
    "Toutes les pages ({n})": "Tutte le pagine ({n})",
    "Page courante ({n})": "Pagina corrente ({n})",
    "Intervalle :": "Intervallo:",
    "De la page": "Dalla pagina",
    "Extraction": "Estrazione",
    "Pages {a} à {b}": "Pagine {a} a {b}",
    "Page {n}": "Pagina {n}",
    "Extraction réussie ✅": "Estrazione riuscita ✅",
    "Extraction terminée avec succès !": "Estrazione completata con successo!",
    "Pages extraites :": "Pagine estratte:",
    "Caractères :": "Caratteri:",
    "Mots :": "Parole:",
    "Lignes :": "Righe:",
    "Fichier :": "File:",

    # ── Pannello lingua (v1.4) ─────────────────────────────────────────────
    "Choisir la langue :": "Scegli lingua:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "È necessario riavviare\nper applicare la modifica.",

    # ── Pannello aiuto (v1.4) ─────────────────────────────────────────────
    "Actions rapides :": "Azioni rapide:",
    "Raccourcis clavier :": "Scorciatoie da tastiera:",

    # ── Dialogo licenza (v1.4) ────────────────────────────────────────────
    "Activation de PDF Editor": "Attivazione di PDF Editor",
    "Licence…": "Licenza…",
    "Licence — PDF Editor": "Licenza — PDF Editor",
    "Clé de licence :": "Chiave di licenza:",
    "Vérification…": "Verifica…",
    "Connexion à Lemon Squeezy…": "Connessione a Lemon Squeezy…",
    "Licence activée avec succès.": "Licenza attivata con successo.",
    "Licence valide.": "Licenza valida.",
    "Licence désactivée sur cet ordinateur.": "Licenza disattivata su questo computer.",
    "Désactiver cette licence": "Disattiva questa licenza",
    "Désactiver la licence": "Disattiva licenza",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "Rimuovere la licenza da questo computer?\n\nPotrai riattivarla su un altro dispositivo.",
    "Aucune licence activée sur cet ordinateur.": "Nessuna licenza attivata su questo computer.",
    "Entrer une clé de licence": "Inserire una chiave di licenza",
    "Clé de licence invalide.": "Chiave di licenza non valida.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "Impossibile validare la licenza (offline da troppo tempo).",
    "Pas encore de licence ? ": "Nessuna licenza ancora? ",
    "Acheter PDF Editor": "Acquista PDF Editor",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Inserisci la tua chiave di licenza ricevuta via email dopo l'acquisto.\nFormato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Modalità offline — {remaining} giorno/i rimanente/i.",
    "Licence": "Licenza",

    # ── Integrazione shell — combina (v1.4) ────────────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Converti immagine in PDF",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Combina file in PDF Editor",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "Quando l'integrazione è attiva, la selezione multipla di file "
        "({exts}) in Esplora risorse propone l'opzione "
        "<b>Combina in PDF Editor</b>. La finestra di organizzazione "
        "si apre con questi file precaricati."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "Combinazione attivata!\n\n"
        "Seleziona più file ({exts}) in Esplora risorse,\n"
        "fai clic destro e scegli «\u202fCombina in PDF Editor\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Clic destro «\u202fCombina\u202f» disattivato.",
}
