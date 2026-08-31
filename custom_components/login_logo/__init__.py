"""The Login Logo integration.

Replaces the Home Assistant login/loading screen favicon and touch icons
with a user-uploaded logo. Intended for installations that will not be
core-updated afterwards, since a Home Assistant core/frontend update will
overwrite the patched files again.
"""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_LOGO_PATH, CONF_PATCH_FRONTEND, WWW_SUBDIR
from .icon_tools import (
    generate_icon_set,
    patch_frontend_icons,
    restore_original_icons,
    find_frontend_icons_dir,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_RESTORE = "restore_default_logo"
SERVICE_REAPPLY = "reapply_logo"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    await _apply_logo(hass, entry)

    async def _handle_restore(call: ServiceCall) -> None:
        await _restore_default(hass, entry)

    async def _handle_reapply(call: ServiceCall) -> None:
        await _apply_logo(hass, entry)

    hass.services.async_register(DOMAIN, SERVICE_RESTORE, _handle_restore)
    hass.services.async_register(DOMAIN, SERVICE_REAPPLY, _handle_reapply)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.services.async_remove(DOMAIN, SERVICE_RESTORE)
    hass.services.async_remove(DOMAIN, SERVICE_REAPPLY)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await _apply_logo(hass, entry)


async def _apply_logo(hass: HomeAssistant, entry: ConfigEntry) -> None:
    logo_path = entry.data.get(CONF_LOGO_PATH)
    patch_frontend = entry.data.get(CONF_PATCH_FRONTEND, True)

    if not logo_path or not Path(logo_path).exists():
        _LOGGER.error("Configured logo path %s does not exist", logo_path)
        return

    www_dir = hass.config.path("www", WWW_SUBDIR)

    def _work() -> dict[str, str]:
        generated = generate_icon_set(logo_path, www_dir)
        if patch_frontend:
            backup_dir = Path(hass.config.path(".storage", "login_logo_backup"))
            patch_frontend_icons(generated, backup_dir)
        return generated

    generated = await hass.async_add_executor_job(_work)
    hass.data[DOMAIN][entry.entry_id] = generated

    _LOGGER.info(
        "Login Logo applied. Local files served from /local/%s/. "
        "Clear your browser cache (or hard refresh) to see the change "
        "on the login/loading screen.",
        WWW_SUBDIR,
    )


async def _restore_default(hass: HomeAssistant, entry: ConfigEntry) -> None:
    icons_dir = find_frontend_icons_dir()
    if icons_dir is None:
        _LOGGER.error("Cannot restore: frontend icons directory not found")
        return

    backup_dir = Path(hass.config.path(".storage", "login_logo_backup"))

    def _work() -> bool:
        return restore_original_icons(icons_dir, backup_dir)

    restored = await hass.async_add_executor_job(_work)
    if restored:
        _LOGGER.info("Original Home Assistant icons restored")
    else:
        _LOGGER.warning("No backup found to restore from")
