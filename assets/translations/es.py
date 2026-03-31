"""Traducciones al español — las claves son las cadenas canónicas en francés."""

TRANSLATIONS: dict[str, str] = {
    # ── Menús ──────────────────────────────────────────────────────────────
    "Fichier": "Archivo",
    "Ouvrir…": "Abrir…",
    "Fichiers récents": "Archivos recientes",
    "Enregistrer": "Guardar",
    "Enregistrer sous…": "Guardar como…",
    "Fermer": "Cerrar",
    "Quitter": "Salir",
    "Édition": "Edición",
    "Annuler": "Deshacer",
    "Rétablir": "Rehacer",
    "Affichage": "Vista",
    "Zoom +": "Ampliar",
    "Zoom -": "Reducir",
    "Ajuster à la page": "Ajustar a la página",
    "Ajuster à la largeur": "Ajustar al ancho",
    "Afficher/masquer le panneau Pages": "Mostrar/ocultar panel de páginas",
    "Afficher/masquer les outils": "Mostrar/ocultar herramientas",
    "Thème sombre": "Tema oscuro",
    "Thème clair": "Tema claro",
    "Langue": "Idioma",
    "Outils": "Herramientas",
    "Fusionner des PDFs…": "Combinar PDFs…",
    "Découper ce PDF…": "Dividir este PDF…",
    "Extraire le texte…": "Extraer texto…",
    "Extraire les images…": "Extraer imágenes…",
    "Protéger par mot de passe…": "Proteger con contraseña…",
    "Supprimer la protection…": "Eliminar protección…",
    "Tourner la page (+90°)": "Rotar página (+90°)",
    "Tourner la page (-90°)": "Rotar página (-90°)",
    "Signature": "Firma",
    "Signer le document…": "Firmar documento…",
    "Vérifier les signatures…": "Verificar firmas…",
    "Aide": "Ayuda",
    "À propos": "Acerca de",
    "Comment obtenir un certificat .pfx ?": "¿Cómo obtener un certificado .pfx?",

    # ── Barra de herramientas ──────────────────────────────────────────────
    "Barre principale": "Barra principal",
    "Ouvrir": "Abrir",
    "Ouvrir un fichier PDF": "Abrir un archivo PDF",
    "Enr. sous…": "Guard. como…",
    "◀ Préc.": "◀ Ant.",
    "Suiv. ▶": "Sig. ▶",
    "Ajuster page": "Aj. página",
    "Ajuster largeur": "Aj. ancho",
    "Annotations": "Anotaciones",
    "Sélection": "Selección",
    "Modifier texte": "Editar texto",
    "Surligner": "Resaltar",
    "Souligner": "Subrayar",
    "Commentaire": "Comentario",
    "Image": "Imagen",
    "Effacer": "Borrar",

    # ── Paneles / pestañas ─────────────────────────────────────────────────
    "Pages": "Páginas",
    "Recherche": "Búsqueda",
    "OCR": "OCR",

    # ── Barra de estado ────────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Bienvenido a PDF Editor. Abra un archivo para comenzar.",
    "Ouvert : {name}": "Abierto: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [solo lectura — se requiere contraseña de propietario para editar]",
    "Fichier enregistré.": "Archivo guardado.",
    "Enregistré sous : {path}": "Guardado como: {path}",
    "Document fermé.": "Documento cerrado.",
    "Page {page} / {total}": "Página {page} / {total}",
    "Texte copié : « {snippet} »": "Texto copiado: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "No se encontró texto en la selección.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Redimensione / mueva la imagen y haga clic en ✓ Confirmar.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Redimensione la imagen y haga clic en ✓ Confirmar.",
    "Image supprimée.": "Imagen eliminada.",
    "Image remplacée.": "Imagen reemplazada.",
    "Aucune annotation dans la sélection.": "Sin anotaciones en la selección.",
    "{n} annotation(s) effacée(s).": "{n} anotación/es borrada/s.",
    "Annulé : {desc}": "Deshecho: {desc}",
    "Rétabli : {desc}": "Rehecho: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Texto editado en el lugar ({method}). Guarde para conservar los cambios.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Texto modificado (superposición). Guarde para conservar los cambios.",
    "Rendu non rafraîchi : {err}": "Vista no actualizada: {err}",
    "Édition en place échouée : {err}": "Edición en el lugar fallida: {err}",
    "Texte exporté : {path}": "Texto exportado: {path}",
    "PDF protégé enregistré.": "PDF protegido guardado.",
    "PDF déprotégé enregistré.": "PDF desprotegido guardado.",
    "Document déverrouillé — modifications autorisées.":
        "Documento desbloqueado — edición permitida.",
    "  Gras": "  Negrita",
    "  Italique": "  Cursiva",

    # ── Diálogos ───────────────────────────────────────────────────────────
    "Ouvrir un PDF": "Abrir un PDF",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;Todos los archivos (*)",
    "Fichier protégé": "Archivo protegido",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "Este archivo está cifrado. Ingrese la contraseña para abrirlo:",
    "Erreur": "Error",
    "Impossible d'ouvrir le fichier :\n{err}": "No se puede abrir el archivo:\n{err}",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "El documento ha sido modificado. ¿Guardar antes de cerrar?",
    "Effacer les annotations": "Borrar anotaciones",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "¿Eliminar {n} anotación/es seleccionada/s?",
    "Image PDF": "Imagen PDF",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Imagen detectada: « {name} »\n¿Qué desea hacer?",
    "Supprimer": "Eliminar",
    "Remplacer…": "Reemplazar…",
    "Choisir une image à insérer": "Elegir una imagen para insertar",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Elegir imagen de reemplazo",
    "Impossible de lire l'image :\n{err}": "No se puede leer la imagen:\n{err}",
    "Exporter le texte": "Exportar texto",
    "Texte (*.txt)": "Texto (*.txt)",
    "{n} image(s) extraite(s).": "{n} imagen/es extraída/s.",
    "Dossier de sortie": "Carpeta de salida",
    "Succès": "Éxito",
    "Protection": "Protección",
    "Mot de passe :": "Contraseña:",
    "Déverrouillage": "Desbloquear",
    "Mot de passe requis": "Contraseña requerida",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "Este documento está protegido. Ingrese la contraseña para editarlo:",
    "Mot de passe incorrect.": "Contraseña incorrecta.",
    "Signatures": "Firmas",
    "Aucune signature trouvée.": "No se encontraron firmas.",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "El documento tiene cambios sin guardar. ¿Salir de todas formas?",
    "Annuler : {desc}": "Deshacer: {desc}",
    "Rétablir : {desc}": "Rehacer: {desc}",

    # ── Menú de idioma ─────────────────────────────────────────────────────
    "Appliquer la langue": "Aplicar idioma",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "¿Reiniciar para aplicar el idioma « {lang} »?",
    "La langue sera appliquée au prochain démarrage.":
        "El idioma se aplicará en el próximo inicio.",

    # ── Ayuda — pfx ────────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Obtener un certificado de firma .pfx",
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
        "<b>Certificado de firma digital (.pfx / .p12)</b><br><br>"
        "Para que la firma sea verificable por terceros, necesita un certificado "
        "emitido por una <b>Autoridad de Certificación (CA) reconocida</b>.<br><br>"
        "<b>Proveedores comunes:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Costo:</b> 50 – 200 €/año según el nivel de validación.<br>"
        "El proveedor entrega directamente un archivo <b>.pfx</b> (o .p12) "
        "protegido por contraseña.<br><br>"
        "<i>Solo para uso interno, puede generar un certificado autofirmado "
        "con OpenSSL:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),
    "À propos de PDF Editor": "Acerca de PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Versión 1.0.0<br><br>"
        "Editor de PDF gratuito de código abierto.<br>"
        "Stack: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licencia: MIT"
    ),

    # ── Panel de búsqueda ──────────────────────────────────────────────────
    "Rechercher dans le document :": "Buscar en el documento:",
    "Terme de recherche…": "Término de búsqueda…",
    "Chercher": "Buscar",
    "Respecter la casse": "Distinguir mayúsculas",
    "Recherche en cours…": "Buscando…",
    "Aucun résultat.": "Sin resultados.",
    "{n} occurrence(s) trouvée(s).": "{n} coincidencia(s) encontrada(s).",
    "Erreur : {err}": "Error: {err}",

    # ── Panel OCR ──────────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR no está instalado.\n\n"
        "Descárguelo aquí:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Luego reinicie la aplicación."
    ),
    "Langue :": "Idioma:",
    "Lancer l'OCR sur la page courante": "Ejecutar OCR en la página actual",
    "Texte extrait :": "Texto extraído:",
    "Copier": "Copiar",
    "Exporter .txt": "Exportar .txt",
    "Erreur OCR": "Error OCR",
    "Fichier texte (*.txt)": "Archivo de texto (*.txt)",

    # ── Diálogo de firma ───────────────────────────────────────────────────
    "Signer le document": "Firmar documento",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko no está instalado.\n"
        "Instálelo con: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Ruta al archivo .pfx / .p12",
    "Certificat (.pfx) :": "Certificado (.pfx):",
    "Raison :": "Razón:",
    "Document signé électroniquement": "Documento firmado electrónicamente",
    "Lieu :": "Lugar:",
    "Contact :": "Contacto:",
    "Page :": "Página:",
    "Sélectionner le certificat": "Seleccionar certificado",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Certificados (*.pfx *.p12);;Todos los archivos (*)",
    "Sélectionnez un fichier certificat valide.":
        "Seleccione un archivo de certificado válido.",
    "Enregistrer le PDF signé": "Guardar PDF firmado",
    "PDF signé sauvegardé :\n{path}": "PDF firmado guardado:\n{path}",

    # ── Diálogo de combinación ─────────────────────────────────────────────
    "Fusionner des PDFs": "Combinar PDFs",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "Archivos a combinar (arrastrar para reordenar):",
    "Ajouter…": "Agregar…",
    "Choisir des PDFs": "Elegir PDFs",
    "↑ Monter": "↑ Subir",
    "↓ Descendre": "↓ Bajar",
    "Attention": "Atención",
    "Ajoutez au moins 2 fichiers PDF.": "Agregue al menos 2 archivos PDF.",
    "Enregistrer le PDF fusionné": "Guardar PDF combinado",
    "PDF fusionné :\n{path}": "PDF combinado:\n{path}",

    # ── Diálogo de división ────────────────────────────────────────────────
    "Découper le PDF": "Dividir PDF",
    "Mode de découpage": "Modo de división",
    "Une page par fichier (toutes les pages)": "Una página por archivo (todas las páginas)",
    "Extraire une plage de pages :": "Extraer un rango de páginas:",
    "De": "De",
    "à": "a",
    "{n} fichiers créés dans :\n{dir}": "{n} archivos creados en:\n{dir}",
    "Enregistrer l'extrait": "Guardar extracto",
    "Extrait sauvegardé :\n{path}": "Extracto guardado:\n{path}",

    # ── Panel izquierdo — herramientas PDF (v1.2) ─────────────────────────
    "🛠  Outils PDF": "🛠  Herramientas PDF",
    "Réorganiser/Fusionner…": "Reorganizar/Combinar…",
    "Fractionner…": "Dividir…",
    "En-têtes / pieds de page…": "Encabezados / pies de página…",

    # ── Menús adicionales (v1.2) ───────────────────────────────────────────
    "Nouveau formulaire vierge…": "Nuevo formulario en blanco…",
    "Imprimer…": "Imprimir…",
    "Insérer une image…": "Insertar imagen…",
    "Insérer un bloc de texte…": "Insertar bloque de texto…",
    "Déplacer un bloc de texte": "Mover bloque de texto",
    "Réorganiser/Fusionner les pages…": "Reorganizar/Combinar páginas…",
    "Fractionner ce PDF…": "Dividir este PDF…",
    "Supprimer la page courante": "Eliminar página actual",
    "Métadonnées…": "Metadatos…",
    "En-têtes et pieds de page…": "Encabezados y pies de página…",
    "Filigrane…": "Marca de agua…",
    "Tampon texte…": "Sello de texto…",
    "Tampon image…": "Sello de imagen…",
    "Compresser le PDF": "Comprimir PDF",
    "Reconnaissance de caractères (OCR)…": "Reconocimiento de caracteres (OCR)…",
    "Rechercher…": "Buscar…",
    "Manuel utilisateur": "Manual de usuario",
    "Intégration Windows (clic droit)…": "Integración Windows (clic derecho)…",
    "Formulaire": "Formulario",

    # ── Barra Páginas & Formulario (v1.2) ──────────────────────────────────
    "Pages & Formulaire": "Páginas & Formulario",
    "⊕ Réorganiser/Fusionner": "⊕ Reorganizar/Combinar",
    "Réorganiser/Fusionner les pages…": "Reorganizar/Combinar páginas…",
    "✂ Fractionner": "✂ Dividir",
    "🗑 Suppr. page": "🗑 Elim. página",
    "Supprimer la page courante (Delete)": "Eliminar página actual (Supr)",
    "🖼 Insérer image": "🖼 Insertar imagen",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Dibuje una zona para insertar una imagen en el PDF",
    "📝 Insérer texte": "📝 Insertar texto",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Dibuje una zona para insertar un bloque de texto en el PDF",
    "✏ Mode Design": "✏ Modo Diseño",
    "Activer/désactiver le mode design de formulaire":
        "Activar/desactivar el modo de diseño de formulario",

    # ── Panel de herramientas (v1.2) ───────────────────────────────────────
    "✏  Annotations": "✏  Anotaciones",
    "Couleur :": "Color:",
    "Personnalisé": "Personalizado",
    "Épaisseur :": "Grosor:",
    "💡 Raccourcis": "💡 Atajos",
    "Double-clic → modifier texte": "Doble clic → editar texto",
    "Clic droit → menu contextuel": "Clic derecho → menú contextual",
    "H  Surligner": "H  Resaltar",
    "C  Commentaire": "C  Comentario",
    "E  Effacer": "E  Borrar",
    "M  Déplacer texte": "M  Mover texto",

    # ── Diálogo sello de texto (v1.2) ──────────────────────────────────────
    "Ajouter un tampon": "Añadir un sello",
    "APPROUVÉ": "APROBADO",
    "REJETÉ": "RECHAZADO",
    "À SIGNER": "A FIRMAR",
    "CONFIDENTIEL": "CONFIDENCIAL",
    "BROUILLON": "BORRADOR",
    "URGENT": "URGENTE",
    "COPIE": "COPIA",
    "À RÉVISER": "A REVISAR",
    "Personnalisé…": "Personalizado…",
    "Tampon :": "Sello:",
    "Votre texte…": "Su texto…",
    "Position :": "Posición:",
    "Pages :": "Páginas:",
    "Horizontal  (0°)": "Horizontal  (0°)",
    "Diagonal  (−45°)": "Diagonal  (−45°)",
    "Rotation :": "Rotación:",
    "Opacité :": "Opacidad:",
    "Appliquer": "Aplicar",
    "Aperçu :": "Vista previa:",
    "Haut-droit": "Superior derecho",
    "Haut-gauche": "Superior izquierdo",
    "Bas-droit": "Inferior derecho",
    "Bas-gauche": "Inferior izquierdo",
    "Centre": "Centro",
    "Toutes les pages": "Todas las páginas",
    "Première page": "Primera página",
    "Dernière page": "Última página",

    # ── Diálogo sello de imagen (v1.2) ─────────────────────────────────────
    "Tampon image": "Sello de imagen",
    "Bibliothèque de tampons :": "Biblioteca de sellos:",
    "Supprimer ce tampon de la bibliothèque": "Eliminar este sello de la biblioteca",
    "Taille :": "Tamaño:",
    " % largeur page": " % ancho página",
    "Choisir une image": "Elegir una imagen",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Nombre del sello",
    "Donnez un nom à ce tampon :": "Dé un nombre a este sello:",
    "Mon tampon": "Mi sello",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "¿Eliminar el sello « {n} » de la biblioteca?",

    # ── Diálogo organizar (v1.2) ───────────────────────────────────────────
    "Organiser les pages": "Organizar páginas",
    "Ajouter un document…": "Agregar documento…",
    "Monter": "Subir",
    "Descendre": "Bajar",
    "Documents supportés": "Documentos compatibles",
    "Images": "Imágenes",
    "Ajouter un document": "Agregar documento",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} página(s) en total — {orig} original(es), {removed} eliminada(s)",
    "Le document ne peut pas être vide.": "El documento no puede estar vacío.",

    # ── Diálogo encabezados/pies (v1.2) ───────────────────────────────────
    "En-têtes et pieds de page": "Encabezados y pies de página",
    "En-tête": "Encabezado",
    "Pied de page": "Pie de página",
    "Options communes": "Opciones comunes",
    "Taille de police :": "Tamaño de fuente:",
    "Marge depuis le bord :": "Margen desde el borde:",
    "Ne pas appliquer sur la 1ère page": "No aplicar en la 1.ª página",
    "Gauche": "Izquierda",
    "Droite": "Derecha",
    "En-tête gauche": "Encabezado izquierdo",

    # ── Diálogo marca de agua (v1.2) ───────────────────────────────────────
    "Ajouter un filigrane": "Añadir marca de agua",
    "Texte :": "Texto:",

    # ── Diálogo metadatos (v1.2) ───────────────────────────────────────────
    "Métadonnées du document": "Metadatos del documento",
    "Informations enregistrées dans le fichier PDF :":
        "Información guardada en el archivo PDF:",
    "Titre :": "Título:",
    "Auteur :": "Autor:",
    "Sujet :": "Asunto:",
    "Mots-clés :": "Palabras clave:",
    "Application :": "Aplicación:",

    # ── Diálogo de ayuda (v1.2) ────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "Manual de usuario — PDF Editor",
    "Rechercher :": "Buscar:",
    "Mot-clé…": "Palabra clave…",
    "Occurrence précédente": "Coincidencia anterior",
    "Occurrence suivante": "Coincidencia siguiente",
    "Fichier de documentation introuvable :\n": "Archivo de documentación no encontrado:\n",

    # ── Panel de formulario (v1.2) ─────────────────────────────────────────
    "Nouveau formulaire vierge": "Nuevo formulario en blanco",
    "✏  Mode Design — Ajouter des champs": "✏  Modo Diseño — Añadir campos",
    "Aucun formulaire détecté dans ce PDF.": "No se detectó formulario en este PDF.",
    "Enregistrer et exporter JSON": "Guardar y exportar JSON",
    "JSON embarqué :": "JSON incrustado:",
    "JSON précédemment embarqué.": "JSON previamente incrustado.",
    "Données sauvegardées.": "Datos guardados.",

    # ── Mensajes de estado (v1.2) ──────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Formulario: {n} campo(s)",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Páginas reorganizadas — recuerde guardar (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Guardar nuevo PDF",
    "Nouveau PDF créé et ouvert : {name}": "Nuevo PDF creado y abierto: {name}",
    "En-têtes/pieds de page supprimés.": "Encabezados/pies de página eliminados.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Encabezados/pies de página añadidos — recuerde guardar (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Marca de agua añadida a todas las páginas — recuerde guardar (Ctrl+S).",
    "toutes les pages": "todas las páginas",
    "la première page": "la primera página",
    "la dernière page": "la última página",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Sello « {t} » añadido en {n} — recuerde guardar (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Sello de imagen aplicado en {n} — recuerde guardar (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Metadatos actualizados — recuerde guardar (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Compresión realizada — ganancia estimada: {kb} KB. Guarde para finalizar (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "El documento ya es óptimo — no es posible ganar con la compresión.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} línea(s) OCR incrustada(s) en la página.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Texto modificado. Guarde para conservar los cambios.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Bloque movido. Guarde para conservar los cambios.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Bloque eliminado. Guarde para conservar los cambios.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Texto ocultado. Guarde para conservar los cambios.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Texto eliminado del flujo. Guarde para conservar los cambios.",
    "Impossible de supprimer ce texte du flux.":
        "No se puede eliminar este texto del flujo.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Clic derecho en un elemento para seleccionarlo, luego Supr para borrarlo.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Haga clic directamente en un bloque de texto OCR para editarlo.",
    "Champ « {name} » modifié.": "Campo « {name} » modificado.",
    "Champ « {name} » ({type}) ajouté.": "Campo « {name} » ({type}) añadido.",
    "Nom de champ vide — champ non créé.": "Nombre de campo vacío — campo no creado.",
    "Chemin d'image manquant.": "Ruta de imagen faltante.",

    # ── Cuadros de diálogo (v1.2) ──────────────────────────────────────────
    "Modifications non enregistrées": "Cambios sin guardar",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "El documento ha sido modificado. ¿Guardar antes de continuar?",
    "Ne pas enregistrer": "No guardar",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Se han realizado cambios. ¿Guardar antes de cerrar?",
    "Quitter sans enregistrer": "Salir sin guardar",
    "Redémarrer": "Reiniciar",
    "Modifier le texte…": "Editar texto…",
    "Supprimer ce bloc": "Eliminar este bloque",
    "Modifier le champ « {name} »…": "Editar campo « {name} »…",
    "Supprimer le champ « {name} »": "Eliminar campo « {name} »",
    "Modifier « {t}… »": "Editar « {t}… »",
    "Masquer (rectangle blanc)": "Ocultar (rectángulo blanco)",
    "Supprimer du flux PDF": "Eliminar del flujo PDF",
    "Déplacer / redimensionner…": "Mover / redimensionar…",
    "Nom déjà utilisé": "Nombre ya utilizado",
    "Un champ nommé « {name} » existe déjà.":
        "Ya existe un campo llamado « {name} ».",
    "Saisir le commentaire :": "Introducir comentario:",
    "Modifier le commentaire": "Editar comentario",
    "Modifier le texte": "Editar texto",
    "Remplacer l'image": "Reemplazar imagen",
    "Supprimer la page": "Eliminar página",
    "Impossible de supprimer l'unique page du document.":
        "No se puede eliminar la única página del documento.",
    "Supprimer la page {n} du document ?": "¿Eliminar la página {n} del documento?",
    "Page {n} supprimée.": "Página {n} eliminada.",

    # ── Integración Windows (v1.2) ─────────────────────────────────────────
    "Intégration Windows — clic droit": "Integración Windows — clic derecho",
    "✅ Actif": "✅ Activo",
    "❌ Inactif": "❌ Inactivo",
    "Statut :": "Estado:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "Cuando la integración está activa, al hacer clic derecho en un archivo de imagen "
        "({exts}) en el Explorador de Windows aparece la opción "
        "<b>Convertir a PDF</b>. El PDF se crea en la misma carpeta "
        "que la imagen."
    ),
    "Désactiver": "Desactivar",
    "Activer": "Activar",
    "Intégration Windows": "Integración Windows",
    "Clic droit désactivé pour les fichiers images.":
        "Clic derecho desactivado para archivos de imagen.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "¡Clic derecho activado!\n\n"
        "Haga clic derecho en cualquier imagen "
        "({exts}) en el Explorador para convertir a PDF."
    ),

    # ── Diálogo extracción de texto (v1.4) ─────────────────────────────────
    "🛠  Outils": "🛠  Herramientas",
    "Extraire le texte": "Extraer texto",
    "Toutes les pages ({n})": "Todas las páginas ({n})",
    "Page courante ({n})": "Página actual ({n})",
    "Intervalle :": "Intervalo:",
    "De la page": "De la página",
    "Extraction": "Extracción",
    "Pages {a} à {b}": "Páginas {a} a {b}",
    "Page {n}": "Página {n}",
    "Extraction réussie ✅": "Extracción exitosa ✅",
    "Extraction terminée avec succès !": "¡Extracción completada con éxito!",
    "Pages extraites :": "Páginas extraídas:",
    "Caractères :": "Caracteres:",
    "Mots :": "Palabras:",
    "Lignes :": "Líneas:",
    "Fichier :": "Archivo:",

    # ── Panel de idioma (v1.4) ─────────────────────────────────────────────
    "Choisir la langue :": "Elegir idioma:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "Es necesario reiniciar\npara aplicar el cambio.",

    # ── Panel de ayuda (v1.4) ─────────────────────────────────────────────
    "Actions rapides :": "Acciones rápidas:",
    "Raccourcis clavier :": "Atajos de teclado:",

    # ── Diálogo de licencia (v1.4) ────────────────────────────────────────
    "Activation de PDF Editor": "Activación de PDF Editor",
    "Licence…": "Licencia…",
    "Licence — PDF Editor": "Licencia — PDF Editor",
    "Clé de licence :": "Clave de licencia:",
    "Vérification…": "Verificando…",
    "Connexion à Lemon Squeezy…": "Conectando con Lemon Squeezy…",
    "Licence activée avec succès.": "Licencia activada correctamente.",
    "Licence valide.": "Licencia válida.",
    "Licence désactivée sur cet ordinateur.": "Licencia desactivada en este equipo.",
    "Désactiver cette licence": "Desactivar esta licencia",
    "Désactiver la licence": "Desactivar licencia",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "¿Eliminar la licencia de este equipo?\n\nPodrá reactivarla en otro dispositivo.",
    "Aucune licence activée sur cet ordinateur.": "No hay licencia activada en este equipo.",
    "Entrer une clé de licence": "Introducir clave de licencia",
    "Clé de licence invalide.": "Clave de licencia no válida.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "No se puede validar la licencia (sin conexión demasiado tiempo).",
    "Pas encore de licence ? ": "¿Sin licencia aún? ",
    "Acheter PDF Editor": "Comprar PDF Editor",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Introduzca su clave de licencia recibida por email tras la compra.\nFormato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Modo sin conexión — {remaining} día(s) restante(s).",
    "Licence": "Licencia",

    # ── Integración de shell — combinar (v1.4) ─────────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Convertir imagen a PDF",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Combinar archivos en PDF Editor",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "Cuando la integración está activa, una selección múltiple de archivos "
        "({exts}) en el Explorador de Windows ofrece la opción "
        "<b>Combinar en PDF Editor</b>. El diálogo de organización "
        "se abre con estos archivos precargados."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "¡Combinación activada!\n\n"
        "Seleccione varios archivos ({exts}) en el Explorador,\n"
        "haga clic derecho y elija «\u202fCombinar en PDF Editor\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Clic derecho «\u202fCombinar\u202f» desactivado.",
}
