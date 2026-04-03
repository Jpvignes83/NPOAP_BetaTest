@echo off
REM Script batch pour lancer les tests de l'application NPOAP
REM Utilise l'environnement conda astroenv

echo Activation de l'environnement astroenv...
call conda activate astroenv

if errorlevel 1 (
    echo Erreur: Impossible d'activer l'environnement astroenv
    echo Essayez de lancer: conda activate astroenv
    pause
    exit /b 1
)

echo.
echo Lancement des tests...
echo.

python test_application_launch.py

if errorlevel 1 (
    echo.
    echo Les tests ont detecte des erreurs. Verifiez les details ci-dessus.
    pause
    exit /b 1
) else (
    echo.
    echo Tous les tests sont passes avec succes !
    pause
)
