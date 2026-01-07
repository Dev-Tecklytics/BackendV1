# Quick Backend Connection Test Script
# Run this to verify your backend is working

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  IAAP Backend Connection Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Check if backend is running
Write-Host "[1/3] Testing backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method Get -ErrorAction Stop
    Write-Host "SUCCESS: Backend is running!" -ForegroundColor Green
    Write-Host "  Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
}
catch {
    Write-Host "ERROR: Backend is not responding!" -ForegroundColor Red
    Write-Host "  Make sure backend is running on port 8000" -ForegroundColor Red
    Write-Host "  Run: python -m uvicorn app.main:app --reload" -ForegroundColor Yellow
    exit
}

# Test 2: Check API documentation
Write-Host "`n[2/3] Checking API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method Get -ErrorAction Stop
    Write-Host "SUCCESS: API docs are accessible!" -ForegroundColor Green
    Write-Host "  URL: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
}
catch {
    Write-Host "WARNING: Could not access API docs" -ForegroundColor Yellow
}

# Test 3: List available endpoints
Write-Host "`n[3/3] Fetching available endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/openapi.json" -Method Get -ErrorAction Stop
    $endpoints = $response.paths.PSObject.Properties | Select-Object -ExpandProperty Name
    Write-Host "SUCCESS: Found $($endpoints.Count) API endpoints!" -ForegroundColor Green
    Write-Host "`nKey endpoints:" -ForegroundColor Cyan
    $keyEndpoints = $endpoints | Where-Object { $_ -match "auth|user|analysis" } | Select-Object -First 10
    $keyEndpoints | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
}
catch {
    Write-Host "WARNING: Could not fetch endpoint list" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nBackend Status: " -NoNewline
Write-Host "READY" -ForegroundColor Green
Write-Host "Backend URL: " -NoNewline
Write-Host "http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Docs: " -NoNewline
Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Start your frontend with npm run dev"
Write-Host "2. Configure frontend .env: VITE_API_URL=http://127.0.0.1:8000"
Write-Host "3. Open test page in browser"
Write-Host "4. Test registration and login"
Write-Host "`n========================================`n" -ForegroundColor Cyan
