; ============================================================================
;  PDF Editor — Inno Setup installer script
;  Requires Inno Setup 6.3+  https://jrsoftware.org/isinfo.php
;
;  Build:
;    iscc installer\PDF_Editor.iss
;
;  Expected input:
;    ..\dist\PDFEditor\   (output of PyInstaller / build_installer.bat)
;    ..\assets\icon.ico   (optional — comment out SetupIconFile if absent)
; ============================================================================

#define AppName      "PDF Editor"
#define AppVersion   "1.4.2"
#define AppPublisher "Leteint"
#define AppURL       "https://github.com/Leteint/pdf-editor"
#define AppExeName   "PDFEditor.exe"
#define DistDir      "..\dist\PDFEditor"

; Tesseract installer — mirrored on our GitHub release for URL stability.
; Original source: https://github.com/UB-Mannheim/tesseract/releases
; To update: download new version, upload to Leteint/pdf-editor release, update defines below.
#define TesseractVersion "5.4.0.20240606"
#define TesseractURL     "https://github.com/Leteint/pdf-editor/releases/download/v1.4.2/tesseract-ocr-w64-setup-" + TesseractVersion + ".exe"

; Tessdata-fast models (~5–10 MB each, good speed/accuracy trade-off)
; Source: https://github.com/tesseract-ocr/tessdata_fast
#define TessdataBaseURL "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/"

; Default Tesseract installation path
#define TesseractDefaultDir "{pf64}\Tesseract-OCR"

