param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [string]$Python = "py"
)

$ErrorActionPreference = "Stop"
$kit = Join-Path $RepositoryRoot "kit\refresh.py"
$example = Join-Path $RepositoryRoot "examples\minimal"
$manifest = Join-Path $example "generated\manifest.json"

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
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
    throw "Refresh completed without a manifest: $manifest"
}
$manifestData = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
$expectedArtifacts = @("registry.json", "observations.json", "context.txt", "context.html", "context.json")
if ($manifestData.artifacts.Count -ne $expectedArtifacts.Count -or
    ((@($manifestData.artifacts) -join "|") -cne ($expectedArtifacts -join "|"))) {
    throw "Refresh manifest is incomplete or invalid: $manifest"
}
