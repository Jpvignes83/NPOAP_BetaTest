@echo off
REM Script batch pour construire une distribution NPOAP
REM Usage: build.bat <profile_name>
REM Exemples: build.bat exoplanets
REM           build.bat full

if "%1"=="" (
    echo Usage: build.bat ^<profile_name^>
    echo.
    echo Profils disponibles:
    echo   - exoplanets: Distribution specialisee exoplanetes
    echo   - asteroids: Distribution specialisee asteroides
    echo   - binary_stars: Distribution etoiles doubles (Binaires + ELI)
    echo   - spectroscopy: Distribution spectroscopie
    echo   - full: Distribution complete
    exit /b 1
)

set PROFILE=%1
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Construction de la distribution: %PROFILE%
echo.

REM Chercher Python dans plusieurs emplacements communs
set PYTHON_CMD=
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=py
        ) else (
            echo Erreur: Python n'est pas trouve dans le PATH.
            echo Veuillez installer Python ou l'ajouter au PATH.
            exit /b 1
        )
    )
)

echo Utilisation de: %PYTHON_CMD%
echo.

REM Vérifier que le fichier existe
if not exist "build_distribution.py" (
    echo Erreur: build_distribution.py non trouve dans %SCRIPT_DIR%
    exit /b 1
)

REM Exécuter le script Python
%PYTHON_CMD% build_distribution.py %PROFILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Distribution construite avec succes!
    echo.
    echo Distribution disponible dans: build\distributions\%PROFILE%
) else (
    echo.
    echo Erreur lors de la construction de la distribution.
    echo Code d'erreur: %ERRORLEVEL%
    exit /b 1
)
