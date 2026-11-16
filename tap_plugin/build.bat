@echo off
setlocal
cd /d "%~dp0"
set LOG=%~dp0build_output.txt
echo MixBuddy Tap build %date% %time% > "%LOG%"

where cargo >nul 2>&1
if errorlevel 1 (
  echo Rust is not installed or not on PATH. Install it from https://rustup.rs then run this again.
  echo NO_CARGO >> "%LOG%"
  pause & exit /b 1
)
rustc --version >> "%LOG%" 2>&1
rustup show active-toolchain >> "%LOG%" 2>&1

echo Building MixBuddy Tap (first build downloads dependencies, takes a few minutes)...
powershell -NoProfile -Command "cargo run --package xtask --release -- bundle mixbuddy_tap --release 2>&1 | Tee-Object -FilePath '%LOG%' -Append"
if not exist "target\bundled\MixBuddy Tap.vst3" (
  echo.
  echo BUILD FAILED. If the log says "link.exe not found", install Visual Studio Build Tools
  echo with "Desktop development with C++", then run this again.
  echo BUILD_FAILED >> "%LOG%"
  pause & exit /b 1
)
echo BUILD_OK >> "%LOG%"

echo.
echo Installing into the shared plugin folders (asks for admin rights)...
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-Command',\"New-Item -ItemType Directory -Force 'C:\Program Files\Common Files\VST3','C:\Program Files\Common Files\CLAP' | Out-Null; Copy-Item -Recurse -Force '%~dp0target\bundled\MixBuddy Tap.vst3' 'C:\Program Files\Common Files\VST3\'; Copy-Item -Force '%~dp0target\bundled\MixBuddy Tap.clap' 'C:\Program Files\Common Files\CLAP\'\""
if exist "C:\Program Files\Common Files\VST3\MixBuddy Tap.vst3" (
  echo INSTALLED >> "%LOG%"
  echo Installed. In FL: Options ^> Manage plugins ^> Find plugins, then load "MixBuddy Tap".
) else (
  echo NOT_INSTALLED >> "%LOG%"
  echo Not installed automatically. Copy target\bundled\MixBuddy Tap.vst3 into
  echo C:\Program Files\Common Files\VST3 yourself.
)
echo.
pause
