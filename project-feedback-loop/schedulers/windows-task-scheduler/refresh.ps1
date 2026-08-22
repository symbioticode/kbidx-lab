param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [string]$Python = "py"
)

$ErrorActionPreference = "Stop"
$kit = Join-Path $RepositoryRoot "kit\refresh.py"
$example = Join-Path $RepositoryRoot "examples\minimal"

if (-not (Test-Path -LiteralPath $kit -PathType Leaf)) {
    throw "Kit entry point not found: $kit"
}
if (-not (Test-Path -LiteralPath $example -PathType Container)) {
    throw "Example directory not found: $example"
}

& $Python $kit $example
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
