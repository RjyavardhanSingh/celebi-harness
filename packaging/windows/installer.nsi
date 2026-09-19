; Celebi NSIS Installer Script
; Build with: makensis installer.nsi

!include "MUI2.nsh"

; ── Configuration ──────────────────────────────────────────────
!ifndef APP_VERSION
  !define APP_VERSION "0.1.0"
!endif
!define APP_NAME "Celebi"
!define APP_PUBLISHER "Rajyavardhan Singh"
!define APP_URL "https://github.com/RjyavardhanSingh/celebi-harness"
!define APP_EXECUTABLE "celebi.exe"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "celebi-${APP_VERSION}-windows-setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "${UNINST_KEY}" "InstallDir"
RequestExecutionLevel admin

; ── Interface ──────────────────────────────────────────────────
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Welcome to ${APP_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will install ${APP_NAME} v${APP_VERSION} on your computer.$\r$\n$\r$\n${APP_NAME} is an LLM Time Travel Harness that captures and visualizes conversations between your coding agent and LLM providers.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXECUTABLE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Visit project on GitHub"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_URL}"

; ── Pages ──────────────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ── Languages ──────────────────────────────────────────────────
!insertmacro MUI_LANGUAGE "English"

; ── Installer ──────────────────────────────────────────────────
Section "Install"
    SetOutPath "$INSTDIR"
    SetRegView 64

    ; Copy all bundle files
    File /r "dist\celebi\*.*"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Add to Programs list
    WriteRegStr HKLM "${UNINST_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${UNINST_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${UNINST_KEY}" "URLInfoAbout" "${APP_URL}"
    WriteRegDWORD HKLM "${UNINST_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${UNINST_KEY}" "NoRepair" 1

    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

; ── Uninstaller ────────────────────────────────────────────────
Section "Uninstall"
    SetRegView 64

    ; Remove installed files
    RMDir /r "$INSTDIR"

    ; Remove registry keys
    DeleteRegKey HKLM "${UNINST_KEY}"

    ; Remove Start Menu shortcuts
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
SectionEnd
