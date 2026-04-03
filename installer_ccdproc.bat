@echo off
REM Script pour installer ccdproc dans l'environnement conda astroenv

echo ========================================
echo Installation de ccdproc
echo ========================================
echo.

echo Activation de l'environnement astroenv...
call conda activate astroenv

if errorlevel 1 (
    echo ERREUR: Impossible d'activer l'environnement astroenv
    echo Assurez-vous que conda est installé et que l'environnement astroenv existe.
    pause
    exit /b 1
)

echo.
echo Installation de ccdproc>=2.4.0...
python -m pip install "ccdproc>=2.4.0"

if errorlevel 1 (
    echo.
    echo ERREUR lors de l'installation de ccdproc
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation terminee avec succes!
echo ========================================
echo.
echo ccdproc est maintenant installe dans l'environnement astroenv.
echo Vous pouvez relancer NPOAP pour utiliser le pre-processing complet.
echo.
pause
