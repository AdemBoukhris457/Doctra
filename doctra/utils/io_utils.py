from __future__ import annotations

import os
from pathlib import Path
from PIL import Image  # <-- import Image explicitly
import PIL


def get_image_from_local(file_path):
    return PIL.Image.open(file_path)