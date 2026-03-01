# Google Assistant Manager

Home Assistant custom integration to manage which entities are exposed to Google Home when using the manual `google_assistant` integration.

This project is only for the manual Google Assistant setup documented by Home Assistant:
https://www.home-assistant.io/integrations/google_assistant/

It is not for Home Assistant Cloud (Nabu Casa) exposure.

## Prerequisites

- Home Assistant `2023.4.0` or newer
- Manual `google_assistant` setup already working

## Install

1. Install via HACS custom repository, or copy this repo's `custom_components/google_assistant_manager` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add **Google Assistant Manager** from **Settings -> Devices & Services -> Integrations**.

## One-time `configuration.yaml` setup

Add this once:

```yaml
google_assistant:
  project_id: YOUR_PROJECT_ID
  service_account: !include service_account.json
  entity_config: !include google_assistant_entity_config.yaml
```

After that, this integration owns and auto-generates `google_assistant_entity_config.yaml`.

## UI behavior

- Sidebar panel: **Google Assistant**
- Search/filter by entity name and domain
- Collapsible domain sections (`Collapse`, `Expand`, `Collapse all`, `Expand all`)
- Per-entity expose toggle, Google `name`, aliases, and optional `room`
- Per-domain `All` / `None` expose shortcuts
- Clickable entity name and entity ID links to Home Assistant entity details
- Save writes the generated YAML and then calls `homeassistant.reload_all`

## Reload note

`homeassistant.reload_all` reloads all YAML-based integrations (not only Google Assistant). This avoids requiring a full Home Assistant restart and is typically fast.

## HACS updates and versioning

To get proper HACS update notifications (instead of pressing `Redownload`):

1. Bump `version` in `custom_components/google_assistant_manager/manifest.json`.
2. Create a Git tag that exactly matches that version with a `v` prefix (example: `v1.1.0`).
3. Publish a GitHub Release for that tag.

HACS checks releases/tags and will show an update when a newer tagged release is available.

## Scope limits

- Does not modify `configuration.yaml`
- Does not integrate with Nabu Casa
- No Node.js build step required
- Does not store cloud credentials
