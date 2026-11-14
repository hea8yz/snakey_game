# SNAKEY updater: downloads changed/new files from the GitHub repo (branch main)
# into the game folder. Launched by update.bat (same folder).
# Only files listed in MANIFEST.txt are touched. Save file (~/.snakey_save.json)
# and your own files (assets, mods) are never removed or overwritten
# unless they are part of the manifest.
param([string]$RepoBase = "https://raw.githubusercontent.com/hea8yz/snakey_game/main/")

$ErrorActionPreference = "Stop"
# GitHub requires TLS 1.2 on older Windows PowerShell defaults
try {
    [Net.ServicePointManager]::SecurityProtocol = `
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch { }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root

function VersionTuple([string]$v) {
    try {
        $v = $v.Trim().TrimStart("v")
        return @($v.Split(".") | ForEach-Object { [int]$_ })
    } catch { return @(0) }
}

function CompareVersions($a, $b) {
    $ta = VersionTuple $a
    $tb = VersionTuple $b
    $n = [Math]::Max($ta.Count, $tb.Count)
    for ($i = 0; $i -lt $n; $i++) {
        $x = 0; if ($i -lt $ta.Count) { $x = $ta[$i] }
        $y = 0; if ($i -lt $tb.Count) { $y = $tb[$i] }
        if ($x -gt $y) { return 1 }
        if ($x -lt $y) { return -1 }
    }
    return 0
}

Write-Host ""
Write-Host "==========================================="
Write-Host "  SNAKEY updater (check + update from GitHub)"
Write-Host "==========================================="
Write-Host ""

$wc = New-Object System.Net.WebClient
try {
    $remoteVer = $wc.DownloadString($RepoBase + "VERSION").Trim()
} catch {
    Write-Host "[ERROR] Could not reach GitHub (no internet?)." -ForegroundColor Red
    exit 1
}
$localVer = "0"
if (Test-Path -LiteralPath "VERSION") {
    $localVer = (Get-Content -LiteralPath "VERSION" -Raw).Trim()
}
Write-Host ("Local version : " + $localVer)
Write-Host ("Latest version: " + $remoteVer)
Write-Host ""

if ((CompareVersions $remoteVer $localVer) -le 0) {
    Write-Host "You already have the latest version. Nothing to update." -ForegroundColor Green
    exit 0
}

try {
    $manifest = $wc.DownloadString($RepoBase + "MANIFEST.txt")
} catch {
    Write-Host "[ERROR] Could not download MANIFEST.txt." -ForegroundColor Red
    exit 1
}

$files = @($manifest -split "`r?`n" | ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and (-not $_.StartsWith("#")) })

$updated = 0; $added = 0; $unchanged = 0; $failed = 0
foreach ($f in $files) {
    # safety: only plain files in the game folder
    if ($f -match "[/\\]" -or $f.StartsWith(".")) { continue }
    $tmp = Join-Path $env:TEMP ("snakey_up_" + [System.Guid]::NewGuid().ToString("N") + ".tmp")
    try {
        $wc.DownloadFile($RepoBase + $f, $tmp)
    } catch {
        Write-Host ("  [!] Download failed: " + $f) -ForegroundColor Red
        $failed++
        continue
    }
    if ((Test-Path -LiteralPath $f) -and
        ((Get-FileHash -LiteralPath $f -Algorithm MD5).Hash -eq
         (Get-FileHash -LiteralPath $tmp -Algorithm MD5).Hash)) {
        $unchanged++
        Remove-Item -LiteralPath $tmp -Force
        continue
    }
    if ($f -eq "update.bat") {
        # update.bat is currently running -> do not touch it while it works.
        # Save the new one nearby and tell the user how to finish the swap.
        Copy-Item -LiteralPath $tmp -Destination "update.new.bat" -Force
        Remove-Item -LiteralPath $tmp -Force
        Write-Host "  [U] update.bat -> saved as update.new.bat" -ForegroundColor Yellow
        Write-Host "      (close this window, delete old update.bat," -ForegroundColor Yellow
        Write-Host "       then rename update.new.bat to update.bat)" -ForegroundColor Yellow
        $updated++
        continue
    }
    $existed = Test-Path -LiteralPath $f
    Move-Item -Force -Path $tmp -Destination $f
    if ($existed) {
        $updated++
        Write-Host ("  [U] " + $f) -ForegroundColor Yellow
    } else {
        $added++
        Write-Host ("  [+] " + $f + "  (new)") -ForegroundColor Green
    }
}

Write-Host ""
Write-Host ("Done!  Updated: " + $updated + "   Added: " + $added +
            "   Unchanged: " + $unchanged + "   Failed: " + $failed)
if ($failed -gt 0) {
    Write-Host "Some files failed to download - just run update.bat again." -ForegroundColor Red
}
Write-Host "Now start the game (snakey_main.py or SNAKEY.exe)."
exit 0
