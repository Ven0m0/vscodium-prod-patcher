from typing import Optional
from ..patch import patch_pkg
from ..shared import err
from ..utils.backup import (
    backup_editor_data,
    get_backups,
    prune_backups,
    restore_editor_data,
)

PATCH_SUBCMDS = ["apply", "backup", "restore", "list-backups", "prune"]


def patch_apply(package_name: str, from_backup: bool):
    patch_pkg(package_name, from_backup=from_backup)


def patch_backup(package_name: str):
    backup_editor_data(package_name)


def patch_restore(package_name: str, backup_id: Optional[str] = None):
    try:
        restore_editor_data(package_name, backup_id)
    except FileNotFoundError as e:
        err(str(e))


def patch_list_backups(package_name: str):
    backups = get_backups(package_name)
    if not backups:
        print(f"No backups found for {package_name}")
        return
    print(f"Backups for {package_name}:")
    for b in backups:
        print(f"- {b}")


def patch_prune(package_name: str, keep: int):
    removed = prune_backups(package_name, keep=keep)
    print(f"Pruned {removed} backup(s) for {package_name}; kept latest {keep}.")


def patch_main(args):
    match args.subcommand:
        case "apply":
            patch_apply(args.package_name, args.from_backup)
        case "backup":
            patch_backup(args.package_name)
        case "restore":
            patch_restore(args.package_name, getattr(args, "backup_id", None))
        case "list-backups":
            patch_list_backups(args.package_name)
        case "prune":
            patch_prune(args.package_name, args.keep)
        case _:
            err("bad subcommand")
