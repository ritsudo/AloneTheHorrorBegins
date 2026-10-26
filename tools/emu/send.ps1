param(
    [Parameter(Mandatory = $true)][string]$Keys,
    [int]$Wait = 1
)
Add-Type -AssemblyName System.Windows.Forms
$ws = New-Object -ComObject WScript.Shell
$ws.AppActivate('DefaultColorPhone') | Out-Null
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Seconds $Wait
