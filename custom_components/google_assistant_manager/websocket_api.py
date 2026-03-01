"""Websocket API for Google Assistant Manager."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import CONFIG_SNIPPET, DEFAULT_ENTITY_CONFIG, DOMAIN, SUPPORTED_DOMAINS
from .store import GAMStore
from .yaml_writer import write_config


def _get_store(hass: HomeAssistant) -> GAMStore:
    domain_data = hass.data.get(DOMAIN, {})
    if not domain_data:
        raise ValueError("Google Assistant Manager is not set up")
    first_entry = next(iter(domain_data.values()))
    return first_entry["store"]


@websocket_api.websocket_command({"type": "google_assistant_manager/get_entities"})
@websocket_api.async_response
async def ws_get_entities(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return all supported entities merged with manager config."""
    store = _get_store(hass)
    store_data = store.get_data().get("entities", {})

    entities = []
    for state in hass.states.async_all():
        domain = state.domain
        if domain not in SUPPORTED_DOMAINS:
            continue

        stored_cfg = store_data.get(state.entity_id, {})
        friendly_name = state.attributes.get("friendly_name", state.name)
        entities.append(
            {
                "entity_id": state.entity_id,
                "friendly_name": friendly_name,
                "domain": domain,
                "expose": stored_cfg.get("expose", DEFAULT_ENTITY_CONFIG["expose"]),
                "aliases": stored_cfg.get("aliases", DEFAULT_ENTITY_CONFIG["aliases"]),
                "name": stored_cfg.get("name", DEFAULT_ENTITY_CONFIG["name"]),
            }
        )

    entities.sort(key=lambda item: (item["domain"], item["friendly_name"].lower()))
    connection.send_result(msg["id"], entities)


@websocket_api.websocket_command(
    {
        "type": "google_assistant_manager/update_entity",
        vol.Required("entity_id"): str,
        vol.Optional("expose"): bool,
        vol.Optional("aliases"): [str],
        vol.Optional("name"): vol.Any(str, None),
        vol.Optional("reload", default=True): bool,
    }
)
@websocket_api.async_response
async def ws_update_entity(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update one entity config and regenerate yaml."""
    store = _get_store(hass)

    update_kwargs: dict[str, Any] = {
        "entity_id": msg["entity_id"],
        "expose": msg.get("expose"),
        "aliases": msg.get("aliases"),
    }
    if "name" in msg:
        update_kwargs["name"] = msg["name"]

    await store.async_update_entity(**update_kwargs)

    await write_config(hass, store.get_data())

    if msg.get("reload", True):
        await hass.services.async_call("homeassistant", "reload_all", blocking=True)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        "type": "google_assistant_manager/bulk_update",
        vol.Required("entity_ids"): [str],
        vol.Required("expose"): bool,
        vol.Optional("reload", default=True): bool,
    }
)
@websocket_api.async_response
async def ws_bulk_update(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Bulk update exposure and regenerate yaml."""
    store = _get_store(hass)
    updated = await store.async_bulk_update(msg["entity_ids"], msg["expose"])

    await write_config(hass, store.get_data())
    if msg.get("reload", True):
        await hass.services.async_call("homeassistant", "reload_all", blocking=True)

    connection.send_result(msg["id"], {"success": True, "updated": updated})


@websocket_api.websocket_command({"type": "google_assistant_manager/reload"})
@websocket_api.async_response
async def ws_reload(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Run reload_all once after batched changes."""
    await hass.services.async_call("homeassistant", "reload_all", blocking=True)
    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command({"type": "google_assistant_manager/get_config_snippet"})
@websocket_api.async_response
async def ws_get_config_snippet(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return one-time configuration snippet for the user."""
    connection.send_result(msg["id"], {"snippet": CONFIG_SNIPPET})


def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register all websocket commands."""
    websocket_api.async_register_command(hass, ws_get_entities)
    websocket_api.async_register_command(hass, ws_update_entity)
    websocket_api.async_register_command(hass, ws_bulk_update)
    websocket_api.async_register_command(hass, ws_reload)
    websocket_api.async_register_command(hass, ws_get_config_snippet)
