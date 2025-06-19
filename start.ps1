# Comprueba si se ejecuta como administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "¡Debes ejecutar este script como Administrador!" -ForegroundColor Red
    Pause
    exit 1
}

$hostLine = "127.0.0.1 tfc.local"
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

# Añadir la línea al archivo hosts si no existe
Write-Host "Configurando hosts de Windows..."
$hostsContent = Get-Content $hostsPath -Raw
if ($hostsContent -notmatch [regex]::Escape($hostLine)) {
    Add-Content -Path $hostsPath -Value $hostLine
    Write-Host "Línea añadida al archivo hosts."
} else {
    Write-Host "La línea ya existe en el archivo hosts."
}

# Detener y eliminar contenedores y volúmenes previos
Write-Host ">> Limpiando contenedores previos..."
docker compose down -v

# Levantar los servicios (build incluido)
Write-Host ">> Levantando servicios con Docker Compose..."
docker compose up --build -d

# Esperar a que MySQL esté healthy
Write-Host ">> Esperando a que MySQL esté completamente preparado..."
$maxTries = 60
for ($i = 1; $i -le $maxTries; $i++) {
    $mysqlId = docker compose ps -q mysql
    if (-not $mysqlId) {
        Write-Host "No se encuentra el contenedor MySQL aún... intento ($i/$maxTries)"
        Start-Sleep -Seconds 2
        continue
    }
    $status = docker inspect --format='{{.State.Health.Status}}' $mysqlId 2>$null
    if ($status -eq "healthy") {
        Write-Host "MySQL está healthy."
        break
    }
    Write-Host "Esperando a que MySQL esté healthy... ($i/$maxTries) Estado actual: $status"
    Start-Sleep -Seconds 2
}

# Mostrar estado de los contenedores
Write-Host ">> Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n¡Todo levantado! Accede a:"
Write-Host "  http://tfc.local"
Pause
