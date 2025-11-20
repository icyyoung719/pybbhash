# PowerShell commands for pybbhash development
# Load with: . .\scripts\commands.ps1

function Test-PyBBHash {
    <#
    .SYNOPSIS
    Run all tests
    #>
    Write-Host "🧪 Running tests..." -ForegroundColor Cyan
    python -m pytest tests/ -v
}

function Test-Examples {
    <#
    .SYNOPSIS
    Run all example scripts
    #>
    Write-Host "💡 Running examples..." -ForegroundColor Cyan
    python examples/basic.py
    python examples/binary_format.py
    python examples/uint64_mapping.py
}

function Build-PyBBHash {
    <#
    .SYNOPSIS
    Build distribution packages
    #>
    Write-Host "📦 Building distribution..." -ForegroundColor Cyan
    python scripts/build.py
}

function Publish-TestPyPI {
    <#
    .SYNOPSIS
    Publish to TestPyPI
    #>
    Write-Host "🚀 Publishing to TestPyPI..." -ForegroundColor Cyan
    python scripts/build.py --test
}

function Publish-PyPI {
    <#
    .SYNOPSIS
    Publish to PyPI
    #>
    Write-Host "🚀 Publishing to PyPI..." -ForegroundColor Yellow
    python scripts/build.py --publish
}

function Update-Version {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("patch", "minor", "major")]
        [string]$Type
    )
    <#
    .SYNOPSIS
    Bump version (patch, minor, or major)
    #>
    Write-Host "🔢 Bumping $Type version..." -ForegroundColor Cyan
    python scripts/version.py $Type
}

function Clean-PyBBHash {
    <#
    .SYNOPSIS
    Clean build artifacts
    #>
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Cyan
    python scripts/build.py --clean
}

function Format-Code {
    <#
    .SYNOPSIS
    Format code with black
    #>
    Write-Host "✨ Formatting code..." -ForegroundColor Cyan
    black pybbhash tests examples
}

function Show-Help {
    <#
    .SYNOPSIS
    Show available commands
    #>
    Write-Host @"
🔷 pybbhash Development Commands

📦 Building & Publishing:
  Build-PyBBHash      - Build distribution packages
  Publish-TestPyPI    - Publish to TestPyPI (test)
  Publish-PyPI        - Publish to PyPI (production)
  Clean-PyBBHash      - Clean build artifacts

🧪 Testing:
  Test-PyBBHash       - Run all tests
  Test-Examples       - Run all example scripts

🔢 Version Management:
  Update-Version patch   - Bump patch version (0.1.0 -> 0.1.1)
  Update-Version minor   - Bump minor version (0.1.0 -> 0.2.0)
  Update-Version major   - Bump major version (0.1.0 -> 1.0.0)

🎨 Code Quality:
  Format-Code         - Format code with black

💡 Usage:
  . .\scripts\commands.ps1    # Load commands
  Show-Help                   # Show this help
  Test-PyBBHash               # Run tests
"@ -ForegroundColor Green
}

# Show help on load
Write-Host "✅ pybbhash commands loaded! Type 'Show-Help' for available commands." -ForegroundColor Green
