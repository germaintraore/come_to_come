; ============================================================
; Come To Code – Script Inno Setup
; 2S Informatique Plus
; ============================================================

[Setup]
AppName=Come To Code
AppVersion=1.0.0
AppPublisher=2S Informatique Plus
AppPublisherURL=https://2sinformatiqueplus.com
AppSupportURL=https://2sinformatiqueplus.com
DefaultDirName={userappdata}\ComeToCode
DefaultGroupName=Come To Code
AllowNoIcons=yes
OutputDir=dist_installer
OutputBaseFilename=ComeToCode_Setup_v1.0
SetupIconFile=
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le Bureau"; GroupDescription: "Icônes additionnelles:"

[Files]
; Fichiers du projet (sans venv, cache, db de prod)
Source: "come_to_code\manage.py";          DestDir: "{app}"; Flags: ignoreversion
Source: "come_to_code\requirements.txt";   DestDir: "{app}"; Flags: ignoreversion
Source: "come_to_code\install.bat";        DestDir: "{app}"; Flags: ignoreversion
Source: "come_to_code\start.bat";          DestDir: "{app}"; Flags: ignoreversion
Source: "come_to_code\INSTALLATION.md";    DestDir: "{app}"; Flags: ignoreversion
Source: "come_to_code\config\*";           DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs
Source: "come_to_code\accounts\*";         DestDir: "{app}\accounts"; Flags: ignoreversion recursesubdirs; Excludes: "__pycache__\*,*.pyc"
Source: "come_to_code\templates\*";        DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs
Source: "come_to_code\static\*";           DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs
Source: "come_to_code\docs\*";             DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Démarrer Come To Code";    Filename: "{app}\start.bat"; WorkingDir: "{app}"
Name: "{group}\Documentation";            Filename: "{app}\INSTALLATION.md"
Name: "{group}\Désinstaller";             Filename: "{uninstallexe}"
Name: "{commondesktop}\Come To Code";     Filename: "{app}\start.bat"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\install.bat"; \
  Description: "Configurer l'application (crée l'environnement Python)"; \
  Flags: runhidden waituntilterminated; \
  StatusMsg: "Installation en cours, veuillez patienter..."

Filename: "{app}\start.bat"; \
  Description: "Lancer Come To Code maintenant"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\staticfiles"
Type: files;          Name: "{app}\db.sqlite3"

[Messages]
WelcomeLabel2=Ce programme va installer [name/ver] sur votre ordinateur.%n%nIl est recommandé de fermer toutes les autres applications avant de continuer.

[Code]
// Vérification que Python est installé
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if not Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox('Python n''est pas détecté sur cet ordinateur.' + #13#10 +
              'Come To Code nécessite Python 3.10 ou supérieur.' + #13#10 + #13#10 +
              'Voulez-vous continuer quand même ?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;
