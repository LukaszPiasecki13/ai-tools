---
applyTo: "**/*.ps1,**/*.psm1"
description: "PowerShell 7+ coding standards: script structure, naming, error handling, Pester tests. Applied automatically to PowerShell files."
---

# PowerShell Coding Standards

PowerShell 7+. Use `#Requires -Version 7.0`. Apply `ShouldProcess` to all destructive operations.

## Script Structure

```powershell
#Requires -Version 7.0

<#
.SYNOPSIS
    Brief description of what the script does.
.PARAMETER InputPath
    Description of parameter.
.EXAMPLE
    .\script.ps1 -InputPath "C:\data"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path $_ })]
    [string]$InputPath,

    [Parameter()]
    [switch]$Force
)

# Script body
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Function | Verb-Noun | `Get-ReportStatus` |
| Variable | PascalCase | `$UserName` |
| Parameter | PascalCase | `-OutputPath` |
| Script file | Verb-Noun | `Deploy-Function.ps1` |
| Module | PascalCase | `ProjectTools.psm1` |

Use only approved PowerShell verbs: `Get`, `Set`, `New`, `Remove`, `Start`, `Stop`, `Test`, `Invoke`, `Export`, `Import`, `Update`, `Find`.

## Error Handling

```powershell
try {
    $Result = Invoke-RestMethod -Uri $ApiUrl -Method Get -Headers $Headers
}
catch [System.Net.WebException] {
    Write-Error "Network error: $_"
    return $null
}
catch {
    Write-Error "Unexpected error: $_"
    throw
}

# -ErrorAction for flow control (not try/catch)
$File = Get-Item -Path $Path -ErrorAction SilentlyContinue
if (-not $File) {
    Write-Warning "File not found: $Path"
    return
}
```

## Output and Logging

```powershell
Write-Verbose "Processing file: $FilePath"          # debug (-Verbose flag)
Write-Information "Deployed 3 functions"            # status (-InformationAction Continue)
Write-Warning "Config not found, using defaults"    # non-critical
Write-Error "Failed to connect to $ServiceUrl"      # failure
```

Return objects, not strings:
```powershell
function Get-DeploymentStatus {
    [PSCustomObject]@{
        Service    = $ServiceName
        Status     = 'Running'
        LastDeploy = Get-Date
        Version    = '1.2.0'
    }
}
```

## Common Patterns

### API calls (splatting)
```powershell
$Params = @{
    Uri         = "$BaseUrl/$Endpoint"
    Method      = $Method
    Headers     = @{ Authorization = "Bearer $Token" }
    ContentType = 'application/json'
}
if ($Body) { $Params.Body = $Body | ConvertTo-Json -Depth 10 }
Invoke-RestMethod @Params
```

### Destructive actions (ShouldProcess)
```powershell
function Remove-OldDeployments {
    [CmdletBinding(SupportsShouldProcess)]
    param([int]$OlderThanDays = 30)

    foreach ($Deploy in (Get-OldDeployments -Days $OlderThanDays)) {
        if ($PSCmdlet.ShouldProcess($Deploy.Name, "Delete deployment")) {
            Remove-Deployment -Id $Deploy.Id
        }
    }
}
```

## Avoid

- Aliases in scripts (`gci` - use `Get-ChildItem`)
- String concatenation for paths (use `Join-Path`)
- Backtick line continuations (use splatting `@Params`)
- `Write-Host` for output (use appropriate `Write-*`)
- Hardcoded credentials (use SecureString or secret managers)
- `Invoke-Expression` (arbitrary code execution risk)

## Testing (Pester)

```powershell
Describe "Get-ReportStatus" {
    BeforeAll { . $PSScriptRoot\..\Get-ReportStatus.ps1 }

    It "Returns status for valid report ID" {
        $Result = Get-ReportStatus -ReportId "RPT-001"
        $Result.Status | Should -Be "Published"
    }

    It "Returns null for invalid report ID" {
        Get-ReportStatus -ReportId "INVALID" | Should -BeNullOrEmpty
    }
}
```
