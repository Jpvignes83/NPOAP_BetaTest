@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
REM ===================================================================
REM NPOAP — Installation dans l'environnement Conda « astroenv »
REM ===================================================================
REM À placer à la racine de la distribution (main.py, requirements.txt).
REM Tous les profils (full, reduction, exoplanets, etc.) utilisent le même
REM environnement conda « astroenv » (Python 3.11) et le requirements.txt
REM fourni avec cette distribution.
REM
REM Prérequis : Miniconda ou Anaconda ; https://docs.conda.io/en/latest/miniconda.html
REM Optionnel MSVC Build Tools pour PHOEBE — voir docs\MANUEL_INSTALLATION.md
REM Paquets Git (ex. ezpadova) : Git dans le PATH
REM ===================================================================

title NPOAP — Installation conda astroenv

cd /d "%~dp0"

echo.
echo ============================================================
echo   NPOAP — Installation environnement conda « astroenv »
echo ============================================================
echo.
echo Dossier : %CD%
echo.

if not exist "requirements.txt" (
    echo ERREUR: requirements.txt introuvable.
    pause
    exit /b 1
)

REM --- Localiser conda (exe de préférence pour « info --base ») ---
set "CONDA_EXE="
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set "CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe"
if not defined CONDA_EXE if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" set "CONDA_EXE=%USERPROFILE%\anaconda3\Scripts\conda.exe"
if not defined CONDA_EXE if exist "%LocalAppData%\miniconda3\Scripts\conda.exe" set "CONDA_EXE=%LocalAppData%\miniconda3\Scripts\conda.exe"
if not defined CONDA_EXE (
    where conda >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%C in ('where conda 2^>nul') do (
            set "CAND=%%C"
            if /i "!CAND:~-9!"=="\conda.bat" (
                for %%P in ("!CAND!\..\Scripts\conda.exe") do if exist "%%~fP" set "CONDA_EXE=%%~fP"
            )
            if /i "!CAND:~-10!"=="\conda.exe" set "CONDA_EXE=!CAND!"
            if defined CONDA_EXE goto :found_conda
        )
    )
)
:found_conda
if not defined CONDA_EXE (
    echo ERREUR: conda introuvable.
    echo Installez Miniconda ^(Windows, Python 3.11^) :
    echo   https://docs.conda.io/en/latest/miniconda.html
    echo Puis rouvrez ce script ^(PATH ou relance du terminal^).
    pause
    exit /b 1
)

for /f "delims=" %%B in ('"!CONDA_EXE!" info --base 2^>nul') do set "CONDA_ROOT=%%B"
if not defined CONDA_ROOT (
    echo ERREUR: impossible de déterminer le répertoire de base conda.
    pause
    exit /b 1)

echo Conda : !CONDA_EXE!
echo Base  : !CONDA_ROOT!
"!CONDA_EXE!" --version
echo.

set "ASTRO_PY=!CONDA_ROOT!\envs\astroenv\python.exe"
if not exist "!ASTRO_PY!" (
    echo Création de l'environnement « astroenv » ^(python=3.11^)...
    "!CONDA_EXE!" create -n astroenv python=3.11 -y
    if errorlevel 1 (
        echo ERREUR: conda create -n astroenv a échoué.
        pause
        exit /b 1
    )
) else (
    echo Environnement « astroenv » déjà présent.
)

if not exist "!CONDA_ROOT!\Scripts\activate.bat" (
    echo ERREUR: activate.bat introuvable.
    pause
    exit /b 1
)

call "!CONDA_ROOT!\Scripts\activate.bat" astroenv
if errorlevel 1 (
    echo ERREUR: impossible d'activer astroenv.
    pause
    exit /b 1
)

python -c "import sys; raise SystemExit(0 if sys.version_info>=(3,11) else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo ATTENTION: le Python d'astroenv est ^< 3.11. Commandes conseillées :
    echo   conda activate astroenv
    echo   conda install "python>=3.11" -y
    echo.
    set /p CONTINUE="Continuer quand même pip install -r requirements.txt ? (O/N): "
    if /i not "!CONTINUE!"=="O" exit /b 1
)

echo.
echo Mise à jour de pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERREUR: mise à jour pip.
    pause
    exit /b 1
)

echo.
echo Installation des paquets depuis requirements.txt...
echo ^(selon le profil de cette distribution — peut prendre plusieurs minutes^)
echo.
python -m pip install -r "requirements.txt"
set "PIP_RC=!errorlevel!"

echo.
echo ============================================================
if !PIP_RC! neq 0 (
    echo   Installation pip terminée avec erreurs — voir messages ci-dessus.
    echo   PHOEBE : souvent Microsoft C++ Build Tools requis.
) else (
    echo   Installation pip réussie dans « astroenv ».
)
echo ============================================================
echo.
echo Lancement : double-cliquez sur lancement.bat
echo.
pause
exit /b !PIP_RC!
