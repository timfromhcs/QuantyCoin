; QuantyCoin v4.0 Combined Suite NSIS Installer Script
!define PRODUCT_NAME "QuantyCoin Combined Suite"
!define PRODUCT_VERSION "4.0.0"
!define PRODUCT_PUBLISHER "QuantyCoin Core Contributors"
!define PRODUCT_WEB_SITE "https://quantycoin.org"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor /SOLID lzma

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "..\..\share\pixmaps\quantycoin.ico"
!define MUI_UNICON "..\..\share\pixmaps\quantycoin.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\COPYING"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\..\dist\windows\QuantyCoin-CombinedSuite-Setup-v4.0.exe"
InstallDir "$PROGRAMFILES64\QuantyCoin"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File /r "..\..\dist\bin\suite\*.*"
  CreateDirectory "$SMPROGRAMS\QuantyCoin"
  CreateShortCut "$SMPROGRAMS\QuantyCoin\QuantyCoin Suite.lnk" "$INSTDIR\QuantyCoinSuite.exe"
  CreateShortCut "$DESKTOP\QuantyCoin Suite.lnk" "$INSTDIR\QuantyCoinSuite.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
SectionEnd
