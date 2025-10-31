# ----------------------------------------------------------------------------------
# Cloudflare - Baseline Deployment Script
# ----------------------------------------------------------------------------------

$ScriptPaths = @{
    SecurityRules = Join-Path $PSScriptRoot "deploy_securityrules.py"
    RateLimiting  = Join-Path $PSScriptRoot "deploy_rate_limiting.py"
    CacheRules    = Join-Path $PSScriptRoot "deploy_cache_rules.py"
    Speed         = Join-Path $PSScriptRoot "deploy_speed.py"
    DNSSecurity   = Join-Path $PSScriptRoot "deploy_dns_sec_settings.py"
    Security      = Join-Path $PSScriptRoot "deploy_sec_settings.py"
}

#Load Configuration and Set Environment Variables
function Load-ConfigAndSetEnv {
    $configFile = Join-Path $PSScriptRoot "config.json"
    
    if (-not (Test-Path $configFile)) {
        Write-Host "Error: 'config.json' file not found." -ForegroundColor Red
        Write-Host "Please create 'config.json' in the same directory with your API Token and Zone ID." -ForegroundColor Red
        return $false
    }

    try {
        $config = Get-Content $configFile | ConvertFrom-Json
    } catch {
        Write-Host "Error: Failed to parse 'config.json'." -ForegroundColor Red
        Write-Host "Please ensure it is valid JSON." -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
    
    if (-not $config.API_TOKEN -or $config.API_TOKEN -eq "YOUR_CLOUDFLARE_API_TOKEN_HERE") {
        Write-Host "Error: 'API_TOKEN' is missing or not set in 'config.json'." -ForegroundColor Red
        return $false
    }
    
    if (-not $config.ZONE_ID -or $config.ZONE_ID -eq "YOUR_ZONE_ID_HERE") {
        Write-Host "Error: 'ZONE_ID' is missing or not set in 'config.json'." -ForegroundColor Red
        return $false
    }

    $env:CLOUDFLARE_API_TOKEN = $config.API_TOKEN
    $env:ZONE_ID = $config.ZONE_ID
    
    Write-Host "Successfully loaded config for Zone ID: $($config.ZONE_ID)" -ForegroundColor Green
    return $true
}

#Run a Python Script
function Run-PythonScript {
    param (
        [string]$ScriptName,
        [string]$ScriptPath
    )
    
    Write-Host "----------------------------------------------------" -ForegroundColor Cyan
    Write-Host "Running: $ScriptName ($ScriptPath)" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------"
    
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: Script not found at path: $ScriptPath" -ForegroundColor Red
        return
    }

    try {
        python $ScriptPath
    } catch {
        Write-Host "A critical error occurred while trying to run the Python script." -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    
    Write-Host "----------------------------------------------------" -ForegroundColor Cyan
    Write-Host "Finished: $ScriptName" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------`n"
}

#Main Menu

function Show-Menu {
    $ColorBorder = "Cyan"
    $ColorTitle = "Yellow"
    $ColorTitleBG = "DarkBlue"
    $ColorInfo = "Gray"
    $ColorHeader = "White"
    $ColorOption = "Green"
    $ColorOptionNumber = "Yellow"
    $ColorAll = "Magenta"
    $ColorQuit = "Red"
    $ColorDefault = "Gray"

    #Width of the menu
    $width = 70
    
    #Helper function to write a bordered line
    function Write-BorderedLine {
        param (
            [string]$Text,
            [string]$LineColor = $ColorBorder,
            [string]$TextColor = $ColorDefault,
            [string]$BackgroundColor = "Black",
            [switch]$PadLeft
        )
        
        $paddingLength = $width - $Text.Length - 4
        if ($paddingLength -lt 0) { $paddingLength = 0 }
        
        if ($PadLeft) {
            $paddedText = (" " * $paddingLength) + $Text
        } else {
            $paddedText = $Text + (" " * $paddingLength)
        }
        
        Write-Host " ║" -ForegroundColor $LineColor -NoNewline
        Write-Host " $paddedText " -ForegroundColor $TextColor -BackgroundColor $BackgroundColor -NoNewline
        Write-Host "║ " -ForegroundColor $LineColor
    }

    function Write-TitleLine {
        param (
            [string]$Text,
            [string]$LineColor = $ColorBorder,
            [string]$TextColor = $ColorTitle,
            [string]$BackgroundColor = $ColorTitleBG
        )
        
        $paddingLength = ($width - $Text.Length - 2) / 2 # -2 for spaces
        $prePad = " " * [math]::Floor($paddingLength)
        $postPad = " " * [math]::Ceiling($paddingLength)
        
        $paddedText = "$prePad$Text$postPad"
        
        Write-Host " ║" -ForegroundColor $LineColor -NoNewline
        Write-Host $paddedText -ForegroundColor $TextColor -BackgroundColor $BackgroundColor -NoNewline
        Write-Host "║ " -ForegroundColor $LineColor
    }
    Clear-Host

    #Top border
    Write-Host (" ╔" + ("═" * ($width - 1)) + "╗ ") -ForegroundColor $ColorBorder

    #Title
    Write-TitleLine -Text "Cloudflare Baseline Deployment Menu"

    #Separator
    Write-Host (" ╠" + ("═" * ($width - 1)) + "╣ ") -ForegroundColor $ColorBorder
    
    #Zone ID
    Write-BorderedLine -Text "Zone ID: $env:ZONE_ID" -TextColor $ColorInfo
    
    #Spacer
    Write-BorderedLine -Text ""

    #Header
    Write-BorderedLine -Text "Select an option:" -TextColor $ColorHeader
    
    #Separator
    Write-Host (" ╟" + ("-" * ($width - 1)) + "╢ ") -ForegroundColor $ColorBorder

    #Options
    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "1" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: WAF Security Rules (Geo-block, Scanners)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 56)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "2" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: Rate Limiting Rules (Logins, Admin, API)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 57)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder
    
    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "3" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: Cache Rules (Bypass Admin Areas)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 48)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "4" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: Speed Settings (Speed Brain, 0-RTT, etc)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 55)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "5" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: DNS & SSL/TLS Settings (DNSSEC, Full Strict, etc)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 65)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "6" -ForegroundColor $ColorOptionNumber -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Deploy: Other Security Settings (Bot Mode, Page Shield)" -ForegroundColor $ColorOption -NoNewline
    Write-Host (" " * ($width - 64)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    #Separator
    Write-Host (" ╠" + ("═" * ($width - 1)) + "╣ ") -ForegroundColor $ColorBorder

    #'A' Option
    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "A" -ForegroundColor $ColorAll -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "RUN ALL ABOVE DEPLOYMENTS" -ForegroundColor $ColorAll -NoNewline
    Write-Host (" " * ($width - 33)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder
    
    #Separator
    Write-Host (" ╠" + ("═" * ($width - 1)) + "╣ ") -ForegroundColor $ColorBorder

    #Quit Option
    Write-Host " ║" -ForegroundColor $ColorBorder -NoNewline
    Write-Host "   [" -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Q" -ForegroundColor $ColorQuit -NoNewline
    Write-Host "] " -ForegroundColor $ColorDefault -NoNewline
    Write-Host "Quit" -ForegroundColor $ColorQuit -NoNewline
    Write-Host (" " * ($width - 13)) -NoNewline
    Write-Host "║ " -ForegroundColor $ColorBorder

    #Bottom border
    Write-Host (" ╚" + ("═" * ($width - 1)) + "╝ ") -ForegroundColor $ColorBorder
    
    #Reset color at the end
    Write-Host ""
}

#Main Logic Starts Here

#Load Config
if (-not (Load-ConfigAndSetEnv)) {
    Write-Host "Exiting due to configuration errors." -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    return
}

#Show Menu Loop
do {
    Show-Menu
    $choice = Read-Host -Prompt "Enter your choice"
    
    switch ($choice) {
        "1" { Run-PythonScript -ScriptName "WAF Security Rules" -ScriptPath $ScriptPaths.SecurityRules }
        "2" { Run-PythonScript -ScriptName "Rate Limiting Rules" -ScriptPath $ScriptPaths.RateLimiting }
        "3" { Run-PythonScript -ScriptName "Cache Rules" -ScriptPath $ScriptPaths.CacheRules }
        "4." { Run-PythonScript -ScriptName "Speed Settings" -ScriptPath $ScriptPaths.Speed }
        "5" { Run-PythonScript -ScriptName "DNS & SSL/TLS Settings" -ScriptPath $ScriptPaths.DNSSecurity }
        "6" { Run-PythonScript -ScriptName "Other Security Settings" -ScriptPath $ScriptPaths.Security }
        "A" {
            Write-Host "*** RUNNING ALL DEPLOYMENTS ***" -ForegroundColor Yellow
            Run-PythonScript -ScriptName "WAF Security Rules" -ScriptPath $ScriptPaths.SecurityRules
            Run-PythonScript -ScriptName "Rate Limiting Rules" -ScriptPath $ScriptPaths.RateLimiting
            Run-PythonScript -ScriptName "Cache Rules" -ScriptPath $ScriptPaths.CacheRules
            Run-PythonScript -ScriptName "Speed Settings" -ScriptPath $ScriptPaths.Speed
            Run-PythonScript -ScriptName "DNS & SSL/TLS Settings" -ScriptPath $ScriptPaths.DNSSecurity
            Run-PythonScript -ScriptName "Other Security Settings" -ScriptPath $ScriptPaths.Security
            Write-Host "*** ALL DEPLOYMENTS COMPLETE ***" -ForegroundColor Green
        }
        "Q" {
            Write-Host "Exiting."
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
    
    if ($choice -ne "Q") {
        Read-Host -Prompt "Press Enter to return to the menu"
    }

} while ($choice -ne "Q")

