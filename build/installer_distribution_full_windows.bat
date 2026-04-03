@echo off
REM ===================================================================
REM Rétro-compatibilité — profil « full »
REM L’installation unifiée se fait via INSTALLER_NPOAP_ASTROENV_WINDOWS.bat
REM ===================================================================
call "%~dp0INSTALLER_NPOAP_ASTROENV_WINDOWS.bat"
exit /b %errorlevel%
