# Render the installed English voice locally. No cloud service, browser voice dependency or font copying.
param([string]$OutputDirectory = (Join-Path $PSScriptRoot '../stories/story-05/assets/audio/letters'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
[void](New-Item -ItemType Directory -Force -Path $OutputDirectory)
$story05Synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $story05English = $story05Synth.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -eq 'en-US' } | Select-Object -First 1
    if (-not $story05English) { throw 'A local en-US voice is required; do not substitute unlicensed recordings.' }
    $story05Synth.SelectVoice($story05English.VoiceInfo.Name)
    $story05Synth.Rate = -2
    $story05Names = @('ay','bee','see','dee','ee','eff','gee','aitch','eye','jay','kay','el','em','en','oh','pee','cue','ar','ess','tee','you','vee','double you','ex','why','zee')
    $story05Records = @()
    for ($story05Index=0; $story05Index -lt 26; $story05Index++) {
        $story05Letter = [string][char](65+$story05Index)
        $story05Path = Join-Path $OutputDirectory ($story05Letter.ToLower()+'.wav')
        $story05Synth.SetOutputToWaveFile($story05Path)
        $story05Synth.Speak($story05Names[$story05Index])
        $story05Synth.SetOutputToNull()
        $story05Records += @{letter=$story05Letter;spoken=$story05Names[$story05Index];src=('letters/'+$story05Letter.ToLower()+'.wav');voice=$story05English.VoiceInfo.Name;sha256=(Get-FileHash -LiteralPath $story05Path -Algorithm SHA256).Hash.ToLower()}
    }
    $story05Records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'manifest.json') -Encoding utf8
    Write-Output 'Rendered all 26 English letter names with an installed local voice.'
} finally { $story05Synth.Dispose() }
