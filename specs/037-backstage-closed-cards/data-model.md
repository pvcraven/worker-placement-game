# Data Model: Backstage Closed Cards

No new data models, entities, or schema changes are required for this feature.

## Rationale

This is a purely client-side visual feature. The existing game phase (`GamePhase.REASSIGNMENT` / `GamePhase.PLACEMENT`) already communicates all the information the client needs to determine which backstage card variant to display.

## Existing Entities Used

- **GamePhase** (`shared/constants.py`): Enum with `PLACEMENT`, `REASSIGNMENT`, etc. Already tracked client-side in `game_state["phase"]`.
- **Backstage slot card images**: PNG files in `client/assets/card_images/spaces/`. Three new PNG files will be generated (closed variants) but no model changes needed.
