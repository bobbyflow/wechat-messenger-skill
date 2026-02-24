param(
    [Parameter(Mandatory=$true)]
    [string]$Message,
    [string]$Contact = "File Transfer"
)

# Load required assemblies
Add-Type -AssemblyName System.Windows.Forms

# Load Win32 API
$code = @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
    }
"@
if (-not ([System.Management.Automation.PSTypeName]'Win32').Type) {
    Add-Type -TypeDefinition $code
}

# Find WeChat Process
$wechat = Get-Process WeChat -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "WeChat" } | Select-Object -First 1
if (-not $wechat) {
    Write-Error "WeChat is not running or main window not found."
    exit 1
}

# Bring to foreground
[Win32]::SetForegroundWindow($wechat.MainWindowHandle)
Start-Sleep -Milliseconds 500

# Focus search (Ctrl+F)
[System.Windows.Forms.SendKeys]::SendWait("^f")
Start-Sleep -Milliseconds 500

# Search for the contact
if ($Contact -eq "File Transfer") {
    # Try searching for File Transfer in English
    [System.Windows.Forms.SendKeys]::SendWait("File Transfer")
    Start-Sleep -Milliseconds 200
    # Also type the Chinese name just in case
    [System.Windows.Forms.SendKeys]::SendWait("文件传输助手")
} else {
    [System.Windows.Forms.SendKeys]::SendWait($Contact)
}
Start-Sleep -Milliseconds 1000

# Select the top result (Enter)
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 500

# Copy message to clipboard and paste (handles complex text better)
[System.Windows.Forms.Clipboard]::SetText($Message)
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 300

# Send (Enter)
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

Write-Host "Sent message to $Contact via WeChat."
