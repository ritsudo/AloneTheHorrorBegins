param(
    [string]$OutDir = "$env:TEMP\opencode\ah",
    [string]$Name = "shot"
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class ShotWin {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X,Y; }
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
}
"@
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$h = [ShotWin]::Skin()
if ($h -eq [IntPtr]::Zero) { Write-Host "skin window not found"; exit 1 }
$r = New-Object ShotWin+RECT
[ShotWin]::GetClientRect($h, [ref]$r) | Out-Null
$p = New-Object ShotWin+POINT
[ShotWin]::ClientToScreen($h, [ref]$p) | Out-Null
$w = $r.R; $ht = $r.B
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($p.X, $p.Y, 0, 0, (New-Object System.Drawing.Size($w, $ht)))
# The DefaultColorPhone skin is drawn at client (0,21). Its LCD is at skin
# (37,54), size 240x320. The MIDlet buffer (176x208) is centered inside it.
$screenRect = New-Object System.Drawing.Rectangle(37, 75, 240, 320)
$screen = $bmp.Clone($screenRect, $bmp.PixelFormat)
$screen.Save((Join-Path $OutDir "$Name.screen.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$gameRect = New-Object System.Drawing.Rectangle(69, 136, 176, 208)
$game = $bmp.Clone($gameRect, $bmp.PixelFormat)
$game.Save((Join-Path $OutDir "$Name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "saved $(Join-Path $OutDir "$Name.png") (176x208) and $Name.screen.png (240x320)"
