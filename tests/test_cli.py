import json
import os
import subprocess
import sys
from pathlib import Path

import reel_sfx

EX = Path(__file__).resolve().parents[1] / 'examples'


def run(*args):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(Path(reel_sfx.__file__).parents[1]), os.environ.get('PYTHONPATH', '')]))
    r = subprocess.run([sys.executable, '-m', 'reel_sfx.cli', *args], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_list_info_path():
    assert 'whoosh.soft' in run('list')
    assert json.loads(run('info', 'bell.ding'))['license'] == 'CC0-1.0'
    assert Path(run('path', 'impact.sub').strip()).is_file()


def test_render_place_export(tmp_path):
    run('render', 'whoosh.air', '--seed', '5', '--out', str(tmp_path / 'w.wav'))
    assert reel_sfx.read_wav(tmp_path / 'w.wav')[1] == 48000
    run('place', str(EX / 'cues.json'), '--duration', '6', '--out', str(tmp_path / 'stem.wav'))
    y, sr = reel_sfx.read_wav(tmp_path / 'stem.wav'); assert len(y) == 6 * sr and abs(y).max() > 0.05
    voice = tmp_path / 'voice.wav'; reel_sfx.write_wav(voice, 0.1 * __import__('numpy').ones((sr * 4, 1)), sr, 16)
    run('place', str(EX / 'cues.json'), '--dialogue', str(voice), '--out', str(tmp_path / 'mix.wav'))
    assert len(reel_sfx.read_wav(tmp_path / 'mix.wav')[0]) == 4 * sr
    run('export', str(tmp_path / 'lib'))
    assert len(list((tmp_path / 'lib').rglob('*.wav'))) == len(reel_sfx.list_sounds())
