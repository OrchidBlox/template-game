param(
    [string]$ProjectName
)

$repoRoot = (Get-Location).Path

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    try {
        $remote = git -C $repoRoot remote get-url origin 2>$null
        if (-not [string]::IsNullOrWhiteSpace($remote)) {
            $remote = $remote.TrimEnd('/')
            $ProjectName = Split-Path -Leaf $remote
            $ProjectName = [System.IO.Path]::GetFileNameWithoutExtension($ProjectName)
        }
    } catch {
        $ProjectName = $null
    }
}

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    $ProjectName = Split-Path -Leaf $repoRoot
}

$ProjectName = $ProjectName.Trim()
$ProjectName = $ProjectName -replace '\s+', '-'
$ProjectName = $ProjectName -replace '[^A-Za-z0-9_.-]', '-'
$ProjectName = $ProjectName.Trim('-')

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    throw "A valid project name is required."
}

$jsonPath = Join-Path $repoRoot 'default.project.json'
if (Test-Path $jsonPath) {
    $json = Get-Content -Path $jsonPath -Raw
    $json = [regex]::Replace($json, '"name"\s*:\s*"[^"]*"', '"name": "' + $ProjectName + '"', 1)
    Set-Content -Path $jsonPath -Value $json -NoNewline
    Write-Host "Updated $jsonPath to use '$ProjectName'"
} else {
    Write-Warning "default.project.json not found at $jsonPath"
}

$readmePath = Join-Path $repoRoot 'README.md'
if (Test-Path $readmePath) {
    $readme = Get-Content -Path $readmePath -Raw
    $readme = $readme -replace 'template-game', $ProjectName
    $readme = $readme -replace 'Item-of-Adventure', $ProjectName
    Set-Content -Path $readmePath -Value $readme -NoNewline
    Write-Host "Updated $readmePath to use '$ProjectName'"
} else {
    Write-Warning "README.md not found at $readmePath"
}

Write-Host "Project renamed to: $ProjectName"
Write-Host "Next step: git remote set-url origin https://github.com/<user>/$ProjectName.git"
