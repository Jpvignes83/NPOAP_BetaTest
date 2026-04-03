@echo off
REM Script pour lancer NPOAP avec l'environnement conda astroenv activé

echo Activation de l'environnement astroenv...
call conda activate astroenv

if errorlevel 1 (
    echo ERREUR: Impossible d'activer l'environnement astroenv
    pause
    exit /b 1
)

echo.
echo Lancement de NPOAP...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo ERREUR lors du lancement de NPOAP
    pause
)






