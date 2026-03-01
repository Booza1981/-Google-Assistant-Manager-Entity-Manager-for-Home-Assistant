"""Constants for Google Assistant Manager."""

DOMAIN = "google_assistant_manager"
STORAGE_KEY = DOMAIN
STORAGE_VERSION = 1
OUTPUT_FILENAME = "google_assistant_entity_config.yaml"
PANEL_URL = "google-assistant-manager"
PANEL_TITLE = "Google Assistant"
PANEL_ICON = "mdi:google-assistant"
PANEL_JS_FILENAME = "google-assistant-manager-panel.js"

DEFAULT_ENTITY_CONFIG = {
    "expose": True,
    "aliases": [],
    "name": None,
    "room": None,
}

CONFIG_SNIPPET = """google_assistant:
  project_id: YOUR_PROJECT_ID
  service_account: !include service_account.json
  entity_config: !include google_assistant_entity_config.yaml
"""

SUPPORTED_DOMAINS = {
    "alarm_control_panel",
    "binary_sensor",
    "button",
    "camera",
    "climate",
    "cover",
    "event",
    "fan",
    "group",
    "humidifier",
    "input_boolean",
    "input_button",
    "input_select",
    "lawn_mower",
    "light",
    "lock",
    "media_player",
    "scene",
    "script",
    "select",
    "sensor",
    "switch",
    "vacuum",
    "valve",
    "water_heater",
}

SUPPORTED_SENSOR_DEVICE_CLASSES = {
    "aqi",
    "carbon_dioxide",
    "carbon_monoxide",
    "humidity",
    "pm10",
    "pm25",
    "temperature",
    "volatile_organic_compounds",
}

SUPPORTED_BINARY_SENSOR_DEVICE_CLASSES = {
    "carbon_monoxide",
    "door",
    "garage_door",
    "lock",
    "moisture",
    "opening",
    "smoke",
    "window",
}

SUPPORTED_EVENT_DEVICE_CLASSES = {
    "doorbell",
}
