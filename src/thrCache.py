"""
thrCache - Generate and cache thumbnails for .thr (Sisyphus track) files.

Thumbnails are stored as PNGs in a .thumbnails/ subdirectory next to the
.thr files.  A thumbnail is regenerated only when the .thr file is newer
than the cached PNG.
"""

import os
import threading
from math import sin, cos, radians

from Sand import THR_PATH, TABLE_WIDTH, TABLE_LENGTH
from thr import loadThr
from Chains import Chains

THUMB_SIZE = 100
THUMB_SUBDIR = '.thumbnails'


def _thumb_dir(thr_dir):
    return os.path.join(thr_dir, THUMB_SUBDIR)


def thumb_path(thr_file):
    """Return the thumbnail PNG path for a given .thr file path."""
    directory = os.path.dirname(thr_file)
    basename = os.path.splitext(os.path.basename(thr_file))[0]
    return os.path.join(_thumb_dir(directory), basename + '.png')


def thumb_url(thr_file):
    """Return a URL-style path suitable for use in an <img src=...> tag."""
    path = thumb_path(thr_file)
    # Strip leading ./ or / so it's relative to app root
    return path.replace(os.sep, '/').lstrip('./')


def _is_stale(thr_file, png_file):
    """True if the thumbnail is missing or older than the source file."""
    if not os.path.exists(png_file):
        return True
    try:
        return os.path.getmtime(thr_file) > os.path.getmtime(png_file)
    except OSError:
        return True


def generate_thumb(thr_file):
    """Generate a thumbnail for a single .thr file.  Returns True on success."""
    png_file = thumb_path(thr_file)
    try:
        os.makedirs(os.path.dirname(png_file), exist_ok=True)
        xc = TABLE_WIDTH / 2.0
        yc = TABLE_LENGTH / 2.0
        multiplier = min(TABLE_WIDTH, TABLE_LENGTH) / 2.0
        chain = loadThr(thr_file, xc, yc, 0, multiplier)
        if not chain:
            return False
        # Use tight bounding box so the drawing fills the thumbnail
        (x0, y0), (x1, y1) = Chains.calcExtents([chain])
        pad = max((x1 - x0), (y1 - y0)) * 0.02
        box = [(x0 - pad, y0 - pad), (x1 + pad, y1 + pad)]
        Chains.saveImage([chain], box, png_file, THUMB_SIZE, THUMB_SIZE, 'Line')
        return True
    except Exception:
        return False


def get_or_create_thumb(thr_file):
    """Return the thumbnail URL, generating it first if needed.
    Returns None if generation fails."""
    png_file = thumb_path(thr_file)
    if _is_stale(thr_file, png_file):
        if not generate_thumb(thr_file):
            return None
    return thumb_url(thr_file)


def _collect_thr_files(root):
    """Walk root and yield all .thr file paths."""
    try:
        for entry in sorted(os.listdir(root)):
            if entry.startswith('.'):
                continue
            full = os.path.join(root, entry)
            if os.path.isdir(full):
                yield from _collect_thr_files(full)
            elif entry.lower().endswith('.thr'):
                yield full
    except OSError:
        pass


def warm_cache():
    """Pre-generate missing/stale thumbnails for all .thr files in THR_PATH.
    Runs in a background daemon thread."""
    def _worker():
        for thr_file in _collect_thr_files(THR_PATH):
            png_file = thumb_path(thr_file)
            if _is_stale(thr_file, png_file):
                generate_thumb(thr_file)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
