import importlib.util
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
if importlib.util.find_spec('reel_sfx') is None:      # running from a checkout without `pip install`
    sys.path.insert(0, str(SRC))
