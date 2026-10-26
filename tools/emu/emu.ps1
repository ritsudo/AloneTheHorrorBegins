param(
    [switch]$Launch,
    [int]$StartWait = 16,
    [string]$Keys = "",
    [int]$KeyDelay = 500,
    [int]$EndWait = 2,
    [switch]$ClickLaunch,
    [string]$Out = "$env:TEMP\opencode\ah\shot.png"
)$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class Dev {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr SetFocus(IntPtr h);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, IntPtr extra);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
    public static IntPtr Skin() {
        IntPtr found = IntPtr.Zero;
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (!IsWindowVisible(h)) return true;
            var c = new StringBuilder(256); GetClassName(h, c, 256);
            var t = new StringBuilder(256); GetWindowText(h, t, 256);
            if (c.ToString() == "SunAwtFrame" && t.ToString().Contains("DefaultColorPhone")) { found = h; return false; }
            return true;
        }, IntPtr.Zero);
        return found;
    }
    public static void Tap(byte vk) {
        keybd_event(vk, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(60);
        keybd_event(vk, 0, 2, IntPtr.Zero);
    }
    public static void Click(int x, int y) {
        SetCursorPos(x, y); System.Threading.Thread.Sleep(80);
        mouse_event(0x0002, 0, 0, 0, IntPtr.Zero);
        mouse_event(0x0004, 0, 0, 0, IntPtr.Zero);
    }
}
"@

$running = Get-Process emulator,emulatorw -ErrorAction SilentlyContinue
if ($Launch -or -not $running) {
    $jad = Join-Path $PSScriptRoot "..\..\bin\AloneTheHorror.jad"
    Start-Process -FilePath "D:\Java\WTK2.5.2_01\bin\emulator.exe" `
        -ArgumentList @("-Xdevice:DefaultColorPhone", "-Xdescriptor:$jad") | Out-Null
    Write-Host "waiting ${StartWait}s for emulator..."
    Start-Sleep -Seconds $StartWait
}

$h = [Dev]::Skin()
if ($h -eq [IntPtr]::Zero) { Write-Host "skin window not found"; exit 1 }
$r0 = New-Object Dev+RECT
[Dev]::GetWindowRect($h, [ref]$r0) | Out-Null
[Dev]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 300
[Dev]::Click($r0.L + 150, $r0.T + 220)
Start-Sleep -Milliseconds 200
[Dev]::SetFocus($h) | Out-Null
if ($ClickLaunch) {
    [Dev]::Click($r0.L + 250, $r0.T + 405)
    Start-Sleep -Seconds 3
}

$map = @{
    "up"=0x26; "down"=0x28; "left"=0x25; "right"=0x27;
    "enter"=0x0D; "f1"=0x70; "f2"=0x71; "f3"=0x72; "esc"=0x1B;
    "0"=0x30; "1"=0x31; "2"=0x32; "3"=0x33; "4"=0x34; "5"=0x35;
    "6"=0x36; "7"=0x37; "8"=0x38; "9"=0x39; "star"=0x6A; "pound"=0x6B
}
if ($Keys -ne "") {
    foreach ($k in $Keys.Split(",")) {
        $k2 = $k.Trim().ToLower()
        if ($map.ContainsKey($k2)) {
            [Dev]::Tap([byte]$map[$k2])
            Start-Sleep -Milliseconds $KeyDelay
        } else {
            Write-Host "unknown key '$k2'"
        }
    }
}
Start-Sleep -Seconds $EndWait
[Dev]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 300
$r = New-Object Dev+RECT
[Dev]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size($w, $ht)))
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "saved $Out ($w x $ht)"

