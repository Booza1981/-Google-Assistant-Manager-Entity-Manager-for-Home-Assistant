"""Config flow for Google Assistant Manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol
import yaml
from homeassistant import config_entries

from .const import CONFIG_SNIPPET, DOMAIN, OUTPUT_FILENAME
from .store import GAMStore
from .yaml_writer import write_config


class _LenientSafeLoader(yaml.SafeLoader):
    """YAML loader that tolerates unknown tags such as !include."""


def _unknown_tag(loader: _LenientSafeLoader, tag_suffix: str, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


_LenientSafeLoader.add_multi_constructor("!", _unknown_tag)


@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Google Assistant Manager."""

    VERSION = 1

    def __init__(self) -> None:
        self._inline_entity_config: dict[str, Any] | None = None
        self._file_entity_config: dict[str, Any] | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Show confirmation and setup notice."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            await self._discover_existing_data()
            has_import = bool(self._inline_entity_config) or bool(self._file_entity_config)
            if has_import:
                return await self.async_step_import_existing()

            return await self._create_entry_with_data({"entities": {}})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={"snippet": CONFIG_SNIPPET},
        )

    async def async_step_import_existing(self, user_input: dict[str, Any] | None = None):
        """Offer importing existing entity config."""
        if user_input is not None:
            import_data: dict[str, Any] = {"entities": {}}
            if user_input["import_existing"]:
                source = self._file_entity_config or self._inline_entity_config or {}
                import_data = {"entities": _normalize_entity_config(source)}
            return await self._create_entry_with_data(import_data)

        return self.async_show_form(
            step_id="import_existing",
            data_schema=vol.Schema({vol.Required("import_existing", default=True): bool}),
        )

    async def _create_entry_with_data(self, data: dict[str, Any]):
        store = GAMStore(self.hass)
        await store.async_save(data)
        await write_config(self.hass, data)
        return self.async_create_entry(title="Google Assistant Manager", data={})

    async def _discover_existing_data(self) -> None:
        config_dir = Path(self.hass.config.config_dir)
        entity_file = config_dir / OUTPUT_FILENAME
        config_file = config_dir / "configuration.yaml"

        if entity_file.exists():
            self._file_entity_config = await self.hass.async_add_executor_job(
                _load_yaml_file, entity_file
            )

        if config_file.exists():
            parsed = await self.hass.async_add_executor_job(_load_yaml_file, config_file)
            google_cfg = parsed.get("google_assistant", {}) if isinstance(parsed, dict) else {}
            entity_cfg = google_cfg.get("entity_config") if isinstance(google_cfg, dict) else None
            if isinstance(entity_cfg, dict):
                self._inline_entity_config = entity_cfg

def _load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_handle:
        loaded = yaml.load(file_handle, Loader=_LenientSafeLoader)
    return loaded or {}


def _normalize_entity_config(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for entity_id, cfg in raw.items():
        if not isinstance(cfg, dict):
            continue

        aliases = cfg.get("aliases")
        if not isinstance(aliases, list):
            aliases = []

        normalized[entity_id] = {
            "expose": cfg.get("expose", True),
            "aliases": [alias for alias in aliases if isinstance(alias, str) and alias],
            "name": cfg.get("name") if isinstance(cfg.get("name"), str) else None,
        }

    return normalized
