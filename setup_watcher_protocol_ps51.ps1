
# Watcher Protocol Bootstrap Script for Windows 11 Home (PowerShell 5.1 compatible)
Write-Host "🦇 Watcher Protocol Setup Starting..."

# Step 1: WSL Check
try {
    wsl -l
    Write-Host "✅ WSL is already installed"
} catch {
    Write-Host "Installing WSL and Ubuntu..."
    wsl --install -d Ubuntu
    Read-Host "⚠️ Please complete Ubuntu setup and then press Enter to continue"
}

# Step 2: Check for Chocolatey
$chocoCommand = Get-Command choco.exe -ErrorAction SilentlyContinue
if (-not $chocoCommand) {
    Write-Host "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "✅ Chocolatey is already installed"
}

# Step 3: Install tools
$packages = @("git", "python", "nodejs", "docker-desktop", "vscode")
foreach ($pkg in $packages) {
    if (-not (Get-Command $pkg -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $pkg..."
        choco install -y $pkg
    } else {
        Write-Host "✅ $pkg already installed"
    }
}

# Step 4: Project Setup
$projectPath = "$env:USERPROFILE\projects\watcher_protocol"
if (-not (Test-Path $projectPath)) {
    git clone https://github.com/your-username/watcher_protocol.git $projectPath
} else {
    Write-Host "✅ Project directory already exists"
}

# Step 5: Install Python dependencies in WSL
Write-Host "Setting up Python environment in WSL..."
wsl bash -c "cd /mnt/c/Users/$env:USERNAME/projects/watcher_protocol && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"

# Step 6: Node setup
Write-Host "Installing frontend dependencies..."
cd $projectPath
npm install

# Final Note
Write-Host "✅ Setup complete! Open Docker Desktop and make sure WSL integration is enabled."
Write-Host "🚀 Launch services with: docker-compose up --build"
