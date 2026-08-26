import subprocess
import sys


class LocalAudioPlayer:
    def __init__(self, platform_name=None, runner=None):
        self.platform_name = platform_name or sys.platform
        self.runner = runner or subprocess.run

    def play_mp3(self, path):
        if not str(self.platform_name).lower().startswith("win"):
            return {"played": False, "reason": "unsupported-platform"}

        safe_path = str(path).replace("'", "''")
        script = (
            "Add-Type -AssemblyName PresentationCore; "
            f"$p='{safe_path}'; "
            "$m=New-Object System.Windows.Media.MediaPlayer; "
            "$m.Open([System.Uri]$p); "
            "$deadline=(Get-Date).AddSeconds(10); "
            "while((-not $m.NaturalDuration.HasTimeSpan) -and ((Get-Date) -lt $deadline)){Start-Sleep -Milliseconds 50}; "
            "if(-not $m.NaturalDuration.HasTimeSpan){throw 'No se pudo leer la duracion del audio'}; "
            "$m.Play(); "
            "$ms=[int][Math]::Ceiling($m.NaturalDuration.TimeSpan.TotalMilliseconds)+200; "
            "Start-Sleep -Milliseconds $ms; "
            "$m.Stop(); $m.Close();"
        )

        try:
            self.runner(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    script,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {"played": True, "backend": "windows-mediaplayer"}
        except Exception as exc:
            return {"played": False, "reason": "playback-failed", "error": str(exc)}


local_audio_player = LocalAudioPlayer()
