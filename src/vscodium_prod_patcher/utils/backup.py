import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..config.main import get_config
from ..consts import ENCODING
from ..paths import BACKUPS_DIR


def backup_json_file(
    original: Path,
    target: Path,
    load_and_dump_json_files: bool,
    json_dump_kwargs: Optional[dict[str, Any]] = None,
):
    if json_dump_kwargs is None:
        json_dump_kwargs = {}

    shutil.copy2(original, target)
    if not load_and_dump_json_files:
        return

    target_dbg_base_name = target.name.removesuffix(".json")
    target_dbg_name = target_dbg_base_name + ".load_and_dump.json"
    target_dbg = target.parent / target_dbg_name
    with (
        open(original, "rt", encoding=ENCODING) as file_in,
        open(target_dbg, "wt", encoding=ENCODING) as file_out,
    ):
        json.dump(json.load(file_in), file_out, **json_dump_kwargs)


def backup_editor_data(pkg: str):
    config = get_config()
    load_and_dump_json_files = \
        config.debug is not None \
        and bool(config.debug.load_and_dump_json_files)
    editor_meta = config.packages[pkg].meta
    current_backup_dir = BACKUPS_DIR / pkg
    os.makedirs(current_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target_name = f"product.json.{timestamp}"

    backup_json_file(
        editor_meta.abs_product_json_path,
        current_backup_dir / target_name,
        load_and_dump_json_files,
        json_dump_kwargs={"indent": 2},
    )


def get_backups(pkg: str) -> list[str]:
    current_backup_dir = BACKUPS_DIR / pkg
    if not current_backup_dir.exists():
        return []

    backups = []
    for f in current_backup_dir.iterdir():
        if not f.is_file():
            continue
        if f.name == "product.json":
            backups.append(f.name)
        elif f.name.startswith("product.json.") and len(f.name) > 13:
             # Check basic length to avoid grabbing partials if any
             backups.append(f.name)

    # Sort descending (lexicographically, so timestamped ones come first if newer,
    # and longer strings usually come after shorter ones if prefix matches...
    # 'product.json' vs 'product.json.2023...'
    # '.' is greater than nothing. So 'product.json.' > 'product.json'
    # Wait. 'a' < 'b'. 'a' < 'aa'.
    # But reverse sort? 'aa' > 'a'.
    # So 'product.json.2023...' comes BEFORE 'product.json' in reverse sort.
    # This means timestamped files (newer) are first. Correct.
    backups.sort(reverse=True)
    return backups


def restore_editor_data(pkg: str, backup_id: Optional[str] = None):
    config = get_config()
    editor_meta = config.packages[pkg].meta
    current_backup_dir = BACKUPS_DIR / pkg

    source: Path
    if backup_id:
        # Check if full name or suffix
        if (current_backup_dir / backup_id).exists():
            source = current_backup_dir / backup_id
        elif (current_backup_dir / f"product.json.{backup_id}").exists():
            source = current_backup_dir / f"product.json.{backup_id}"
        else:
            raise FileNotFoundError(f"Backup {backup_id} not found")
    else:
        backups = get_backups(pkg)
        if not backups:
            raise FileNotFoundError(f"No backups found for {pkg}")
        source = current_backup_dir / backups[0]

    print(f"Restoring from {source.name}...")
    shutil.copy2(
        source,
        editor_meta.abs_product_json_path,
    )
