# drive.ps1 - launch the MIDlet in the WTK emulator and capture the LCD.
# Usage: powershell -File tools\emu\drive.ps1 -Keys "5,5" -Name menu -WaitMs 3000
param(
    [string]$Keys = "",
    [int]$KeyDelay = 700,
    [int]$WaitMs = 2500,
    [string]$Name = "shot",
    [switch]$Launch
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class Dev2 {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr SetFocus(IntPtr h);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, IntPtr extra);
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
    public static void Down(byte vk) {
        keybd_event(vk, 0, 0, IntPtr.Zero);
    }
    public static void Up(byte vk) {
        keybd_event(vk, 0, 2, IntPtr.Zero);
    }
}
"@
$wd = Join-Path $PSScriptRoot "..\..\docs\reference\emu2"
New-Item -ItemType Directory -Force -Path $wd | Out-Null

if ($Launch) {
    $jad = Join-Path $PSScriptRoot "..\..\bin\AloneTheHorror.jad"
    if (-not (Get-Process emulator,emulatorw -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath "D:\Java\WTK2.5.2_01\bin\emulator.exe" `
            -ArgumentList @("-Xdevice:DefaultColorPhone", "-Xdescriptor:$jad") | Out-Null
        Start-Sleep -Seconds 14
    }
}

$h = [Dev2]::Skin()
if ($h -eq [IntPtr]::Zero) { Write-Host "skin window not found"; exit 1 }
$r = New-Object Dev2+RECT
[Dev2]::GetWindowRect($h, [ref]$r) | Out-Null
[Dev2]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 300
[Dev2]::SetFocus($h) | Out-Null

if ($Launch) {
    # AMS launch confirmation: press Enter / fire on the soft button
    [Dev2]::Tap(0x0D)
    Start-Sleep -Seconds 6
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
        $hold = 0
        if ($k2.Contains(":")) {
            $parts = $k2.Split(":")
            $k2 = $parts[0]
            $hold = [int]$parts[1]
        }
        if ($map.ContainsKey($k2)) {
            if ($hold -gt 0) {
                [Dev2]::Down([byte]$map[$k2])
                Start-Sleep -Milliseconds $hold
                [Dev2]::Up([byte]$map[$k2])
            } else {
                [Dev2]::Tap([byte]$map[$k2])
            }
            Start-Sleep -Milliseconds $KeyDelay
        } else {
            Write-Host "unknown key '$k2'"
        }
    }
}
Start-Sleep -Milliseconds $WaitMs

# capture: LCD 240x320 at window offset (41,144); MIDlet 176x208 centered
$w = $r.R - $r.L; $hh = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size $w, $hh))
$lcd = $bmp.Clone((New-Object System.Drawing.Rectangle 41,144,240,320), $bmp.PixelFormat)
$lcd.Save((Join-Path $wd "$Name.lcd.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$game = $bmp.Clone((New-Object System.Drawing.Rectangle 73,162,176,208), $bmp.PixelFormat)
$game.Save((Join-Path $wd "$Name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "saved $Name.png"
