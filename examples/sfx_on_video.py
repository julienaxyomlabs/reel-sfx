"""Add sound effects to an edited video with reel-sfx + ffmpeg.

    python examples/sfx_on_video.py my_edit.mp4 examples/cues.json my_edit_sfx.mp4

The video's own audio is treated as dialogue: the SFX are ducked under it. The video stream is copied, not
re-encoded. Needs ffmpeg on PATH (only this example does; the package itself does not).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import reel_sfx


def main(video, cues_path, out):
    tmp = Path(tempfile.mkdtemp())
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True, check=True).stdout)
    voice = tmp / 'voice.wav'
    has_audio = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip()
    dia = None
    if has_audio:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s16le', str(voice)], check=True)
        dia, _ = reel_sfx.read_wav(voice)
    cues = json.loads(Path(cues_path).read_text())
    mixed = reel_sfx.mix(dia, reel_sfx.place(cues, dur), 48000)
    reel_sfx.write_wav(tmp / 'mix.wav', mixed, 48000)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', str(tmp / 'mix.wav'), '-map', '0:v:0', '-map', '1:a:0',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out], check=True)
    print('→', out)


if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
