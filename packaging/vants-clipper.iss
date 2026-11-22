#define MyAppName "VANTS Clipper"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppPublisher "VANTS GAMES"
#define MyAppURL "https://github.com/VANTSGAMES/VANTS-Clipper"
#define MyAppExeName "VANTS-Clipper.exe"

[Setup]
AppId={{8E9B7D4C-2B61-4C5A-9D08-51E2E3F4A110}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\VANTSGAMES\VANTS-Clipper
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=VANTS-Clipper-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\VANTS-Clipper.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\VANTS Clipper"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\VALORANT + VANTS Clipper"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--launch-valorant"
Name: "{group}\Desinstalar VANTS Clipper"; Filename: "{uninstallexe}"
Name: "{autodesktop}\VANTS Clipper"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--chequeo"; Description: "Verificar Razer Cortex y VALORANT"; Flags: nowait postinstall skipifsilent
