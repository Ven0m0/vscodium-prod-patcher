# Feature Implementation Plans

This document outlines the plans for key features to enhance the `vscodium-prod-patcher` tool.

## 1. Snapshot-based Backup System

### Problem Statement
The current backup mechanism overwrites the single `product.json` backup for each package. This means users cannot revert to an older version if a recent patch introduces issues, or if they want to compare different configurations over time.

### Proposed Solution
Implement a snapshot-based backup system where each backup is saved with a timestamp. Provide commands to list available backups and restore from a specific one.

### Implementation Steps

1.  **Modify Backup Logic:**
    *   Update `src/vscodium_prod_patcher/utils/backup.py`: `backup_editor_data`.
    *   Change the backup filename format from `product.json` to `product.json.<TIMESTAMP>` (e.g., `product.json.20231027-103000`).
    *   Ensure the timestamp format is sortable (YYYYMMDD-HHMMSS).

2.  **List Backups Command:**
    *   Add a new subcommand `backup list <package_name>` to the CLI.
    *   Implement a function in `src/vscodium_prod_patcher/utils/backup.py` to scan `BACKUPS_DIR / pkg` and list files matching the pattern.
    *   Display the list sorted by date (newest first).

3.  **Restore Specific Backup:**
    *   Update `src/vscodium_prod_patcher/patch/command.py` (or wherever `restore` is handled) to accept an optional argument `--backup-id` or `--timestamp`.
    *   If no argument is provided, restore the latest backup (lexicographically last).
    *   If an argument is provided, restore that specific file.

4.  **Pruning (Optional but Recommended):**
    *   Implement a simple pruning mechanism to keep only the last N (e.g., 5) backups to avoid disk clutter, or add a `backup prune` command.

### Benefits
*   **Safety:** Users can experiment with patches without fear of losing a working configuration.
*   **History:** Users can track changes to their `product.json` over time.
*   **Flexibility:** Easy to switch between different patched states.

## 2. Granular Feature Selection

### Problem Statement
Currently, the `extra_features` option is an all-or-nothing toggle that enables all features listed in `features-patch.json`. This forces users to accept unwanted changes (e.g., telemetry or certain Microsoft extensions) if they want any extra features at all.

### Proposed Solution
Implement a granular selection mechanism that allows users to enable specific feature groups or categories from `features-patch.json`.

### Implementation Steps

1.  **Refactor Features Patch Logic:**
    *   In `src/vscodium_prod_patcher/patch/main.py`, modify `patch_features` to iterate over keys in `features-patch.json` and selectively apply them.
    *   Currently, the patch applies top-level keys like `extensionEnabledApiProposals`, `tasConfig`, `extensionKind`, etc.
    *   Group these keys into user-friendly categories (e.g., "API Proposals", "Telemetry Config", "Extension Rules", "Trusted Domains", "Auth").
    *   Create a mapping in `src/vscodium_prod_patcher/patch/features-patch.json` (or hardcoded in code) between these categories and the JSON keys.

2.  **Update Configuration Schema:**
    *   Modify `src/vscodium_prod_patcher/config/schema.py`: `VscPatchConfig`.
    *   Change `extra_features: Optional[bool]` to `extra_features: Optional[list[str]]`.
    *   Retain backward compatibility by interpreting `extra_features=True` as enabling all categories.

3.  **Enhance TUI:**
    *   Update `src/vscodium_prod_patcher/config/tui.py`: `config_features`.
    *   Replace the boolean question for `extra_features` with a multi-select checkbox list (`inquirer.Checkbox`).
    *   List the available categories with descriptions.

4.  **Refactor Patch Execution:**
    *   In `patch_features`, verify if `config.enabled_features` is a list. If so, only apply keys associated with the enabled categories.
    *   If no specific categories are selected (for example, when migrating from a legacy `extra_features=True` configuration), apply all.

### Benefits
*   **User Control:** Users can customize their VSCodium experience precisely.
*   **Privacy:** Users can opt out of specific features (like telemetry) while keeping others (like API proposals).
*   **Flexibility:** Adapt to different extension requirements without enabling everything.
