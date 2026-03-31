"""Traduções para português — as chaves são as cadeias canônicas em francês."""

TRANSLATIONS: dict[str, str] = {
    # ── Menus ──────────────────────────────────────────────────────────────
    "Fichier": "Ficheiro",
    "Ouvrir…": "Abrir…",
    "Fichiers récents": "Ficheiros recentes",
    "Enregistrer": "Guardar",
    "Enregistrer sous…": "Guardar como…",
    "Fermer": "Fechar",
    "Quitter": "Sair",
    "Édition": "Edição",
    "Annuler": "Desfazer",
    "Rétablir": "Refazer",
    "Affichage": "Ver",
    "Zoom +": "Ampliar",
    "Zoom -": "Reduzir",
    "Ajuster à la page": "Ajustar à página",
    "Ajuster à la largeur": "Ajustar à largura",
    "Afficher/masquer le panneau Pages": "Mostrar/ocultar painel de páginas",
    "Afficher/masquer les outils": "Mostrar/ocultar ferramentas",
    "Thème sombre": "Tema escuro",
    "Thème clair": "Tema claro",
    "Langue": "Idioma",
    "Outils": "Ferramentas",
    "Fusionner des PDFs…": "Juntar PDFs…",
    "Découper ce PDF…": "Dividir este PDF…",
    "Extraire le texte…": "Extrair texto…",
    "Extraire les images…": "Extrair imagens…",
    "Protéger par mot de passe…": "Proteger com senha…",
    "Supprimer la protection…": "Remover proteção…",
    "Tourner la page (+90°)": "Rodar página (+90°)",
    "Tourner la page (-90°)": "Rodar página (-90°)",
    "Signature": "Assinatura",
    "Signer le document…": "Assinar documento…",
    "Vérifier les signatures…": "Verificar assinaturas…",
    "Aide": "Ajuda",
    "À propos": "Sobre",
    "Comment obtenir un certificat .pfx ?": "Como obter um certificado .pfx?",

    # ── Barra principal ────────────────────────────────────────────────────
    "Barre principale": "Barra principal",
    "Ouvrir": "Abrir",
    "Ouvrir un fichier PDF": "Abrir um ficheiro PDF",
    "Enr. sous…": "Guard. como…",
    "◀ Préc.": "◀ Ant.",
    "Suiv. ▶": "Próx. ▶",
    "Ajuster page": "Ajustar pág.",
    "Ajuster largeur": "Ajustar larg.",

    # ── Barra de anotações ─────────────────────────────────────────────────
    "Annotations": "Anotações",
    "Sélection": "Seleção",
    "Modifier texte": "Editar texto",
    "Surligner": "Realçar",
    "Souligner": "Sublinhar",
    "Commentaire": "Comentário",
    "Image": "Imagem",
    "Effacer": "Apagar",

    # ── Painéis / separadores ──────────────────────────────────────────────
    "Pages": "Páginas",
    "Recherche": "Pesquisa",
    "OCR": "OCR",

    # ── Barra de estado ────────────────────────────────────────────────────
    "Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer.":
        "Bem-vindo ao PDF Editor. Abra um ficheiro para começar.",
    "Ouvert : {name}": "Aberto: {name}",
    "  [lecture seule — mot de passe requis pour modifier]":
        "  [só leitura — palavra-passe de proprietário necessária para editar]",
    "Fichier enregistré.": "Ficheiro guardado.",
    "Enregistré sous : {path}": "Guardado como: {path}",
    "Document fermé.": "Documento fechado.",
    "Page {page} / {total}": "Página {page} / {total}",
    "Texte copié : « {snippet} »": "Texto copiado: « {snippet} »",
    "Aucun texte trouvé dans la sélection.": "Nenhum texto encontrado na seleção.",
    "Redimensionnez / déplacez l'image puis cliquez ✓ Valider.":
        "Redimensione / mova a imagem e clique em ✓ Confirmar.",
    "Redimensionnez l'image puis cliquez ✓ Valider.":
        "Redimensione a imagem e clique em ✓ Confirmar.",
    "Image supprimée.": "Imagem eliminada.",
    "Image remplacée.": "Imagem substituída.",
    "Aucune annotation dans la sélection.": "Nenhuma anotação na seleção.",
    "{n} annotation(s) effacée(s).": "{n} anotação(ões) apagada(s).",
    "Annulé : {desc}": "Desfeito: {desc}",
    "Rétabli : {desc}": "Refeito: {desc}",
    "Texte modifié en place ({method}). Enregistrez pour sauvegarder.":
        "Texto editado diretamente ({method}). Guarde para conservar as alterações.",
    "Texte modifié (overlay). Enregistrez pour sauvegarder.":
        "Texto editado (sobreposição). Guarde para conservar as alterações.",
    "Rendu non rafraîchi : {err}": "Vista não atualizada: {err}",
    "Édition en place échouée : {err}": "Edição direta falhou: {err}",
    "Texte exporté : {path}": "Texto exportado: {path}",
    "PDF protégé enregistré.": "PDF protegido guardado.",
    "PDF déprotégé enregistré.": "PDF desprotegido guardado.",
    "Document déverrouillé — modifications autorisées.":
        "Documento desbloqueado — edição permitida.",
    "Police : {info}": "Tipo de letra: {info}",
    "  Gras": "  Negrito",
    "  Italique": "  Itálico",
    "  Couleur : {color}": "  Cor: {color}",

    # ── Diálogos ───────────────────────────────────────────────────────────
    "Ouvrir un PDF": "Abrir um PDF",
    "PDF (*.pdf);;Tous les fichiers (*)": "PDF (*.pdf);;Todos os ficheiros (*)",
    "Fichier protégé": "Ficheiro protegido",
    "Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :":
        "Este ficheiro está encriptado. Introduza a palavra-passe para o abrir:",
    "Erreur": "Erro",
    "Impossible d'ouvrir le fichier :\n{err}": "Impossível abrir o ficheiro:\n{err}",
    "Enregistrer sous…": "Guardar como…",
    "PDF (*.pdf)": "PDF (*.pdf)",
    "Le document a été modifié. Enregistrer avant de fermer ?":
        "O documento foi modificado. Guardar antes de fechar?",
    "Effacer les annotations": "Apagar anotações",
    "Supprimer {n} annotation(s) sélectionnée(s) ?":
        "Eliminar {n} anotação(ões) selecionada(s)?",
    "Image PDF": "Imagem PDF",
    "Image détectée : « {name} »\nQue souhaitez-vous faire ?":
        "Imagem detetada: « {name} »\nO que pretende fazer?",
    "Supprimer": "Eliminar",
    "Remplacer…": "Substituir…",
    "Annuler": "Cancelar",
    "Choisir une image à insérer": "Escolher imagem para inserir",
    "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)":
        "Imagens (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)",
    "Choisir une image de remplacement": "Escolher imagem de substituição",
    "Impossible de lire l'image :\n{err}": "Impossível ler a imagem:\n{err}",
    "Exporter le texte": "Exportar texto",
    "Texte (*.txt)": "Texto (*.txt)",
    "{n} image(s) extraite(s).": "{n} imagem(ns) extraída(s).",
    "Dossier de sortie": "Pasta de saída",
    "Succès": "Sucesso",
    "Protection": "Proteção",
    "Mot de passe :": "Palavra-passe:",
    "Déverrouillage": "Desbloquear",
    "Mot de passe requis": "Palavra-passe necessária",
    "Ce document est protégé. Entrez le mot de passe pour le modifier :":
        "Este documento está protegido. Introduza a palavra-passe para editá-lo:",
    "Mot de passe incorrect.": "Palavra-passe incorreta.",
    "Signatures": "Assinaturas",
    "Aucune signature trouvée.": "Nenhuma assinatura encontrada.",
    "Le document a des modifications non enregistrées. Quitter quand même ?":
        "O documento tem alterações não guardadas. Sair mesmo assim?",
    "Annuler : {desc}": "Desfazer: {desc}",
    "Rétablir : {desc}": "Refazer: {desc}",

    # ── Menu de idioma ─────────────────────────────────────────────────────
    "Appliquer la langue": "Aplicar idioma",
    "Redémarrer pour appliquer la langue « {lang} » ?":
        "Reiniciar para aplicar o idioma « {lang} »?",
    "La langue sera appliquée au prochain démarrage.":
        "O idioma será aplicado no próximo arranque.",

    # ── Ajuda — pfx ────────────────────────────────────────────────────────
    "Obtenir un certificat de signature .pfx":
        "Obter um certificado de assinatura .pfx",
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
        "<b>Certificado de assinatura digital (.pfx / .p12)</b><br><br>"
        "Para que a assinatura seja verificável por terceiros, é necessário um "
        "certificado emitido por uma <b>Autoridade de Certificação (CA) reconhecida</b>.<br><br>"
        "<b>Fornecedores comuns:</b><br>"
        "• <b>Certum</b> (Asseco) — certum.eu<br>"
        "• <b>Sectigo</b> — sectigo.com<br>"
        "• <b>GlobalSign</b> — globalsign.com<br>"
        "• <b>DigiCert</b> — digicert.com<br><br>"
        "<b>Custo:</b> 50 – 200 €/ano consoante o nível de validação.<br>"
        "O fornecedor entrega diretamente um ficheiro <b>.pfx</b> (ou .p12) "
        "protegido por palavra-passe.<br><br>"
        "<i>Apenas para uso interno, pode gerar um certificado auto-assinado "
        "com OpenSSL:<br>"
        "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem "
        "-days 365 -nodes<br>"
        "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt></i>"
    ),

    # ── Diálogo Sobre ──────────────────────────────────────────────────────
    "À propos de PDF Editor": "Sobre o PDF Editor",
    (
        "<b>PDF Editor</b><br>"
        "Version 1.0.0<br><br>"
        "Éditeur PDF open source gratuit.<br>"
        "Stack : PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licence : MIT"
    ): (
        "<b>PDF Editor</b><br>"
        "Versão 1.0.0<br><br>"
        "Editor PDF gratuito e de código aberto.<br>"
        "Stack: PySide6 · pdfium2 · pikepdf · pypdf · pyHanko · Tesseract<br><br>"
        "Licença: MIT"
    ),

    # ── Painel de pesquisa ─────────────────────────────────────────────────
    "Rechercher dans le document :": "Pesquisar no documento:",
    "Terme de recherche…": "Termo de pesquisa…",
    "Chercher": "Pesquisar",
    "Respecter la casse": "Distinguir maiúsculas",
    "Recherche en cours…": "A pesquisar…",
    "Aucun résultat.": "Sem resultados.",
    "{n} occurrence(s) trouvée(s).": "{n} ocorrência(s) encontrada(s).",
    "Erreur : {err}": "Erro: {err}",

    # ── Painel OCR ─────────────────────────────────────────────────────────
    (
        "⚠️  Tesseract OCR non installé.\n\n"
        "Téléchargez-le ici :\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Puis redémarrez l'application."
    ): (
        "⚠️  Tesseract OCR não está instalado.\n\n"
        "Descarregue aqui:\n"
        "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
        "Depois reinicie a aplicação."
    ),
    "Langue :": "Idioma:",
    "Lancer l'OCR sur la page courante": "Executar OCR na página atual",
    "Texte extrait :": "Texto extraído:",
    "Copier": "Copiar",
    "Exporter .txt": "Exportar .txt",
    "Erreur OCR": "Erro OCR",
    "Fichier texte (*.txt)": "Ficheiro de texto (*.txt)",

    # ── Diálogo de assinatura ──────────────────────────────────────────────
    "Signer le document": "Assinar documento",
    (
        "⚠️  pyHanko n'est pas installé.\n"
        "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
    ): (
        "⚠️  pyHanko não está instalado.\n"
        "Instale com: pip install pyhanko pyhanko-certvalidator"
    ),
    "Chemin vers le fichier .pfx / .p12": "Caminho para o ficheiro .pfx / .p12",
    "Certificat (.pfx) :": "Certificado (.pfx):",
    "Raison :": "Motivo:",
    "Document signé électroniquement": "Documento assinado eletronicamente",
    "Lieu :": "Local:",
    "Contact :": "Contacto:",
    "Page :": "Página:",
    "Sélectionner le certificat": "Selecionar certificado",
    "Certificats (*.pfx *.p12);;Tous les fichiers (*)":
        "Certificados (*.pfx *.p12);;Todos os ficheiros (*)",
    "Sélectionnez un fichier certificat valide.":
        "Selecione um ficheiro de certificado válido.",
    "Enregistrer le PDF signé": "Guardar PDF assinado",
    "PDF signé sauvegardé :\n{path}": "PDF assinado guardado:\n{path}",

    # ── Diálogo de junção ──────────────────────────────────────────────────
    "Fusionner des PDFs": "Juntar PDFs",
    "Fichiers à fusionner (glisser pour réordonner) :":
        "Ficheiros a juntar (arrastar para reordenar):",
    "Ajouter…": "Adicionar…",
    "Choisir des PDFs": "Escolher PDFs",
    "↑ Monter": "↑ Subir",
    "↓ Descendre": "↓ Descer",
    "Attention": "Atenção",
    "Ajoutez au moins 2 fichiers PDF.": "Adicione pelo menos 2 ficheiros PDF.",
    "Enregistrer le PDF fusionné": "Guardar PDF unido",
    "PDF fusionné :\n{path}": "PDF unido:\n{path}",

    # ── Diálogo de divisão ─────────────────────────────────────────────────
    "Découper le PDF": "Dividir PDF",
    "Mode de découpage": "Modo de divisão",
    "Une page par fichier (toutes les pages)": "Uma página por ficheiro (todas as páginas)",
    "Extraire une plage de pages :": "Extrair um intervalo de páginas:",
    "De": "De",
    "à": "a",
    "{n} fichiers créés dans :\n{dir}": "{n} ficheiro(s) criado(s) em:\n{dir}",
    "Enregistrer l'extrait": "Guardar extrato",
    "Extrait sauvegardé :\n{path}": "Extrato guardado:\n{path}",

    # ── Painel esquerdo — ferramentas PDF (v1.2) ───────────────────────────
    "🛠  Outils PDF": "🛠  Ferramentas PDF",
    "Réorganiser/Fusionner…": "Reorganizar/Juntar…",
    "Fractionner…": "Dividir…",
    "En-têtes / pieds de page…": "Cabeçalhos / rodapés…",

    # ── Menus adicionais (v1.2) ────────────────────────────────────────────
    "Nouveau formulaire vierge…": "Novo formulário em branco…",
    "Imprimer…": "Imprimir…",
    "Insérer une image…": "Inserir imagem…",
    "Insérer un bloc de texte…": "Inserir bloco de texto…",
    "Déplacer un bloc de texte": "Mover bloco de texto",
    "Réorganiser/Fusionner les pages…": "Reorganizar/Juntar páginas…",
    "Fractionner ce PDF…": "Dividir este PDF…",
    "Supprimer la page courante": "Eliminar página atual",
    "Métadonnées…": "Metadados…",
    "En-têtes et pieds de page…": "Cabeçalhos e rodapés…",
    "Filigrane…": "Marca de água…",
    "Tampon texte…": "Carimbo de texto…",
    "Tampon image…": "Carimbo de imagem…",
    "Compresser le PDF": "Comprimir PDF",
    "Reconnaissance de caractères (OCR)…": "Reconhecimento de caracteres (OCR)…",
    "Rechercher…": "Procurar…",
    "Manuel utilisateur": "Manual do utilizador",
    "Intégration Windows (clic droit)…": "Integração Windows (clique direito)…",
    "Formulaire": "Formulário",

    # ── Barra Páginas & Formulário (v1.2) ──────────────────────────────────
    "Pages & Formulaire": "Páginas & Formulário",
    "⊕ Réorganiser/Fusionner": "⊕ Reorganizar/Juntar",
    "Réorganiser/Fusionner les pages…": "Reorganizar/Juntar páginas…",
    "✂ Fractionner": "✂ Dividir",
    "🗑 Suppr. page": "🗑 Elim. pág.",
    "Supprimer la page courante (Delete)": "Eliminar página atual (Del)",
    "🖼 Insérer image": "🖼 Inserir imagem",
    "Dessiner une zone pour insérer une image dans le PDF":
        "Desenhe uma área para inserir uma imagem no PDF",
    "📝 Insérer texte": "📝 Inserir texto",
    "Dessiner une zone pour insérer un bloc de texte dans le PDF":
        "Desenhe uma área para inserir um bloco de texto no PDF",
    "✏ Mode Design": "✏ Modo Design",
    "Activer/désactiver le mode design de formulaire":
        "Ativar/desativar o modo de design de formulário",

    # ── Painel de ferramentas (v1.2) ───────────────────────────────────────
    "✏  Annotations": "✏  Anotações",
    "Couleur :": "Cor:",
    "Personnalisé": "Personalizado",
    "Épaisseur :": "Espessura:",
    "💡 Raccourcis": "💡 Atalhos",
    "Double-clic → modifier texte": "Duplo clique → editar texto",
    "Clic droit → menu contextuel": "Clique direito → menu de contexto",
    "H  Surligner": "H  Realçar",
    "C  Commentaire": "C  Comentário",
    "E  Effacer": "E  Apagar",
    "M  Déplacer texte": "M  Mover texto",

    # ── Diálogo carimbo de texto (v1.2) ────────────────────────────────────
    "Ajouter un tampon": "Adicionar um carimbo",
    "APPROUVÉ": "APROVADO",
    "REJETÉ": "REJEITADO",
    "À SIGNER": "A ASSINAR",
    "CONFIDENTIEL": "CONFIDENCIAL",
    "BROUILLON": "RASCUNHO",
    "URGENT": "URGENTE",
    "COPIE": "CÓPIA",
    "À RÉVISER": "A REVER",
    "Personnalisé…": "Personalizado…",
    "Tampon :": "Carimbo:",
    "Votre texte…": "O seu texto…",
    "Position :": "Posição:",
    "Pages :": "Páginas:",
    "Horizontal  (0°)": "Horizontal  (0°)",
    "Diagonal  (−45°)": "Diagonal  (−45°)",
    "Rotation :": "Rotação:",
    "Opacité :": "Opacidade:",
    "Appliquer": "Aplicar",
    "Aperçu :": "Pré-visualização:",
    "Haut-droit": "Superior direito",
    "Haut-gauche": "Superior esquerdo",
    "Bas-droit": "Inferior direito",
    "Bas-gauche": "Inferior esquerdo",
    "Centre": "Centro",
    "Toutes les pages": "Todas as páginas",
    "Première page": "Primeira página",
    "Dernière page": "Última página",

    # ── Diálogo carimbo de imagem (v1.2) ───────────────────────────────────
    "Tampon image": "Carimbo de imagem",
    "Bibliothèque de tampons :": "Biblioteca de carimbos:",
    "Supprimer ce tampon de la bibliothèque": "Remover este carimbo da biblioteca",
    "Taille :": "Tamanho:",
    " % largeur page": " % largura da página",
    "Choisir une image": "Escolher uma imagem",
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)":
        "Imagens (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)",
    "Nom du tampon": "Nome do carimbo",
    "Donnez un nom à ce tampon :": "Dê um nome a este carimbo:",
    "Mon tampon": "O meu carimbo",
    "Supprimer le tampon « {n} » de la bibliothèque ?":
        "Remover o carimbo « {n} » da biblioteca?",

    # ── Diálogo organizar (v1.2) ───────────────────────────────────────────
    "Organiser les pages": "Organizar páginas",
    "Ajouter un document…": "Adicionar documento…",
    "Monter": "Subir",
    "Descendre": "Descer",
    "Documents supportés": "Documentos suportados",
    "Images": "Imagens",
    "Ajouter un document": "Adicionar documento",
    "{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)":
        "{n} página(s) no total — {orig} original(ais), {removed} eliminada(s)",
    "Le document ne peut pas être vide.": "O documento não pode estar vazio.",

    # ── Diálogo cabeçalhos/rodapés (v1.2) ─────────────────────────────────
    "En-têtes et pieds de page": "Cabeçalhos e rodapés",
    "En-tête": "Cabeçalho",
    "Pied de page": "Rodapé",
    "Options communes": "Opções comuns",
    "Taille de police :": "Tamanho da letra:",
    "Marge depuis le bord :": "Margem a partir da borda:",
    "Ne pas appliquer sur la 1ère page": "Não aplicar na 1.ª página",
    "Gauche": "Esquerda",
    "Droite": "Direita",
    "En-tête gauche": "Cabeçalho esquerdo",

    # ── Diálogo marca de água (v1.2) ───────────────────────────────────────
    "Ajouter un filigrane": "Adicionar marca de água",
    "Texte :": "Texto:",

    # ── Diálogo metadados (v1.2) ───────────────────────────────────────────
    "Métadonnées du document": "Metadados do documento",
    "Informations enregistrées dans le fichier PDF :":
        "Informação guardada no ficheiro PDF:",
    "Titre :": "Título:",
    "Auteur :": "Autor:",
    "Sujet :": "Assunto:",
    "Mots-clés :": "Palavras-chave:",
    "Application :": "Aplicação:",

    # ── Diálogo de ajuda (v1.2) ────────────────────────────────────────────
    "Manuel utilisateur — PDF Editor": "Manual do utilizador — PDF Editor",
    "Rechercher :": "Procurar:",
    "Mot-clé…": "Palavra-chave…",
    "Occurrence précédente": "Ocorrência anterior",
    "Occurrence suivante": "Ocorrência seguinte",
    "Fichier de documentation introuvable :\n": "Ficheiro de documentação não encontrado:\n",

    # ── Painel de formulário (v1.2) ────────────────────────────────────────
    "Nouveau formulaire vierge": "Novo formulário em branco",
    "✏  Mode Design — Ajouter des champs": "✏  Modo Design — Adicionar campos",
    "Aucun formulaire détecté dans ce PDF.": "Nenhum formulário detetado neste PDF.",
    "Enregistrer et exporter JSON": "Guardar e exportar JSON",
    "JSON embarqué :": "JSON incorporado:",
    "JSON précédemment embarqué.": "JSON anteriormente incorporado.",
    "Données sauvegardées.": "Dados guardados.",

    # ── Barra de estado (v1.2) ─────────────────────────────────────────────
    "   📋 Formulaire : {n} champ(s)": "   📋 Formulário: {n} campo(s)",
    "Pages réorganisées — pensez à enregistrer (Ctrl+S).":
        "Páginas reorganizadas — lembre-se de guardar (Ctrl+S).",
    "Enregistrer le nouveau PDF": "Guardar novo PDF",
    "Nouveau PDF créé et ouvert : {name}": "Novo PDF criado e aberto: {name}",
    "En-têtes/pieds de page supprimés.": "Cabeçalhos/rodapés removidos.",
    "En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S).":
        "Cabeçalhos/rodapés adicionados — lembre-se de guardar (Ctrl+S).",
    "Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S).":
        "Marca de água adicionada a todas as páginas — lembre-se de guardar (Ctrl+S).",
    "toutes les pages": "todas as páginas",
    "la première page": "a primeira página",
    "la dernière page": "a última página",
    "Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).":
        "Carimbo « {t} » adicionado em {n} — lembre-se de guardar (Ctrl+S).",
    "Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).":
        "Carimbo de imagem aplicado em {n} — lembre-se de guardar (Ctrl+S).",
    "Métadonnées mises à jour — pensez à enregistrer (Ctrl+S).":
        "Metadados atualizados — lembre-se de guardar (Ctrl+S).",
    "Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).":
        "Compressão efetuada — ganho estimado: {kb} KB. Guarde para finalizar (Ctrl+S).",
    "Le document est déjà optimal — aucun gain de compression possible.":
        "O documento já é ótimo — não é possível ganho de compressão.",
    "{n} ligne(s) OCR incrustée(s) sur la page.":
        "{n} linha(s) OCR incorporada(s) na página.",
    "Texte modifié. Enregistrez pour sauvegarder.":
        "Texto modificado. Guarde para manter as alterações.",
    "Bloc déplacé. Enregistrez pour sauvegarder.":
        "Bloco movido. Guarde para manter as alterações.",
    "Bloc supprimé. Enregistrez pour sauvegarder.":
        "Bloco eliminado. Guarde para manter as alterações.",
    "Texte masqué. Enregistrez pour sauvegarder.":
        "Texto ocultado. Guarde para manter as alterações.",
    "Texte supprimé du flux. Enregistrez pour sauvegarder.":
        "Texto removido do fluxo. Guarde para manter as alterações.",
    "Impossible de supprimer ce texte du flux.":
        "Não é possível remover este texto do fluxo.",
    "Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer.":
        "Clique direito num elemento para o selecionar, depois Del para apagar.",
    "Cliquez directement sur un bloc de texte OCR pour le modifier.":
        "Clique diretamente num bloco de texto OCR para o editar.",
    "Champ « {name} » modifié.": "Campo « {name} » modificado.",
    "Champ « {name} » ({type}) ajouté.": "Campo « {name} » ({type}) adicionado.",
    "Nom de champ vide — champ non créé.": "Nome de campo vazio — campo não criado.",
    "Chemin d'image manquant.": "Caminho de imagem em falta.",

    # ── Caixas de diálogo (v1.2) ───────────────────────────────────────────
    "Modifications non enregistrées": "Alterações não guardadas",
    "Le document a été modifié. Enregistrer avant de continuer ?":
        "O documento foi modificado. Guardar antes de continuar?",
    "Ne pas enregistrer": "Não guardar",
    "Des modifications ont été apportées. Enregistrer avant de fermer ?":
        "Foram feitas alterações. Guardar antes de fechar?",
    "Quitter sans enregistrer": "Sair sem guardar",
    "Redémarrer": "Reiniciar",
    "Modifier le texte…": "Editar texto…",
    "Supprimer ce bloc": "Eliminar este bloco",
    "Modifier le champ « {name} »…": "Editar campo « {name} »…",
    "Supprimer le champ « {name} »": "Eliminar campo « {name} »",
    "Modifier « {t}… »": "Editar « {t}… »",
    "Masquer (rectangle blanc)": "Ocultar (retângulo branco)",
    "Supprimer du flux PDF": "Remover do fluxo PDF",
    "Déplacer / redimensionner…": "Mover / redimensionar…",
    "Nom déjà utilisé": "Nome já utilizado",
    "Un champ nommé « {name} » existe déjà.":
        "Já existe um campo com o nome « {name} ».",
    "Saisir le commentaire :": "Introduzir comentário:",
    "Modifier le commentaire": "Editar comentário",
    "Modifier le texte": "Editar texto",
    "Remplacer l'image": "Substituir imagem",
    "Supprimer la page": "Eliminar página",
    "Impossible de supprimer l'unique page du document.":
        "Não é possível eliminar a única página do documento.",
    "Supprimer la page {n} du document ?": "Eliminar a página {n} do documento?",
    "Page {n} supprimée.": "Página {n} eliminada.",

    # ── Integração Windows (v1.2) ──────────────────────────────────────────
    "Intégration Windows — clic droit": "Integração Windows — clique direito",
    "✅ Actif": "✅ Ativo",
    "❌ Inactif": "❌ Inativo",
    "Statut :": "Estado:",
    (
        "Lorsque l'intégration est active, un clic droit sur un fichier image "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
        "que l'image."
    ): (
        "Quando a integração está ativa, um clique direito num ficheiro de imagem "
        "({exts}) no Explorador do Windows apresenta a opção "
        "<b>Converter em PDF</b>. O PDF é criado na mesma pasta "
        "que a imagem."
    ),
    "Désactiver": "Desativar",
    "Activer": "Ativar",
    "Intégration Windows": "Integração Windows",
    "Clic droit désactivé pour les fichiers images.":
        "Clique direito desativado para ficheiros de imagem.",
    (
        "Clic droit activé !\n\n"
        "Faites un clic droit sur n'importe quelle image "
        "({exts}) dans l'explorateur pour convertir en PDF."
    ): (
        "Clique direito ativado!\n\n"
        "Clique com o botão direito em qualquer imagem "
        "({exts}) no Explorador para converter em PDF."
    ),

    # ── Diálogo extração de texto (v1.4) ───────────────────────────────────
    "🛠  Outils": "🛠  Ferramentas",
    "Extraire le texte": "Extrair texto",
    "Toutes les pages ({n})": "Todas as páginas ({n})",
    "Page courante ({n})": "Página atual ({n})",
    "Intervalle :": "Intervalo:",
    "De la page": "Da página",
    "Extraction": "Extração",
    "Pages {a} à {b}": "Páginas {a} a {b}",
    "Page {n}": "Página {n}",
    "Extraction réussie ✅": "Extração bem-sucedida ✅",
    "Extraction terminée avec succès !": "Extração concluída com sucesso!",
    "Pages extraites :": "Páginas extraídas:",
    "Caractères :": "Caracteres:",
    "Mots :": "Palavras:",
    "Lignes :": "Linhas:",
    "Fichier :": "Ficheiro:",

    # ── Painel de idioma (v1.4) ────────────────────────────────────────────
    "Choisir la langue :": "Escolher idioma:",
    "Un redémarrage est nécessaire\npour appliquer le changement.":
        "É necessário reiniciar\npara aplicar a alteração.",

    # ── Painel de ajuda (v1.4) ─────────────────────────────────────────────
    "Actions rapides :": "Ações rápidas:",
    "Raccourcis clavier :": "Atalhos de teclado:",

    # ── Diálogo de licença (v1.4) ─────────────────────────────────────────
    "Activation de PDF Editor": "Ativação do PDF Editor",
    "Licence…": "Licença…",
    "Licence — PDF Editor": "Licença — PDF Editor",
    "Clé de licence :": "Chave de licença:",
    "Vérification…": "A verificar…",
    "Connexion à Lemon Squeezy…": "A ligar ao Lemon Squeezy…",
    "Licence activée avec succès.": "Licença ativada com sucesso.",
    "Licence valide.": "Licença válida.",
    "Licence désactivée sur cet ordinateur.": "Licença desativada neste computador.",
    "Désactiver cette licence": "Desativar esta licença",
    "Désactiver la licence": "Desativar licença",
    "Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste.":
        "Remover a licença deste computador?\n\nPoderá reativá-la noutro dispositivo.",
    "Aucune licence activée sur cet ordinateur.": "Nenhuma licença ativada neste computador.",
    "Entrer une clé de licence": "Introduzir chave de licença",
    "Clé de licence invalide.": "Chave de licença inválida.",
    "Impossible de valider la licence (hors-ligne depuis trop longtemps).":
        "Não é possível validar a licença (sem ligação há demasiado tempo).",
    "Pas encore de licence ? ": "Ainda sem licença? ",
    "Acheter PDF Editor": "Comprar PDF Editor",
    "Veuillez entrer votre clé de licence reçue par email après l'achat.\nFormat : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX":
        "Introduza a sua chave de licença recebida por email após a compra.\nFormato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "Mode hors-ligne — {remaining} jour(s) restant(s).":
        "Modo offline — {remaining} dia(s) restante(s).",
    "Licence": "Licença",

    # ── Integração de shell — combinar (v1.4) ──────────────────────────────
    "🖼  Transformer une image en PDF": "🖼  Converter imagem em PDF",
    "📎  Combiner des fichiers dans PDF Editor":
        "📎  Combinar ficheiros no PDF Editor",
    (
        "Lorsque l'intégration est active, une sélection multiple de fichiers "
        "({exts}) dans l'explorateur Windows propose l'option "
        "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
        "s'ouvre avec ces fichiers pré-chargés."
    ): (
        "Quando a integração está ativa, uma seleção múltipla de ficheiros "
        "({exts}) no Explorador do Windows propõe a opção "
        "<b>Combinar no PDF Editor</b>. O diálogo de organização "
        "abre com estes ficheiros pré-carregados."
    ),
    (
        "Combinaison activée !\n\n"
        "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
        "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
    ): (
        "Combinação ativada!\n\n"
        "Selecione vários ficheiros ({exts}) no Explorador,\n"
        "clique com o botão direito e escolha «\u202fCombinar no PDF Editor\u202f»."
    ),
    "Clic droit «\u202fCombiner\u202f» désactivé.":
        "Clique direito «\u202fCombinar\u202f» desativado.",
}
