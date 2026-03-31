"""Переводы на русский язык — ключи являются каноническими французскими строками."""

TRANSLATIONS: dict[str, str] = {
    # ── Меню ───────────────────────────────────────────────────────────────
    "Fichier": "Файл",
    "Ouvrir…": "Открыть…",
    "Fichiers récents": "Последние файлы",
    "Enregistrer": "Сохранить",
    "Enregistrer sous…": "Сохранить как…",
    "Fermer": "Закрыть",
    "Quitter": "Выйти",
    "Édition": "Правка",
    "Annuler": "Отменить",
    "Rétablir": "Повторить",
    "Affichage": "Вид",
    "Zoom +": "Увеличить",
    "Zoom -": "Уменьшить",
    "Ajuster à la page": "По странице",
    "Ajuster à la largeur": "По ширине",
    "Afficher/masquer le panneau Pages": "Показать/скрыть панель страниц",
    "Afficher/masquer les outils": "Показать/скрыть инструменты",
    "Thème sombre": "Тёмная тема",
    "Thème clair": "Светлая тема",
    "Langue": "Язык",
    "Outils": "Инструменты",
    "Fusionner des PDFs…": "Объединить PDF…",
    "Découper ce PDF…": "Разделить PDF…",
    "Extraire le texte…": "Извлечь текст…",
    "Extraire les images…": "Извлечь изображения…",
    "Protéger par mot de passe…": "Защитить паролем…",
    "Supprimer la protection…": "Снять защиту…",
    "Tourner la page (+90°)": "Повернуть страницу (+90°)",
    "Tourner la page (-90°)": "Повернуть страницу (-90°)",
    "Signature": "Подпись",
    "Signer le document…": "Подписать документ…",
    "Vérifier les signatures…": "Проверить подписи…",
    "Aide": "Справка",
    "À propos": "О программе",
    "Comment obtenir un certificat .pfx ?": "Как получить сертификат .pfx?",

    # ── Панель инструментов ────────────────────────────────────────────────
    "Barre principale": "Главная панель",
    "Ouvrir": "Открыть",
    "Ouvrir un fichier PDF": "Открыть PDF файл",
    "Enr. sous…": "Сохр. как…",
    "◀ Préc.": "◀ Пред.",
    "Suiv. ▶": "След. ▶",
    "Ajuster page": "По стр.",
    "Ajuster largeur": "По шир.",
    "Annotations": "Аннотации",
    "Sélection": "Выделение",
    "Modifier texte": "Ред. текст",
    "Surligner": "Выделить",
    "Souligner": "Подчеркнуть",
    "Commentaire": "Комментарий",
    "Image": "Изображение",
    "Effacer": "Стереть",

    # ── Панели / вкладки ───────────────────────────────────────────────────
    "Pages": "Страницы",
    "Recherche": "Поиск",
    "OCR": "OCR",

    # ── Строка состояния ───────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Добро пожаловать в PDF Editor. Откройте файл для начала работы.",
    "Ouvert : {name}": "Открыт: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [только чтение — требуется пароль владельца для редактирования]",
    "Fichier enregistré.": "Файл сохранён.",
    "Enregistré sous : {path}": "Сохранён как: {path}",
    "Document fermé.": "Документ закрыт.",
    "Page {page} / {total}": "Страница {page} / {total}",
    "Texte copié : « {snippet} »": "Текст скопирован: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "Текст в выделенной области не найден.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Измените размер / переместите изображение, затем нажмите ✓ Подтвердить.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Измените размер изображения, затем нажмите ✓ Подтвердить.",
    "Image supprimée.": "Изображение удалено.",
    "Image remplacée.": "Изображение заменено.",
    "Aucune annotation dans la sélection.": "Нет аннотаций в выделении.",
    "{n} annotation(s) effacée(s).": "{n} аннотация(й) удалена(о).",
    "Annulé : {desc}": "Отменено: {desc}",
    "Rétabli : {desc}": "Повторено: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Текст изменён на месте ({method}). Сохраните для сохранения изменений.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Текст изменён (наложение). Сохраните для сохранения изменений.",
    "Rendu non rafraîchi : {err}": "Вид не обновлён: {err}",
    "Édition en place échouée : {err}": "Редактирование на месте не удалось: {err}",
    "Texte exporté : {path}": "Текст экспортирован: {path}",
    "PDF protégé enregistré.": "Защищённый PDF сохранён.",
    "PDF déprotégé enregistré.": "Незащищённый PDF сохранён.",
    "Document déverrouillé — modifications autorisées.":
        "Документ разблокирован — редактирование разрешено.",
    "  Gras": "  Жирный",
    "  Italique": "  Курсив",

    # ── Диалоги ────────────────────────────────────────────────────────────
    "Ouvrir un PDF": "Открыть PDF",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;Все файлы (*)",
    "Fichier protégé": "Защищённый файл",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "Этот файл зашифрован. Введите пароль для открытия:",
    "Erreur": "Ошибка",
    "Impossible d'ouvrir le fichier :\n{err}": "Невозможно открыть файл:\n{err}",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "Документ был изменён. Сохранить перед закрытием?",
    "Effacer les annotations": "Стереть аннотации",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "Удалить {n} выбранную(ые) аннотацию(и)?",
    "Image PDF": "Изображение PDF",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Изображение обнаружено: « {name} »\nЧто вы хотите сделать?",
    "Supprimer": "Удалить",
    "Remplacer…": "Заменить…",
    "Choisir une image à insérer": "Выбрать изображение для вставки",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Изображения (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Выбрать изображение для замены",
    "Impossible de lire l'image :\n{err}": "Невозможно прочитать изображение:\n{err}",
    "Exporter le texte": "Экспортировать текст",
    "Texte (*.txt)": "Текст (*.txt)",
    "{n} image(s) extraite(s).": "{n} изображение(й) извлечено.",
    "Dossier de sortie": "Папка вывода",
    "Succès": "Успех",
    "Protection": "Защита",
    "Mot de passe :": "Пароль:",
    "Déverrouillage": "Разблокировка",
    "Mot de passe requis": "Требуется пароль",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "Этот документ защищён. Введите пароль для редактирования:",
    "Mot de passe incorrect.": "Неверный пароль.",
    "Signatures": "Подписи",
    "Aucune signature trouvée.": "Подписи не найдены.",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "В документе есть несохранённые изменения. Всё равно выйти?",
    "Annuler : {desc}": "Отмена: {desc}",
    "Rétablir : {desc}": "Повтор: {desc}",

    # ── Меню языка ─────────────────────────────────────────────────────────
    "Appliquer la langue": "Применить язык",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "Перезапустить для применения языка « {lang} »?",
    "La langue sera appliquée au prochain démarrage.":
        "Язык будет применён при следующем запуске.",

    # ── Справка — pfx ──────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Получить сертификат подписи .pfx",
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
        "<b>Сертификат цифровой подписи (.pfx / .p12)</b><br><br>"
        "Чтобы подпись можно было проверить третьими лицами, необходим сертификат, "
        "выданный <b>признанным Центром сертификации (CA)</b>.<br><br>"
        "<b>Распространённые провайдеры:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Стоимость:</b> 50 – 200 €/год в зависимости от уровня проверки.<br>"
        "Провайдер доставляет файл <b>.pfx</b> (или .p12), "
        "защищённый паролем.<br><br>"
        "<i>Только для внутреннего использования можно создать самоподписанный "
        "сертификат с помощью OpenSSL:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),
    "À propos de PDF Editor": "О программе PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Версия 1.0.0<br><br>"
        "Бесплатный редактор PDF с открытым исходным кодом.<br>"
        "Стек: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Лицензия: MIT"
    ),

    # ── Панель поиска ──────────────────────────────────────────────────────
    "Rechercher dans le document :": "Поиск в документе:",
    "Terme de recherche…": "Поисковый запрос…",
    "Chercher": "Найти",
    "Respecter la casse": "С учётом регистра",
    "Recherche en cours…": "Поиск…",
    "Aucun résultat.": "Нет результатов.",
    "{n} occurrence(s) trouvée(s).": "Найдено совпадений: {n}.",
    "Erreur : {err}": "Ошибка: {err}",

    # ── Панель OCR ─────────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR не установлен.\n\n"
        "Скачайте его здесь:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Затем перезапустите приложение."
    ),
    "Langue :": "Язык:",
    "Lancer l'OCR sur la page courante": "Запустить OCR на текущей странице",
    "Texte extrait :": "Извлечённый текст:",
    "Copier": "Копировать",
    "Exporter .txt": "Экспорт .txt",
    "Erreur OCR": "Ошибка OCR",
    "Fichier texte (*.txt)": "Текстовый файл (*.txt)",

    # ── Диалог подписи ─────────────────────────────────────────────────────
    "Signer le document": "Подписать документ",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko не установлен.\n"
        "Установите: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Путь к файлу .pfx / .p12",
    "Certificat (.pfx) :": "Сертификат (.pfx):",
    "Raison :": "Причина:",
    "Document signé électroniquement": "Документ подписан электронно",
    "Lieu :": "Место:",
    "Contact :": "Контакт:",
    "Page :": "Страница:",
    "Sélectionner le certificat": "Выбрать сертификат",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Сертификаты (*.pfx *.p12);;Все файлы (*)",
    "Sélectionnez un fichier certificat valide.":
        "Выберите действительный файл сертификата.",
    "Enregistrer le PDF signé": "Сохранить подписанный PDF",
    "PDF signé sauvegardé :\n{path}": "Подписанный PDF сохранён:\n{path}",

    # ── Диалог объединения ─────────────────────────────────────────────────
    "Fusionner des PDFs": "Объединить PDF",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "Файлы для объединения (перетащите для изменения порядка):",
    "Ajouter…": "Добавить…",
    "Choisir des PDFs": "Выбрать PDF файлы",
    "↑ Monter": "↑ Вверх",
    "↓ Descendre": "↓ Вниз",
    "Attention": "Внимание",
    "Ajoutez au moins 2 fichiers PDF.": "Добавьте не менее 2 PDF файлов.",
    "Enregistrer le PDF fusionné": "Сохранить объединённый PDF",
    "PDF fusionné :\n{path}": "PDF объединён:\n{path}",

    # ── Диалог разделения ──────────────────────────────────────────────────
    "Découper le PDF": "Разделить PDF",
    "Mode de découpage": "Режим разделения",
    "Une page par fichier (toutes les pages)": "По одной странице (все страницы)",
    "Extraire une plage de pages :": "Извлечь диапазон страниц:",
    "De": "С",
    "à": "по",
    "{n} fichiers créés dans :\n{dir}": "Создано файлов {n} в:\n{dir}",
    "Enregistrer l'extrait": "Сохранить извлечённое",
    "Extrait sauvegardé :\n{path}": "Извлечённое сохранено:\n{path}",

    # ── Левая панель — инструменты PDF (v1.2) ─────────────────────────────
    "🛠  Outils PDF": "🛠  Инструменты PDF",
    "Réorganiser/Fusionner…": "Реорганизовать/объединить…",
    "Fractionner…": "Разделить…",
    "En-têtes / pieds de page…": "Верхние / нижние колонтитулы…",

    # ── Дополнительные меню (v1.2) ─────────────────────────────────────────
    "Nouveau formulaire vierge…": "Новая пустая форма…",
    "Imprimer…": "Печать…",
    "Insérer une image…": "Вставить изображение…",
    "Insérer un bloc de texte…": "Вставить текстовый блок…",
    "Déplacer un bloc de texte": "Переместить текстовый блок",
    "Réorganiser/Fusionner les pages…": "Реорганизовать/объединить страницы…",
    "Fractionner ce PDF…": "Разделить этот PDF…",
    "Supprimer la page courante": "Удалить текущую страницу",
    "Métadonnées…": "Метаданные…",
    "En-têtes et pieds de page…": "Верхние и нижние колонтитулы…",
    "Filigrane…": "Водяной знак…",
    "Tampon texte…": "Текстовый штамп…",
    "Tampon image…": "Графический штамп…",
    "Compresser le PDF": "Сжать PDF",
    "Reconnaissance de caractères (OCR)…": "Распознавание символов (OCR)…",
    "Rechercher…": "Поиск…",
    "Manuel utilisateur": "Руководство пользователя",
    "Intégration Windows (clic droit)…": "Интеграция Windows (правый клик)…",
    "Formulaire": "Форма",

    # ── Панель Страницы & Форма (v1.2) ────────────────────────────────────
    "Pages & Formulaire": "Страницы & Форма",
    "⊕ Réorganiser/Fusionner": "⊕ Реорганизовать/объединить",
    "Réorganiser/Fusionner les pages…": "Реорганизовать/объединить страницы…",
    "✂ Fractionner": "✂ Разделить",
    "🗑 Suppr. page": "🗑 Удал. стр.",
    "Supprimer la page courante (Delete)": "Удалить текущую страницу (Del)",
    "🖼 Insérer image": "🖼 Вставить изображение",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Нарисуйте область для вставки изображения в PDF",
    "📝 Insérer texte": "📝 Вставить текст",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Нарисуйте область для вставки текстового блока в PDF",
    "✏ Mode Design": "✏ Режим дизайна",
    "Activer/désactiver le mode design de formulaire":
        "Включить/выключить режим дизайна формы",

    # ── Панель инструментов (v1.2) ─────────────────────────────────────────
    "✏  Annotations": "✏  Аннотации",
    "Couleur :": "Цвет:",
    "Personnalisé": "Пользовательский",
    "Épaisseur :": "Толщина:",
    "💡 Raccourcis": "💡 Горячие клавиши",
    "Double-clic → modifier texte": "Двойной клик → редактировать текст",
    "Clic droit → menu contextuel": "Правый клик → контекстное меню",
    "H  Surligner": "H  Выделить",
    "C  Commentaire": "C  Комментарий",
    "E  Effacer": "E  Стереть",
    "M  Déplacer texte": "M  Переместить текст",

    # ── Диалог текстового штампа (v1.2) ────────────────────────────────────
    "Ajouter un tampon": "Добавить штамп",
    "APPROUVÉ": "ОДОБРЕНО",
    "REJETÉ": "ОТКЛОНЕНО",
    "À SIGNER": "НА ПОДПИСЬ",
    "CONFIDENTIEL": "КОНФИДЕНЦИАЛЬНО",
    "BROUILLON": "ЧЕРНОВИК",
    "URGENT": "СРОЧНО",
    "COPIE": "КОПИЯ",
    "À RÉVISER": "НА ДОРАБОТКУ",
    "Personnalisé…": "Произвольный…",
    "Tampon :": "Штамп:",
    "Votre texte…": "Ваш текст…",
    "Position :": "Позиция:",
    "Pages :": "Страницы:",
    "Horizontal  (0°)": "Горизонтально  (0°)",
    "Diagonal  (−45°)": "По диагонали  (−45°)",
    "Rotation :": "Поворот:",
    "Opacité :": "Прозрачность:",
    "Appliquer": "Применить",
    "Aperçu :": "Предпросмотр:",
    "Haut-droit": "Вверху справа",
    "Haut-gauche": "Вверху слева",
    "Bas-droit": "Внизу справа",
    "Bas-gauche": "Внизу слева",
    "Centre": "По центру",
    "Toutes les pages": "Все страницы",
    "Première page": "Первая страница",
    "Dernière page": "Последняя страница",

    # ── Диалог графического штампа (v1.2) ─────────────────────────────────
    "Tampon image": "Графический штамп",
    "Bibliothèque de tampons :": "Библиотека штампов:",
    "Supprimer ce tampon de la bibliothèque": "Удалить этот штамп из библиотеки",
    "Taille :": "Размер:",
    " % largeur page": " % ширины страницы",
    "Choisir une image": "Выбрать изображение",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Изображения (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Название штампа",
    "Donnez un nom à ce tampon :": "Дайте название этому штампу:",
    "Mon tampon": "Мой штамп",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "Удалить штамп « {n} » из библиотеки?",

    # ── Диалог организации страниц (v1.2) ─────────────────────────────────
    "Organiser les pages": "Организовать страницы",
    "Ajouter un document…": "Добавить документ…",
    "Monter": "Вверх",
    "Descendre": "Вниз",
    "Documents supportés": "Поддерживаемые документы",
    "Images": "Изображения",
    "Ajouter un document": "Добавить документ",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} страниц(а) всего — {orig} оригинальных, {removed} удалено",
    "Le document ne peut pas être vide.": "Документ не может быть пустым.",

    # ── Диалог колонтитулов (v1.2) ────────────────────────────────────────
    "En-têtes et pieds de page": "Верхние и нижние колонтитулы",
    "En-tête": "Верхний колонтитул",
    "Pied de page": "Нижний колонтитул",
    "Options communes": "Общие параметры",
    "Taille de police :": "Размер шрифта:",
    "Marge depuis le bord :": "Отступ от края:",
    "Ne pas appliquer sur la 1ère page": "Не применять на 1-й странице",
    "Gauche": "Слева",
    "Droite": "Справа",
    "En-tête gauche": "Левый верхний колонтитул",

    # ── Диалог водяного знака (v1.2) ──────────────────────────────────────
    "Ajouter un filigrane": "Добавить водяной знак",
    "Texte :": "Текст:",

    # ── Диалог метаданных (v1.2) ───────────────────────────────────────────
    "Métadonnées du document": "Метаданные документа",
    "Informations enregistrées dans le fichier PDF :":
        "Информация, сохранённая в файле PDF:",
    "Titre :": "Заголовок:",
    "Auteur :": "Автор:",
    "Sujet :": "Тема:",
    "Mots-clés :": "Ключевые слова:",
    "Application :": "Приложение:",

    # ── Диалог справки (v1.2) ─────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "Руководство пользователя — PDF Editor",
    "Rechercher :": "Поиск:",
    "Mot-clé…": "Ключевое слово…",
    "Occurrence précédente": "Предыдущее совпадение",
    "Occurrence suivante": "Следующее совпадение",
    "Fichier de documentation introuvable :\n": "Файл документации не найден:\n",

    # ── Панель формы (v1.2) ────────────────────────────────────────────────
    "Nouveau formulaire vierge": "Новая пустая форма",
    "✏  Mode Design — Ajouter des champs": "✏  Режим дизайна — Добавить поля",
    "Aucun formulaire détecté dans ce PDF.": "Форма в этом PDF не обнаружена.",
    "Enregistrer et exporter JSON": "Сохранить и экспортировать JSON",
    "JSON embarqué :": "Встроенный JSON:",
    "JSON précédemment embarqué.": "Ранее встроенный JSON.",
    "Données sauvegardées.": "Данные сохранены.",

    # ── Строка состояния (v1.2) ────────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Форма: {n} поле(й)",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Страницы реорганизованы — не забудьте сохранить (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Сохранить новый PDF",
    "Nouveau PDF créé et ouvert : {name}": "Новый PDF создан и открыт: {name}",
    "En-têtes/pieds de page supprimés.": "Колонтитулы удалены.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Колонтитулы добавлены — не забудьте сохранить (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Водяной знак добавлен на все страницы — не забудьте сохранить (Ctrl+S).",
    "toutes les pages": "все страницы",
    "la première page": "первую страницу",
    "la dernière page": "последнюю страницу",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Штамп « {t} » добавлен на {n} — не забудьте сохранить (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Графический штамп применён на {n} — не забудьте сохранить (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Метаданные обновлены — не забудьте сохранить (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Сжатие выполнено — ожидаемый выигрыш: {kb} КБ. Сохраните для завершения (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "Документ уже оптимален — сжатие невозможно.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} строк(а) OCR встроено на странице.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Текст изменён. Сохраните для применения изменений.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Блок перемещён. Сохраните для применения изменений.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Блок удалён. Сохраните для применения изменений.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Текст скрыт. Сохраните для применения изменений.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Текст удалён из потока. Сохраните для применения изменений.",
    "Impossible de supprimer ce texte du flux.":
        "Невозможно удалить этот текст из потока.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Щёлкните правой кнопкой по элементу для выбора, затем Del для удаления.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Щёлкните прямо по блоку текста OCR, чтобы его редактировать.",
    "Champ « {name} » modifié.": "Поле « {name} » изменено.",
    "Champ « {name} » ({type}) ajouté.": "Поле « {name} » ({type}) добавлено.",
    "Nom de champ vide — champ non créé.": "Имя поля пустое — поле не создано.",
    "Chemin d'image manquant.": "Путь к изображению отсутствует.",

    # ── Диалоговые окна (v1.2) ─────────────────────────────────────────────
    "Modifications non enregistrées": "Несохранённые изменения",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "Документ изменён. Сохранить перед продолжением?",
    "Ne pas enregistrer": "Не сохранять",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Внесены изменения. Сохранить перед закрытием?",
    "Quitter sans enregistrer": "Выйти без сохранения",
    "Redémarrer": "Перезапустить",
    "Modifier le texte…": "Редактировать текст…",
    "Supprimer ce bloc": "Удалить этот блок",
    "Modifier le champ « {name} »…": "Редактировать поле « {name} »…",
    "Supprimer le champ « {name} »": "Удалить поле « {name} »",
    "Modifier « {t}… »": "Редактировать « {t}… »",
    "Masquer (rectangle blanc)": "Скрыть (белый прямоугольник)",
    "Supprimer du flux PDF": "Удалить из потока PDF",
    "Déplacer / redimensionner…": "Переместить / изменить размер…",
    "Nom déjà utilisé": "Имя уже используется",
    "Un champ nommé « {name} » existe déjà.":
        "Поле с именем « {name} » уже существует.",
    "Saisir le commentaire :": "Введите комментарий:",
    "Modifier le commentaire": "Редактировать комментарий",
    "Modifier le texte": "Редактировать текст",
    "Remplacer l'image": "Заменить изображение",
    "Supprimer la page": "Удалить страницу",
    "Impossible de supprimer l'unique page du document.":
        "Невозможно удалить единственную страницу документа.",
    "Supprimer la page {n} du document ?": "Удалить страницу {n} из документа?",
    "Page {n} supprimée.": "Страница {n} удалена.",

    # ── Интеграция Windows (v1.2) ──────────────────────────────────────────
    "Intégration Windows — clic droit": "Интеграция Windows — правый клик",
    "✅ Actif": "✅ Активна",
    "❌ Inactif": "❌ Неактивна",
    "Statut :": "Статус:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "Когда интеграция активна, щелчок правой кнопкой по файлу изображения "
        "({exts}) в Проводнике Windows предлагает опцию "
        "<b>Преобразовать в PDF</b>. PDF создаётся в той же папке, "
        "что и изображение."
    ),
    "Désactiver": "Отключить",
    "Activer": "Включить",
    "Intégration Windows": "Интеграция Windows",
    "Clic droit désactivé pour les fichiers images.":
        "Правый клик для файлов изображений отключён.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "Правый клик активирован!\n\n"
        "Щёлкните правой кнопкой по любому изображению "
        "({exts}) в Проводнике для преобразования в PDF."
    ),

    # ── Диалог извлечения текста (v1.4) ────────────────────────────────────
    "🛠  Outils": "🛠  Инструменты",
    "Extraire le texte": "Извлечь текст",
    "Toutes les pages ({n})": "Все страницы ({n})",
    "Page courante ({n})": "Текущая страница ({n})",
    "Intervalle :": "Диапазон:",
    "De la page": "Со страницы",
    "Extraction": "Извлечение",
    "Pages {a} à {b}": "Страницы {a}–{b}",
    "Page {n}": "Страница {n}",
    "Extraction réussie ✅": "Извлечение выполнено ✅",
    "Extraction terminée avec succès !": "Извлечение успешно завершено!",
    "Pages extraites :": "Извлечённые страницы:",
    "Caractères :": "Символы:",
    "Mots :": "Слова:",
    "Lignes :": "Строки:",
    "Fichier :": "Файл:",

    # ── Панель языка (v1.4) ────────────────────────────────────────────────
    "Choisir la langue :": "Выбрать язык:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "Для применения изменений\nнеобходим перезапуск.",

    # ── Панель справки (v1.4) ─────────────────────────────────────────────
    "Actions rapides :": "Быстрые действия:",
    "Raccourcis clavier :": "Горячие клавиши:",

    # ── Диалог лицензии (v1.4) ────────────────────────────────────────────
    "Activation de PDF Editor": "Активация PDF Editor",
    "Licence…": "Лицензия…",
    "Licence — PDF Editor": "Лицензия — PDF Editor",
    "Clé de licence :": "Ключ лицензии:",
    "Vérification…": "Проверка…",
    "Connexion à Lemon Squeezy…": "Подключение к Lemon Squeezy…",
    "Licence activée avec succès.": "Лицензия успешно активирована.",
    "Licence valide.": "Лицензия действительна.",
    "Licence désactivée sur cet ordinateur.": "Лицензия деактивирована на этом компьютере.",
    "Désactiver cette licence": "Деактивировать лицензию",
    "Désactiver la licence": "Деактивировать лицензию",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "Удалить лицензию с этого компьютера?\n\nВы сможете активировать её на другом устройстве.",
    "Aucune licence activée sur cet ordinateur.": "На этом компьютере нет активированной лицензии.",
    "Entrer une clé de licence": "Ввести ключ лицензии",
    "Clé de licence invalide.": "Недействительный ключ лицензии.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "Не удаётся проверить лицензию (слишком долго без подключения).",
    "Pas encore de licence ? ": "Нет лицензии? ",
    "Acheter PDF Editor": "Купить PDF Editor",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Введите ключ лицензии, полученный по электронной почте после покупки.\nФормат: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Автономный режим — осталось {remaining} дн.",
    "Licence": "Лицензия",

    # ── Интеграция оболочки — объединение (v1.4) ───────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Преобразовать изображение в PDF",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Объединить файлы в PDF Editor",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "Когда интеграция активна, выбор нескольких файлов "
        "({exts}) в Проводнике Windows предлагает опцию "
        "<b>Объединить в PDF Editor</b>. Диалог организации "
        "открывается с предзагруженными файлами."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "Объединение активировано!\n\n"
        "Выберите несколько файлов ({exts}) в Проводнике,\n"
        "щёлкните правой кнопкой и выберите «\u202fОбъединить в PDF Editor\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Правый клик «\u202fОбъединить\u202f» отключён.",
}
