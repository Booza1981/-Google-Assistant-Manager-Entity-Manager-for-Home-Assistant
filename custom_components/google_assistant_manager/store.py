"""Storage helpers for Google Assistant Manager."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DEFAULT_ENTITY_CONFIG, STORAGE_KEY, STORAGE_VERSION

_UNSET = object()


class GAMStore:
    """Wrap Home Assistant Store for manager data."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"version": STORAGE_VERSION, "entities": {}}

    async def async_load(self) -> dict[str, Any]:
        """Load persisted data, returning defaults on first run."""
        stored = await self._store.async_load()
        if not stored:
            self._data = {"version": STORAGE_VERSION, "entities": {}}
            return deepcopy(self._data)

        entities = stored.get("entities", {})
        if not isinstance(entities, dict):
            entities = {}

        self._data = {
            "version": STORAGE_VERSION,
            "entities": entities,
        }
        return deepcopy(self._data)

    async def async_save(self, data: dict[str, Any]) -> None:
        """Persist the provided data payload."""
        self._data = {
            "version": STORAGE_VERSION,
            "entities": data.get("entities", {}),
        }
        await self._store.async_save(self._data)

    async def async_get_entity(self, entity_id: str) -> dict[str, Any]:
        """Return config for an entity with defaults."""
        cfg = self._data["entities"].get(entity_id, {})
        return {
            "expose": cfg.get("expose", DEFAULT_ENTITY_CONFIG["expose"]),
            "aliases": list(cfg.get("aliases", DEFAULT_ENTITY_CONFIG["aliases"])),
            "name": cfg.get("name", DEFAULT_ENTITY_CONFIG["name"]),
        }

    async def async_update_entity(
        self,
        entity_id: str,
        expose: bool | None = None,
        aliases: list[str] | None = None,
        name: str | None | object = _UNSET,
    ) -> dict[str, Any]:
        """Partially update one entity and persist."""
        current = await self.async_get_entity(entity_id)

        if expose is not None:
            current["expose"] = expose
        if aliases is not None:
            current["aliases"] = aliases
        if name is not _UNSET:
            current["name"] = name

        self._data["entities"][entity_id] = current
        await self._store.async_save(self._data)
        return current

    async def async_bulk_update(self, entity_ids: list[str], expose: bool) -> int:
        """Bulk set expose for a list of entities and persist."""
        updated = 0
        for entity_id in entity_ids:
            current = await self.async_get_entity(entity_id)
            if current.get("expose") == expose:
                continue
            current["expose"] = expose
            self._data["entities"][entity_id] = current
            updated += 1

        if updated:
            await self._store.async_save(self._data)

        return updated

    def get_data(self) -> dict[str, Any]:
        """Return in-memory data snapshot."""
        return deepcopy(self._data)
