"""Helpers for generating and installing favicon/icon assets."""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from PIL import Image

from .const import ICON_SPECS, ICO_SIZES, FRONTEND_ICON_DIR_CANDIDATES

_LOGGER = logging.getLogger(__name__)


def generate_icon_set(source_path: str, output_dir: str) -> dict[str, str]:
    """Generate all favicon/touch-icon sizes plus favicon.ico from one source image."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    img = Image.open(source_path).convert("RGBA")

    generated: dict[str, str] = {}

    for filename, size in ICON_SPECS:
        resized = img.resize((size, size), Image.LANCZOS)
        dest = out / filename
        resized.save(dest, format="PNG")
        generated[filename] = str(dest)

    ico_dest = out / "favicon.ico"
    ico_images = [img.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    ico_images[0].save(
        ico_dest, format="ICO", sizes=[(s, s) for s in ICO_SIZES]
    )
    generated["favicon.ico"] = str(ico_dest)

    return generated


def find_frontend_icons_dir() -> Path | None:
    """Locate the installed hass_frontend static/icons directory."""
    try:
        import hass_frontend
    except ImportError:
        _LOGGER.warning("hass_frontend package not importable")
        return None

    base = Path(hass_frontend.__file__).parent
    candidate = base / "static" / "icons"
    if candidate.is_dir():
        return candidate

    _LOGGER.warning("Could not find hass_frontend icons dir at %s", candidate)
    return None


def backup_original_icons(icons_dir: Path, backup_dir: Path) -> None:
    """Back up original frontend icon files once, before first overwrite."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    marker = backup_dir / ".backed_up"
    if marker.exists():
        return

    for item in icons_dir.iterdir():
        if item.is_file():
            shutil.copy(item, backup_dir / item.name)

    marker.touch()
    _LOGGER.info("Backed up original frontend icons to %s", backup_dir)


def restore_original_icons(icons_dir: Path, backup_dir: Path) -> bool:
    """Restore original frontend icons from backup, if present."""
    marker = backup_dir / ".backed_up"
    if not marker.exists():
        return False

    for item in backup_dir.iterdir():
        if item.is_file() and item.name != ".backed_up":
            shutil.copy(item, icons_dir / item.name)

    _LOGGER.info("Restored original frontend icons from %s", backup_dir)
    return True


def patch_frontend_icons(generated: dict[str, str], backup_dir: Path) -> bool:
    """Overwrite installed hass_frontend icon files with generated ones.

    Only safe when Home Assistant core will not be updated afterwards,
    since a core/frontend update will overwrite these files again.
    """
    icons_dir = find_frontend_icons_dir()
    if icons_dir is None:
        return False

    backup_original_icons(icons_dir, backup_dir)

    name_map = {
        "favicon.ico": "favicon.ico",
        "favicon-32x32.png": "favicon-32x32.png",
        "favicon-192x192.png": "favicon-192x192.png",
        "favicon-1024x1024.png": "favicon-1024x1024.png",
        "apple-touch-icon-180x180.png": "apple-touch-icon-180x180.png",
        "apple-touch-icon-60x60.png": "apple-touch-icon-60x60.png",
        "apple-touch-icon-76x76.png": "apple-touch-icon-76x76.png",
        "apple-touch-icon-120x120.png": "apple-touch-icon-120x120.png",
        "apple-touch-icon-152x152.png": "apple-touch-icon-152x152.png",
    }

    copied = 0
    for gen_name, target_name in name_map.items():
        src = generated.get(gen_name)
        if not src:
            continue
        target = icons_dir / target_name
        if target.exists() or True:
            try:
                shutil.copy(src, target)
                copied += 1
            except OSError as err:
                _LOGGER.error("Failed to overwrite %s: %s", target, err)

    _LOGGER.info("Patched %s frontend icon files in %s", copied, icons_dir)
    return copied > 0
