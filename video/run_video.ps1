# run_video.ps1 — Run from project root:
#   powershell -ExecutionPolicy Bypass -File video/run_video.ps1
#
# This script runs the video generator with no timeout and waits for ffmpeg to finish.

Set-Location $PSScriptRoot\..
Write-Host "[run_video] Starting video generation..."
$proc = Start-Process -FilePath python -ArgumentList "video/generate_video.py" -NoNewWindow -PassThru -Wait
if ($proc.ExitCode -eq 0) {
    Write-Host "[run_video] SUCCESS — video/spark-ai-demo.mp4 created"
    Get-Item video/spark-ai-demo.mp4 | Select-Object Name, @{N='Size_MB';E={[math]::Round($_.Length/1MB,1)}}, LastWriteTime
} else {
    Write-Host "[run_video] FAILED — exit code $($proc.ExitCode)"
}
