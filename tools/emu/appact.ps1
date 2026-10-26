Add-Type -AssemblyName System.Windows.Forms
$ws = New-Object -ComObject WScript.Shell
$ok = $ws.AppActivate("DefaultColorPhone")
Write-Host "activate: $ok"
Start-Sleep -Milliseconds 700
[System.Windows.Forms.SendKeys]::SendWait("{F2}")
Start-Sleep -Milliseconds 900
[System.Windows.Forms.SendKeys]::SendWait("~")
Start-Sleep -Seconds 4
Write-Host "sent"
