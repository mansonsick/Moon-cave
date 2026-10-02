# Compatibility entry point. TTS "ay" incorrectly became "eye".
# Rebuild pinned human recordings instead; never overwrite them with TTS.
$ErrorActionPreference = 'Stop'
python (Join-Path $PSScriptRoot 'build_story05_letters.py')
if ($LASTEXITCODE -ne 0) { throw 'Human letter recording rebuild failed.' }