; ============================================================================
[Setup]
AppId={{B3F2A1C4-9D7E-4F2B-8A5C-1E6D3F0A2B7C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=.
OutputBaseFilename=PDFEditor-{#AppVersion}-Setup
MinVersion=10.0
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\assets\icons\icon.ico  ; uncomment once icon.ico is placed in assets/
WizardStyle=modern
WizardSizePercent=120
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; Extra wizard pages need more height
WizardResizable=yes

; ============================================================================
[Languages]
Name: "french";    MessagesFile: "compiler:Languages\French.isl"
Name: "english";   MessagesFile: "compiler:Default.isl"
Name: "spanish";   MessagesFile: "compiler:Languages\Spanish.isl"
Name: "italian";   MessagesFile: "compiler:Languages\Italian.isl"

; ============================================================================
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}";                                             GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "setdefault";  Description: "Définir PDF Editor comme application par défaut pour les fichiers PDF"; GroupDescription: "Association de fichiers :"; Flags: checked

; ============================================================================
[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ============================================================================
[Icons]
Name: "{group}\{#AppName}";                           Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}";     Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";                     Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

; ============================================================================
[Registry]

; ── ProgID : déclaration de PDFEditor.Document ────────────────────────────
Root: HKCU; Subkey: "Software\Classes\PDFEditor.Document";                        ValueType: string; ValueName: "";                   ValueData: "Fichier PDF";           Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\PDFEditor.Document";                        ValueType: string; ValueName: "FriendlyTypeName";    ValueData: "Fichier PDF"
Root: HKCU; Subkey: "Software\Classes\PDFEditor.Document\DefaultIcon";            ValueType: string; ValueName: "";                   ValueData: "{app}\{#AppExeName},0"
Root: HKCU; Subkey: "Software\Classes\PDFEditor.Document\shell\open\command";     ValueType: string; ValueName: "";                   ValueData: """{app}\{#AppExeName}"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\PDFEditor.Document\shell\open";             ValueType: string; ValueName: "FriendlyAppName";    ValueData: "{#AppName}"

; ── Apparaître dans "Ouvrir avec" pour les .pdf ───────────────────────────
Root: HKCU; Subkey: "Software\Classes\.pdf\OpenWithProgids";                      ValueType: string; ValueName: "PDFEditor.Document"; ValueData: "";                      Flags: uninsdeletevalue

; ── Capabilities (panneau "Applications par défaut" de Windows) ───────────
Root: HKLM; Subkey: "Software\{#AppName}\Capabilities";                           ValueType: string; ValueName: "ApplicationName";        ValueData: "{#AppName}";         Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppName}\Capabilities";                           ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Éditeur PDF open source"
Root: HKLM; Subkey: "Software\{#AppName}\Capabilities\FileAssociations";          ValueType: string; ValueName: ".pdf";                   ValueData: "PDFEditor.Document"
Root: HKLM; Subkey: "Software\RegisteredApplications";                            ValueType: string; ValueName: "{#AppName}";             ValueData: "Software\{#AppName}\Capabilities"; Flags: uninsdeletevalue

; ── Définir PDF Editor comme application par défaut (tâche optionnelle) ───
; Écrit dans HKCU\Software\Classes\.pdf — sans droits admin, pris en compte
; immédiatement par Windows pour l'utilisateur courant.
Root: HKCU; Subkey: "Software\Classes\.pdf";                                      ValueType: string; ValueName: "";                   ValueData: "PDFEditor.Document";    Flags: uninsdeletevalue; Tasks: setdefault

; ============================================================================
[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; ============================================================================
[UninstallDelete]
; Uncomment to wipe user config on uninstall:
; Type: filesandordirs; Name: "{%USERPROFILE}\.pdf_editor"

; ============================================================================
[Code]

// ──────────────────────────────────────────────────────────────────────────
// Global variables
// ──────────────────────────────────────────────────────────────────────────
var
  // OCR setup wizard page (custom)
  OcrPage:        TWizardPage;
  ChkInstallOcr:  TCheckBox;
  LblOcrInfo:     TLabel;
  LblLangInfo:    TLabel;
  CmbLang:        TComboBox;

  // Resolved at runtime
  DetectedLangCode:   String;   // e.g. "fra"
  DetectedLangLabel:  String;   // e.g. "Français"
  TesseractInstalled: Boolean;
  TesseractPath:      String;

// ──────────────────────────────────────────────────────────────────────────
// Map Windows primary-language ID → Tesseract language code + display name
// Windows LCID docs: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid
// ──────────────────────────────────────────────────────────────────────────
procedure GetSystemLangInfo(out LangCode, LangLabel: String);
var
  PrimaryLang: Integer;
begin
  // GetSystemDefaultLCID returns a full LCID; primary language is low 10 bits
  PrimaryLang := GetSystemDefaultLCID() and 1023;
  case PrimaryLang of
    $001: begin LangCode := 'ara'; LangLabel := 'Arabic / عربي';         end;
    $004: begin LangCode := 'chi_sim'; LangLabel := 'Chinese Simplified'; end;
    $005: begin LangCode := 'ces'; LangLabel := 'Czech / Čeština';        end;
    $006: begin LangCode := 'dan'; LangLabel := 'Danish / Dansk';         end;
    $007: begin LangCode := 'deu'; LangLabel := 'German / Deutsch';       end;
    $008: begin LangCode := 'ell'; LangLabel := 'Greek / Ελληνικά';       end;
    $009: begin LangCode := 'eng'; LangLabel := 'English';                end;
    $00A: begin LangCode := 'spa'; LangLabel := 'Spanish / Español';      end;
    $00B: begin LangCode := 'fin'; LangLabel := 'Finnish / Suomi';        end;
    $00C: begin LangCode := 'fra'; LangLabel := 'Français';               end;
    $00D: begin LangCode := 'heb'; LangLabel := 'Hebrew / עברית';         end;
    $00E: begin LangCode := 'hun'; LangLabel := 'Hungarian / Magyar';     end;
    $010: begin LangCode := 'ita'; LangLabel := 'Italian / Italiano';     end;
    $011: begin LangCode := 'jpn'; LangLabel := 'Japanese / 日本語';       end;
    $012: begin LangCode := 'kor'; LangLabel := 'Korean / 한국어';          end;
    $013: begin LangCode := 'nld'; LangLabel := 'Dutch / Nederlands';     end;
    $014: begin LangCode := 'nor'; LangLabel := 'Norwegian / Norsk';      end;
    $015: begin LangCode := 'pol'; LangLabel := 'Polish / Polski';        end;
    $016: begin LangCode := 'por'; LangLabel := 'Portuguese / Português'; end;
    $018: begin LangCode := 'ron'; LangLabel := 'Romanian / Română';      end;
    $019: begin LangCode := 'rus'; LangLabel := 'Russian / Русский';      end;
    $01D: begin LangCode := 'swe'; LangLabel := 'Swedish / Svenska';      end;
    $01F: begin LangCode := 'tur'; LangLabel := 'Turkish / Türkçe';       end;
    $022: begin LangCode := 'ukr'; LangLabel := 'Ukrainian / Українська'; end;
    $02A: begin LangCode := 'vie'; LangLabel := 'Vietnamese / Tiếng Việt';end;
  else
    // Unsupported locale → fall back to English
    LangCode  := 'eng';
    LangLabel := 'English (default)';
  end;
end;

// ──────────────────────────────────────────────────────────────────────────
// Check whether Tesseract is already installed (registry + disk)
// ──────────────────────────────────────────────────────────────────────────
function FindTesseract(out InstallPath: String): Boolean;
begin
  Result := False;
  InstallPath := '';

  // 1. Installer writes this key
  if RegQueryStringValue(HKLM64,
       'SOFTWARE\Tesseract-OCR', 'InstallDir', InstallPath) then
  begin
    if FileExists(InstallPath + '\tesseract.exe') then
    begin
      Result := True;
      Exit;
    end;
  end;

  // 2. Common fallback paths
  if FileExists(ExpandConstant('{pf64}\Tesseract-OCR\tesseract.exe')) then
  begin
    InstallPath := ExpandConstant('{pf64}\Tesseract-OCR');
    Result := True;
    Exit;
  end;
  if FileExists(ExpandConstant('{pf}\Tesseract-OCR\tesseract.exe')) then
  begin
    InstallPath := ExpandConstant('{pf}\Tesseract-OCR');
    Result := True;
  end;
end;

// ──────────────────────────────────────────────────────────────────────────
// Download a file using PowerShell (Invoke-WebRequest)
// Returns True on success.
// ──────────────────────────────────────────────────────────────────────────
function DownloadFile(const URL, Dest: String): Boolean;
var
  Args:       String;
  ResultCode: Integer;
begin
  // Use TLS 1.2 explicitly for GitHub/CDN compatibility
  Args := Format(
    '-NoProfile -NonInteractive -Command ' +
    '"[Net.ServicePointManager]::SecurityProtocol = ' +
    '''[Net.SecurityProtocolType]::Tls12''; ' +
    'Invoke-WebRequest -Uri ''%s'' -OutFile ''%s'' -UseBasicParsing"',
    [URL, Dest]);
  Result := Exec('powershell.exe', Args, '', SW_HIDE,
                 ewWaitUntilTerminated, ResultCode)
            and (ResultCode = 0);
end;

// ──────────────────────────────────────────────────────────────────────────
// Write / update the app config.json with the Tesseract path
// The file lives in %USERPROFILE%\.pdf_editor\config.json
// We use PowerShell so we don't need to parse JSON ourselves.
// ──────────────────────────────────────────────────────────────────────────
procedure WriteConfigTesseractPath(const TessDir: String);
var
  ConfigDir, ConfigFile, TessExe, Script: String;
  ResultCode: Integer;
begin
  ConfigDir  := ExpandConstant('{%USERPROFILE}') + '\.pdf_editor';
  ConfigFile := ConfigDir + '\config.json';
  TessExe    := TessDir + '\tesseract.exe';

  // Build the PowerShell one-liner:
  // – read existing JSON (or start from empty object)
  // – update / add the tesseract_path key
  // – write back
  Script :=
    '-NoProfile -NonInteractive -Command ' +
    '"$f=''' + ConfigFile + '''; ' +
    '$d=''' + ConfigDir  + '''; ' +
    'if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }; ' +
    'if (Test-Path $f) { $c = Get-Content $f -Raw | ConvertFrom-Json } ' +
    'else { $c = New-Object PSObject }; ' +
    '$c | Add-Member -NotePropertyName tesseract_path -NotePropertyValue ''' +
       TessExe + ''' -Force; ' +
    '$c | ConvertTo-Json | Set-Content $f -Encoding UTF8"';

  Exec('powershell.exe', Script, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// ──────────────────────────────────────────────────────────────────────────
// Download + install Tesseract, then download the requested language model.
// Called from CurStepChanged when Step = ssPostInstall.
// ──────────────────────────────────────────────────────────────────────────
procedure InstallTesseract(const LangCode: String);
var
  TmpInstaller, TmpTrainedData: String;
  TargetTessDir:                String;
  TessdataDir:                  String;
  ResultCode:                   Integer;
  NeedsInstall:                 Boolean;
begin
  // ── 1. Determine whether we need to run the installer ──────────────────
  NeedsInstall := not FindTesseract(TargetTessDir);

  if NeedsInstall then
  begin
    // Download the Tesseract installer to a temp location
    TmpInstaller := ExpandConstant('{tmp}') + '\tesseract-setup.exe';
    Log('Downloading Tesseract from: {#TesseractURL}');
    WizardForm.StatusLabel.Caption := 'Téléchargement de Tesseract OCR…';

    if not DownloadFile('{#TesseractURL}', TmpInstaller) then
    begin
      MsgBox(
        'Le téléchargement de Tesseract OCR a échoué.' + #13#10 +
        'Vérifiez votre connexion Internet.' + #13#10#13#10 +
        'Vous pourrez l''installer manuellement depuis :' + #13#10 +
        'https://github.com/UB-Mannheim/tesseract/releases',
        mbError, MB_OK);
      Exit;
    end;

    // Run the NSIS installer silently
    // /S = silent, /D = install dir (must be last argument for NSIS)
    TargetTessDir := ExpandConstant('{pf64}') + '\Tesseract-OCR';
    WizardForm.StatusLabel.Caption := 'Installation de Tesseract OCR…';
    Log('Running Tesseract installer silently into: ' + TargetTessDir);
    Exec(TmpInstaller, '/S /D=' + TargetTessDir, '', SW_HIDE,
         ewWaitUntilTerminated, ResultCode);

    if ResultCode <> 0 then
    begin
      MsgBox(
        Format('L''installation de Tesseract a échoué (code %d).', [ResultCode]) +
        #13#10 + 'L''OCR sera indisponible.',
        mbError, MB_OK);
      Exit;
    end;
  end
  else
  begin
    Log('Tesseract already installed at: ' + TargetTessDir);
  end;

  // ── 2. Download the language model ────────────────────────────────────
  TessdataDir := TargetTessDir + '\tessdata';
  // Create tessdata dir if the minimal installer omitted it
  if not DirExists(TessdataDir) then
    CreateDir(TessdataDir);

  // Always ensure English is present as fallback
  if (LangCode <> 'eng') and
     (not FileExists(TessdataDir + '\eng.traineddata')) then
  begin
    TmpTrainedData := ExpandConstant('{tmp}') + '\eng.traineddata';
    WizardForm.StatusLabel.Caption := 'Téléchargement du modèle OCR (eng)…';
    Log('Downloading eng.traineddata');
    DownloadFile('{#TessdataBaseURL}eng.traineddata', TmpTrainedData);
    FileCopy(TmpTrainedData, TessdataDir + '\eng.traineddata', False);
  end;

  // Download the selected language model (skip if already present)
  if not FileExists(TessdataDir + '\' + LangCode + '.traineddata') then
  begin
    TmpTrainedData := ExpandConstant('{tmp}') + '\' + LangCode + '.traineddata';
    WizardForm.StatusLabel.Caption :=
      Format('Téléchargement du modèle OCR (%s)…', [LangCode]);
    Log('Downloading ' + LangCode + '.traineddata');
    if not DownloadFile('{#TessdataBaseURL}' + LangCode + '.traineddata',
                        TmpTrainedData) then
    begin
      MsgBox(
        Format('Le modèle OCR pour « %s » n''a pas pu être téléchargé.', [LangCode]) +
        #13#10 + 'Seul l''anglais sera disponible pour l''OCR.',
        mbInformation, MB_OK);
    end
    else
    begin
      FileCopy(TmpTrainedData,
               TessdataDir + '\' + LangCode + '.traineddata', False);
    end;
  end;

  // ── 3. Persist the Tesseract path in PDF Editor's config.json ─────────
  WriteConfigTesseractPath(TargetTessDir);
  Log('Tesseract setup complete at: ' + TargetTessDir);
end;

// ──────────────────────────────────────────────────────────────────────────
// Build the list of languages shown in the combo box
// ──────────────────────────────────────────────────────────────────────────
procedure PopulateLangCombo;
type
  TLangEntry = record
    Code:  String;
    Label: String;
  end;
const
  NLangs = 24;
var
  Langs:   array[0..NLangs-1] of TLangEntry;
  i:       Integer;
  SelIdx:  Integer;
begin
  // Same list as GetSystemLangInfo, in display order
  Langs[0].Code  := 'ara'; Langs[0].Label  := 'Arabic / عربي';
  Langs[1].Code  := 'ces'; Langs[1].Label  := 'Czech / Čeština';
  Langs[2].Code  := 'dan'; Langs[2].Label  := 'Danish / Dansk';
  Langs[3].Code  := 'deu'; Langs[3].Label  := 'German / Deutsch';
  Langs[4].Code  := 'ell'; Langs[4].Label  := 'Greek / Ελληνικά';
  Langs[5].Code  := 'eng'; Langs[5].Label  := 'English';
  Langs[6].Code  := 'spa'; Langs[6].Label  := 'Spanish / Español';
  Langs[7].Code  := 'fin'; Langs[7].Label  := 'Finnish / Suomi';
  Langs[8].Code  := 'fra'; Langs[8].Label  := 'Français';
  Langs[9].Code  := 'heb'; Langs[9].Label  := 'Hebrew / עברית';
  Langs[10].Code := 'hun'; Langs[10].Label := 'Hungarian / Magyar';
  Langs[11].Code := 'ita'; Langs[11].Label := 'Italian / Italiano';
  Langs[12].Code := 'jpn'; Langs[12].Label := 'Japanese / 日本語';
  Langs[13].Code := 'kor'; Langs[13].Label := 'Korean / 한국어';
  Langs[14].Code := 'nld'; Langs[14].Label := 'Dutch / Nederlands';
  Langs[15].Code := 'nor'; Langs[15].Label := 'Norwegian / Norsk';
  Langs[16].Code := 'pol'; Langs[16].Label := 'Polish / Polski';
  Langs[17].Code := 'por'; Langs[17].Label := 'Portuguese / Português';
  Langs[18].Code := 'ron'; Langs[18].Label := 'Romanian / Română';
  Langs[19].Code := 'rus'; Langs[19].Label := 'Russian / Русский';
  Langs[20].Code := 'chi_sim'; Langs[20].Label := 'Chinese Simplified / 简体中文';
  Langs[21].Code := 'swe'; Langs[21].Label := 'Swedish / Svenska';
  Langs[22].Code := 'tur'; Langs[22].Label := 'Turkish / Türkçe';
  Langs[23].Code := 'ukr'; Langs[23].Label := 'Ukrainian / Українська';

  SelIdx := 5; // English as safety default
  for i := 0 to NLangs - 1 do
  begin
    CmbLang.Items.Add(Langs[i].Label);
    // Tag each item with its code (stored as item Objects — encode as integer index trick)
    CmbLang.Items.Objects[i] := TObject(i);
    if Langs[i].Code = DetectedLangCode then
      SelIdx := i;
  end;
  CmbLang.ItemIndex := SelIdx;

  // Keep the code in a parallel simple lookup via tag on the combo itself
  // We'll retrieve it by index in GetSelectedLangCode()
end;

// ──────────────────────────────────────────────────────────────────────────
// Retrieve the Tesseract code for the currently selected combo item
// ──────────────────────────────────────────────────────────────────────────
function GetSelectedLangCode: String;
const
  Codes: array[0..23] of String = (
    'ara','ces','dan','deu','ell','eng','spa','fin','fra','heb',
    'hun','ita','jpn','kor','nld','nor','pol','por','ron','rus',
    'chi_sim','swe','tur','ukr');
begin
  if (CmbLang.ItemIndex >= 0) and (CmbLang.ItemIndex <= 23) then
    Result := Codes[CmbLang.ItemIndex]
  else
    Result := 'eng';
end;

// ──────────────────────────────────────────────────────────────────────────
// Create the custom OCR configuration wizard page
// ──────────────────────────────────────────────────────────────────────────
procedure CreateOcrPage;
var
  LblTitle, LblSub: TLabel;
begin
  OcrPage := CreateCustomPage(
    wpSelectTasks,
    'Reconnaissance de texte (OCR)',
    'Configuration du moteur Tesseract OCR');

  // ── Title ──
  LblTitle := TLabel.Create(OcrPage);
  LblTitle.Parent  := OcrPage.Surface;
  LblTitle.Caption := 'Tesseract OCR — moteur de reconnaissance de texte';
  LblTitle.Font.Style := [fsBold];
  LblTitle.SetBounds(0, 0, OcrPage.SurfaceWidth, 18);

  // ── Description ──
  LblSub := TLabel.Create(OcrPage);
  LblSub.Parent    := OcrPage.Surface;
  LblSub.Caption   :=
    'Tesseract est un logiciel libre (Apache 2.0) qui permet à PDF Editor' + #13#10 +
    'd''extraire le texte contenu dans les pages numérisées / images.' + #13#10 +
    'Il sera téléchargé depuis GitHub (~50 MB) puis installé automatiquement.';
  LblSub.WordWrap  := True;
  LblSub.SetBounds(0, 24, OcrPage.SurfaceWidth, 52);

  // ── Checkbox ──
  ChkInstallOcr := TCheckBox.Create(OcrPage);
  ChkInstallOcr.Parent  := OcrPage.Surface;
  if TesseractInstalled then
  begin
    ChkInstallOcr.Caption := 'Tesseract est déjà installé — vérifier / compléter les modèles de langue';
    ChkInstallOcr.Checked := True;
  end
  else
  begin
    ChkInstallOcr.Caption := 'Installer Tesseract OCR (recommandé)';
    ChkInstallOcr.Checked := True;
  end;
  ChkInstallOcr.SetBounds(0, 90, OcrPage.SurfaceWidth, 22);

  // ── Language label ──
  LblOcrInfo := TLabel.Create(OcrPage);
  LblOcrInfo.Parent  := OcrPage.Surface;
  LblOcrInfo.Caption := 'Langue OCR principale (détectée depuis votre système) :';
  LblOcrInfo.SetBounds(16, 122, OcrPage.SurfaceWidth - 16, 18);

  // ── Language combo ──
  CmbLang := TComboBox.Create(OcrPage);
  CmbLang.Parent   := OcrPage.Surface;
  CmbLang.Style    := csDropDownList;
  CmbLang.SetBounds(16, 144, 320, 24);
  PopulateLangCombo;

  // ── Info note ──
  LblLangInfo := TLabel.Create(OcrPage);
  LblLangInfo.Parent   := OcrPage.Surface;
  LblLangInfo.Caption  :=
    'L''anglais sera toujours inclus comme langue de secours.' + #13#10 +
    'D''autres langues peuvent être ajoutées plus tard via les préférences.';
  LblLangInfo.WordWrap := True;
  LblLangInfo.Font.Color := clGray;
  LblLangInfo.SetBounds(16, 175, OcrPage.SurfaceWidth - 16, 36);
end;

// ──────────────────────────────────────────────────────────────────────────
// Check for a previous installation and offer to remove it
// ──────────────────────────────────────────────────────────────────────────
function InitializeSetup(): Boolean;
var
  UninstallString: String;
  ResultCode:      Integer;
begin
  Result := True;

  // Previous version detection
  if RegQueryStringValue(HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B3F2A1C4-9D7E-4F2B-8A5C-1E6D3F0A2B7C}_is1',
    'UninstallString', UninstallString) then
  begin
    if MsgBox(
      'Une version précédente de PDF Editor est détectée.' + #13#10 +
      'Souhaitez-vous la désinstaller avant de continuer ?',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallString), '/SILENT', '',
           SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;

  // Pre-detect system language and Tesseract presence for later use
  GetSystemLangInfo(DetectedLangCode, DetectedLangLabel);
  TesseractInstalled := FindTesseract(TesseractPath);
end;

// ──────────────────────────────────────────────────────────────────────────
// Build the custom wizard pages once the wizard form is ready
// ──────────────────────────────────────────────────────────────────────────
procedure InitializeWizard;
begin
  CreateOcrPage;
end;

// ──────────────────────────────────────────────────────────────────────────
// After all files are copied, run the Tesseract install if requested
// ──────────────────────────────────────────────────────────────────────────
// ──────────────────────────────────────────────────────────────────────────
// Notifie Windows du changement d'association de fichiers (.pdf)
// SHChangeNotify(SHCNE_ASSOCCHANGED=0x08000000, SHCNF_IDLIST=0, 0, 0)
// ──────────────────────────────────────────────────────────────────────────
procedure NotifyFileAssocChanged;
var
  ResultCode: Integer;
begin
  Exec('powershell.exe',
    '-NoProfile -NonInteractive -Command ' +
    '"$code = @''
[DllImport(\"shell32.dll\")]
public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);
''@; ' +
    '$shell = Add-Type -MemberDefinition $code -Name ''Shell32'' -Namespace ''Win32'' -PassThru; ' +
    '$shell::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ChosenLangCode: String;
begin
  if CurStep = ssPostInstall then
  begin
    // ── OCR ──────────────────────────────────────────────────────────────
    if ChkInstallOcr.Checked then
    begin
      ChosenLangCode := GetSelectedLangCode();
      Log(Format('OCR install requested. Lang=%s', [ChosenLangCode]));
      InstallTesseract(ChosenLangCode);
    end
    else
    begin
      // User skipped OCR — still write path if Tesseract is present
      if TesseractInstalled and (TesseractPath <> '') then
        WriteConfigTesseractPath(TesseractPath);
      Log('OCR install skipped by user.');
    end;

    // ── Association de fichiers : notifier Windows ────────────────────────
    if WizardIsTaskSelected('setdefault') then
    begin
      Log('Notifying Windows of file association change for .pdf');
      NotifyFileAssocChanged;
    end;
  end;
end;
