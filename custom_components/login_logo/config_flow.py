"""Config flow for Login Logo integration."""
from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_LOGO_PATH, CONF_PATCH_FRONTEND

_LOGGER = logging.getLogger(__name__)


class LoginLogoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Login Logo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                stored_path = await self.hass.async_add_executor_job(
                    self._store_uploaded_file, user_input["logo_upload"]
                )
            except HomeAssistantError as err:
                _LOGGER.error("Failed to store uploaded logo: %s", err)
                errors["base"] = "upload_failed"
            else:
                return self.async_create_entry(
                    title="Login Logo",
                    data={
                        CONF_LOGO_PATH: stored_path,
                        CONF_PATCH_FRONTEND: user_input.get(
                            CONF_PATCH_FRONTEND, True
                        ),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required("logo_upload"): selector.FileSelector(
                    selector.FileSelectorConfig(accept="image/png,image/x-icon")
                ),
                vol.Optional(CONF_PATCH_FRONTEND, default=True): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    def _store_uploaded_file(self, file_id: str) -> str:
        """Move the uploaded file out of the temp upload dir into config/www."""
        from homeassistant.components.file_upload import process_uploaded_file

        with process_uploaded_file(self.hass, file_id) as uploaded_path:
            dest_dir = Path(self.hass.config.path("www", "login_logo"))
            dest_dir.mkdir(parents=True, exist_ok=True)
            suffix = Path(uploaded_path).suffix or ".png"
            dest_file = dest_dir / f"source_{uuid.uuid4().hex[:8]}{suffix}"
            shutil.copy(uploaded_path, dest_file)
            return str(dest_file)

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LoginLogoOptionsFlow:
        return LoginLogoOptionsFlow(config_entry)


class LoginLogoOptionsFlow(config_entries.OptionsFlow):
    """Allow re-uploading a new logo later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            flow = LoginLogoConfigFlow()
            flow.hass = self.hass
            try:
                stored_path = await self.hass.async_add_executor_job(
                    flow._store_uploaded_file, user_input["logo_upload"]
                )
            except HomeAssistantError:
                errors["base"] = "upload_failed"
            else:
                new_data = dict(self.config_entry.data)
                new_data[CONF_LOGO_PATH] = stored_path
                new_data[CONF_PATCH_FRONTEND] = user_input.get(
                    CONF_PATCH_FRONTEND, True
                )
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required("logo_upload"): selector.FileSelector(
                    selector.FileSelectorConfig(accept="image/png,image/x-icon")
                ),
                vol.Optional(
                    CONF_PATCH_FRONTEND,
                    default=self.config_entry.data.get(CONF_PATCH_FRONTEND, True),
                ): selector.BooleanSelector(),
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
