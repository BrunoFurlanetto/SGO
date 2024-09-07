# Lista de branches permitidas para migrações em ambos os bancos
$branches = @("master")

# Verificar o nome da branch atual
$current_branch = git rev-parse --abbrev-ref HEAD

# Função para verificar se a branch atual está na lista de branches permitidas
function BranchInList {
    param (
        [string]$branch
    )

    if ($branches -contains $branch) {
        return $true
    }
    return $false
}

# Verificar se a branch atual está na lista
if (BranchInList -branch $current_branch) {
    Write-Host "Branch atual ($current_branch) esta na lista. Aplicando migracoes no banco de dados local e remoto..." -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2
    Write-Host "Aplicando migrcoes no banco de dados local..." -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2

    # Migrar no banco de dados local
    python manage.py migrate --database=default

    Write-Host "Aplicando migrcoes no banco de dados remoto..." -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2
    # Migrar no banco de dados remoto
    python manage.py migrate --database=remote

    Write-Host "Migracoes aplicadas em ambos os bancos de dados!" -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2
} else {
    Write-Host "Branch atual ($current_branch) não está na lista. Aplicando migrações apenas no banco de dados local." -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2
    # Migrar apenas no banco de dados local
    python manage.py migrate --database=default

    Write-Host "Migrações aplicadas apenas no banco de dados 'default'." -ForegroundColor DarkCyan
    Start-Sleep -Seconds 2
}