# Function to check if a port is in use
function Test-PortInUse {
    param($port)
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

# Kill any existing processes on ports 8000 and 5173
if (Test-PortInUse 8000) {
    Write-Host "Killing process on port 8000..."
    Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
}
if (Test-PortInUse 5173) {
    Write-Host "Killing process on port 5173..."
    Stop-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess -Force
}

# Set working directory to script location
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Start backend server
Write-Host "Starting backend server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Start frontend server
Write-Host "Starting frontend server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev"

Write-Host "Servers are starting..."
Write-Host "Backend will be available at: http://localhost:8000"
Write-Host "Frontend will be available at: http://localhost:5173"
Write-Host "Press Ctrl+C in respective windows to stop the servers" 