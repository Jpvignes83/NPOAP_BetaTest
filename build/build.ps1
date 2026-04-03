# Script PowerShell pour construire une distribution NPOAP
# Usage: .\build.ps1 <profile_name>
# Exemples: .\build.ps1 exoplanets
#           .\build.ps1 full

param(
    [Parameter(Mandatory=$false)]
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrEmpty($Profile)) {
    Write-Host "Usage: .\build.ps1 <profile_name>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Profils disponibles:" -ForegroundColor Cyan
    Write-Host "  - exoplanets: Distribution spécialisée exoplanètes"
    Write-Host "  - full: Distribution complète"
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Construction de la distribution: $Profile" -ForegroundColor Green
Write-Host ""

# Chercher Python
$PythonCmd = $null

# Essayer python
try {
    $null = Get-Command python -ErrorAction Stop
    $PythonCmd = "python"
} catch {
    # Essayer python3
    try {
        $null = Get-Command python3 -ErrorAction Stop
        $PythonCmd = "python3"
    } catch {
        # Essayer py (Windows Python Launcher)
        try {
            $null = Get-Command py -ErrorAction Stop
            $PythonCmd = "py"
        } catch {
            Write-Host "Erreur: Python n'est pas trouvé dans le PATH." -ForegroundColor Red
            Write-Host "Veuillez installer Python ou l'ajouter au PATH." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "Utilisation de: $PythonCmd" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le fichier existe
if (-not (Test-Path "build_distribution.py")) {
    Write-Host "Erreur: build_distribution.py non trouvé dans $ScriptDir" -ForegroundColor Red
    exit 1
}

# Exécuter le script Python
try {
    & $PythonCmd build_distribution.py $Profile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Distribution construite avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Distribution disponible dans: build\distributions\$Profile" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "Erreur lors de la construction de la distribution." -ForegroundColor Red
        Write-Host "Code d'erreur: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Erreur lors de l'exécution du script Python:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
