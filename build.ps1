# ---------------------------------------------------------------------------
# build.ps1 - build Alone: The Horror Begins (MIDP 2.0) with the Sun WTK 2.5.2
#             tool chain (JDK 1.8 javac + WTK preverify + jar).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File build.ps1          # build
#   powershell -ExecutionPolicy Bypass -File build.ps1 -Run     # build + run
# ---------------------------------------------------------------------------
param(
    [switch]$Run,
    [string]$Device = "DefaultColorPhone",
    [string]$Version = "1.0.2"
)

$ErrorActionPreference = "Stop"

$JDK  = "D:\Java\jdk1.8.0_131\bin"
$WTK  = "D:\Java\WTK2.5.2_01"
$proj = $PSScriptRoot
$src  = Join-Path $proj "src"
$res  = Join-Path $proj "res"
$cls  = Join-Path $proj "classes"
$pre  = Join-Path $proj "tmpclasses"
$bin  = Join-Path $proj "bin"

$boot = "$WTK\lib\cldcapi11.jar;$WTK\lib\midpapi20.jar;$WTK\lib\mmapi.jar;$WTK\lib\jsr75.jar"

# the emulator keeps the previous JAR locked - stop it before cleaning
Get-Process emulator, emulatorw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*WTK*" -or $_.CommandLine -like "*AloneTheHorror.jad*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Milliseconds 800

foreach ($d in @($cls, $pre, $bin)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    # antivirus and a just-closed emulator can hold handles for a few seconds
    for ($i = 0; $i -lt 20; $i++) {
        try {
            Get-ChildItem $d -Recurse -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction Stop
            break
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
}

$sources = (Get-ChildItem $src -Filter *.java | ForEach-Object { $_.FullName })

Write-Host "[1/4] Compiling (JDK 1.8, -source/-target 1.4, CLDC 1.1 bootclasspath)"
& "$JDK\javac.exe" -source 1.4 -target 1.4 -nowarn -bootclasspath $boot -d $cls $sources
if ($LASTEXITCODE -ne 0) { throw "javac failed ($LASTEXITCODE)" }

Write-Host "[2/4] Preverifying (WTK CLDC preverifier)"
& "$WTK\bin\preverify.exe" -d $pre -classpath $boot $cls
if ($LASTEXITCODE -ne 0) { throw "preverify failed ($LASTEXITCODE)" }

Get-ChildItem $res -File | Where-Object { $_.Extension -in ".png", ".txt", ".mid", ".wav", ".raw", ".map", ".bin", ".jmap" } |
    Copy-Item -Destination $pre -Force

$manifest = @(
    "MIDlet-1: AloneTheHorror, AloneTheHorror.png, horror"
    "MIDlet-Name: AloneTheHorror"
    "MIDlet-Vendor: Centerscope ritsudo"
    "MIDlet-Version: $Version"
    "MicroEdition-Configuration: CLDC-1.1"
    "MicroEdition-Profile: MIDP-2.1"
) -join "`r`n"
[System.IO.File]::WriteAllText((Join-Path $bin "MANIFEST.MF"), $manifest + "`r`n")

Write-Host "[3/4] Packaging JAR"
& "$JDK\jar.exe" cfm (Join-Path $bin "AloneTheHorror.jar") (Join-Path $bin "MANIFEST.MF") -C $pre .
if ($LASTEXITCODE -ne 0) { throw "jar failed ($LASTEXITCODE)" }

$size = (Get-Item (Join-Path $bin "AloneTheHorror.jar")).Length
$jad = @(
    "MIDlet-1: AloneTheHorror, AloneTheHorror.png, horror"
    "MIDlet-Jar-Size: $size"
    "MIDlet-Jar-URL: AloneTheHorror.jar"
    "MIDlet-Name: AloneTheHorror"
    "MIDlet-Vendor: Centerscope ritsudo"
    "MIDlet-Version: $Version"
    "MicroEdition-Configuration: CLDC-1.1"
    "MicroEdition-Profile: MIDP-2.1"
) -join "`r`n"
[System.IO.File]::WriteAllText((Join-Path $bin "AloneTheHorror.jad"), $jad + "`r`n")

Write-Host "[4/4] Done -> bin\AloneTheHorror.jar ($size bytes) + bin\AloneTheHorror.jad"

if ($Run) {
    Write-Host "Launching emulator (device $Device) ..."
    & "$WTK\bin\emulator.exe" -Xdevice:$Device -Xdescriptor:"$bin\AloneTheHorror.jad"
}
