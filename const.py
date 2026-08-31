"""Constants for the Login Logo integration."""

DOMAIN = "login_logo"

CONF_LOGO_PATH = "logo_path"
CONF_PATCH_FRONTEND = "patch_frontend"

WWW_SUBDIR = "login_logo"

ICON_SPECS = [
    ("favicon-32x32.png", 32),
    ("favicon-192x192.png", 192),
    ("favicon-1024x1024.png", 1024),
    ("apple-touch-icon-180x180.png", 180),
    ("apple-touch-icon-60x60.png", 60),
    ("apple-touch-icon-76x76.png", 76),
    ("apple-touch-icon-120x120.png", 120),
    ("apple-touch-icon-152x152.png", 152),
]

ICO_SIZES = [16, 32, 48]

FRONTEND_ICON_DIR_CANDIDATES = [
    "hass_frontend/static/icons",
]
