@echo off
setlocal enabledelayedexpansion
REM Script pour créer une archive ZIP de NPOAP
REM Exclut les fichiers temporaires et les dossiers non nécessaires

echo ============================================================
echo   Creation de l'archive ZIP de NPOAP
echo ============================================================
echo.

REM Obtenir le nom du dossier actuel
for %%I in (.) do set CURRENT_DIR=%%~nxI

REM Créer un nom d'archive avec la date et l'heure
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set mytime=%mytime: =0%
set ARCHIVE_NAME=NPOAP_%mydate%_%mytime%.zip

echo Nom de l'archive: %ARCHIVE_NAME%
echo.

REM Vérifier si l'archive existe déjà
if exist "%ARCHIVE_NAME%" (
    echo L'archive %ARCHIVE_NAME% existe deja.
    set /p OVERWRITE="Voulez-vous l'ecraser? (O/N): "
    if /i not "%OVERWRITE%"=="O" (
        echo Operation annulee.
        pause
        exit /b 0
    )
    del "%ARCHIVE_NAME%"
    echo.
)

echo Creation de l'archive en cours...
echo.

REM Créer un script PowerShell temporaire
set PS_SCRIPT=%TEMP%\creer_archive_%RANDOM%.ps1
(
echo $ErrorActionPreference = 'Stop'
echo $source = Get-Location
echo $archivePath = Join-Path $source '%ARCHIVE_NAME%'
echo if ^(Test-Path $archivePath^) { Remove-Item $archivePath -Force }
echo.
echo # Fonction pour vérifier si un chemin doit être exclu
echo function ShouldExclude ^($itemPath, $itemName^) {
echo     $relativePath = $itemPath.Substring^($source.Path.Length + 1^)
echo     if ^($relativePath -like '*__pycache__*'^) { return $true }
echo     if ^($relativePath -like '*.git*'^) { return $true }
echo     if ^($relativePath -like '*.conda*'^) { return $true }
echo     if ^($relativePath -like '*.cache*'^) { return $true }
echo     if ^($relativePath -like 'logs\*'^) { return $true }
echo     if ^($relativePath -like '*.vscode*'^) { return $true }
echo     if ^($relativePath -like '*.idea*'^) { return $true }
echo     if ^($itemName -like '*.pyc'^) { return $true }
echo     if ^($itemName -like '*.pyo'^) { return $true }
echo     if ^($itemName -like '*.pyd'^) { return $true }
echo     if ^($itemName -like '*.log'^) { return $true }
echo     if ^($itemName -like '*.zip'^) { return $true }
echo     if ^($itemName -eq '.DS_Store'^) { return $true }
echo     if ^($itemName -eq 'Thumbs.db'^) { return $true }
echo     if ^($itemPath -eq $archivePath^) { return $true }
echo     return $false
echo }
echo.
echo # Créer une liste de tous les fichiers à inclure avec leurs chemins relatifs
echo $filesToAdd = @^(^)
echo Get-ChildItem -Path $source -Recurse ^| Where-Object {
echo     $fullName = $_.FullName
echo     -not ^(ShouldExclude $fullName $_.Name^) -and -not $_.PSIsContainer
echo } ^| ForEach-Object {
echo     $relativePath = $_.FullName.Substring^($source.Path.Length + 1^)
echo     $filesToAdd += @{Source=$_.FullName; RelativePath=$relativePath}
echo }
echo.
echo # Créer un dossier temporaire avec la structure préservée
echo $guid = [System.Guid]::NewGuid^(^).ToString^(^)
echo $tempDir = Join-Path $env:TEMP "npoap_archive_$guid"
echo New-Item -ItemType Directory -Path $tempDir -Force ^| Out-Null
echo $projectName = Split-Path -Leaf $source
echo $tempProjectDir = Join-Path $tempDir $projectName
echo New-Item -ItemType Directory -Path $tempProjectDir -Force ^| Out-Null
echo try {
echo     # Copier les fichiers en préservant la structure
echo     foreach ^($file in $filesToAdd^) {
echo         $destPath = Join-Path $tempProjectDir $file.RelativePath
echo         $destDir = Split-Path -Parent $destPath
echo         if ^(-not ^(Test-Path $destDir^)^) {
echo             New-Item -ItemType Directory -Path $destDir -Force ^| Out-Null
echo         }
echo         Copy-Item -Path $file.Source -Destination $destPath -Force
echo     }
echo     # Créer l'archive depuis le dossier temporaire
echo     Add-Type -AssemblyName System.IO.Compression.FileSystem
echo     $compressionLevel = [System.IO.Compression.CompressionLevel]::Optimal
echo     [System.IO.Compression.ZipFile]::CreateFromDirectory^($tempProjectDir, $archivePath, $compressionLevel, $false^)
echo     Write-Host 'OK'
echo } catch {
echo     Write-Host "ERREUR: $_"
echo     exit 1
echo } finally {
echo     # Nettoyer le dossier temporaire
echo     if ^(Test-Path $tempDir^) {
echo         Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
echo     }
echo }
) > "%PS_SCRIPT%"

REM Exécuter le script PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

REM Supprimer le script temporaire
del "%PS_SCRIPT%" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   Archive creee avec succes!
    echo ============================================================
    echo.
    echo Fichier: %ARCHIVE_NAME%
    echo.
    
    REM Afficher la taille de l'archive avec PowerShell
    for /f "delims=" %%A in ('powershell -NoProfile -Command "(Get-Item '%ARCHIVE_NAME%').Length / 1MB"') do set SIZE_MB=%%A
    if defined SIZE_MB (
        echo Taille: !SIZE_MB! MB ^(environ^)
    ) else (
        REM Méthode alternative si PowerShell échoue
        for %%F in ("%ARCHIVE_NAME%") do (
            set SIZE_BYTES=%%~zF
            if defined SIZE_BYTES (
                set /a SIZE_MB=!SIZE_BYTES! / 1048576
                echo Taille: !SIZE_MB! MB ^(environ^)
            ) else (
                echo Taille: non disponible
            )
        )
    )
    
    echo.
    echo L'archive est prete pour distribution.
) else (
    echo.
    echo ============================================================
    echo   ERREUR lors de la creation de l'archive
    echo ============================================================
    echo.
    echo Code d'erreur: %ERRORLEVEL%
)

echo.
pause
