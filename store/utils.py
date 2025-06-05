import json
from django.conf import settings
from pathlib import Path

def load_default_blocks():
    default_path = Path(settings.BASE_DIR) / 'store' / 'fixtures' / 'layout_defaults.json'
    with open(default_path, 'r', encoding='utf-8') as f:
        return json.load(f)
