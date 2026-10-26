param(
    [int]$Wait = 18,
    [string]$Out = "$env:TEMP\opencode\ah\emu.png"
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
"@
$jad = Join-Path $PSScriptRoot "..\..\bin\AloneTheHorror.jad"
$emu = Start-Process -FilePath "D:\Java\WTK2.5.2_01\bin\emulator.exe" `
    -ArgumentList @("-Xdevice:DefaultColorPhone", "-Xdescriptor:$jad") -PassThru
Write-Host "emulator pid $($emu.Id)"
Start-Sleep -Seconds $Wait
$p = Get-Process -Id $emu.Id -ErrorAction SilentlyContinue
if (-not $p) { $p = Get-Process -Name emulatorw -ErrorAction SilentlyContinue | Select-Object -First 1 }
if ($p) {
    $h = $p.MainWindowHandle
    [Win]::ShowWindow($h, 5) | Out-Null
    [Win]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Milliseconds 500
    $r = New-Object Win+RECT
    [Win]::GetWindowRect($h, [ref]$r) | Out-Null
    $w = $r.R - $r.L; $ht = $r.B - $r.T
    Write-Host "window $($r.L),$($r.T) ${w}x${ht}"
    if ($w -gt 0 -and $ht -gt 0) {
        $bmp = New-Object System.Drawing.Bitmap($w, $ht)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size($w, $ht)))
        $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host "saved $Out"
    }
} else {
    Write-Host "emulator process not found"
}

