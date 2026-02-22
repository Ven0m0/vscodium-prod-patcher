from contextlib import suppress
from functools import lru_cache
from typing import Any, Optional

from ..config.main import get_config
from ..config.schema import Config, VscPatchConfig
from ..config.utils import merge_patch_config
from ..consts import FEATURE_CATEGORIES
from ..paths import BACKUPS_DIR, DATA_DIR
from ..shared import json_load, json_write
from ..utils.backup import backup_editor_data, get_backups
from ..utils.print import pacinfo, pacwarn
from .extension_galleries import (EXTENSIONS_MS_GALLERY,
                                  EXTENSIONS_OPENVSX_GALLERY,
                                  EXTENSIONS_OPENVSX_TRUSTED)

FEATURES_PATCH_PATH = DATA_DIR / "patch/features-patch.json"
TDKEY = "linkProtectionTrustedDomains"


@lru_cache(maxsize=1)
def get_features_patch_data() -> dict[str, Any]:
    return json_load(FEATURES_PATCH_PATH)


def patch_features(product: dict[str, Any], config: VscPatchConfig):
    extra_features = config.extra_features
    if not extra_features:
        # False, None, or empty list
        return
    patch_data = get_features_patch_data()

    keys_to_apply: set[str] = set()

    if extra_features is True:
        keys_to_apply = set(patch_data.keys())
    elif isinstance(extra_features, list):
        for category in extra_features:
            keys = FEATURE_CATEGORIES.get(category, [])
            keys_to_apply.update(keys)

    for key in keys_to_apply:
        if key in patch_data:
            product[key] = patch_data[key]


def patch_data_dir(product: dict[str, Any], config: VscPatchConfig):
    data_dir = config.data_dir
    if not data_dir:
        return
    product["dataFolderName"] = str(data_dir)


def patch_marketplace_trusted_domains(product: dict[str, Any]):
    cur_domains: list[str]
    try:
        cur_domains = product[TDKEY]
    except KeyError:
        cur_domains = []
    for domain in EXTENSIONS_OPENVSX_TRUSTED:
        with suppress(ValueError):
            cur_domains.remove(domain)
    if not cur_domains:
        with suppress(KeyError):
            product.pop(TDKEY)
    else:
        product[TDKEY] = cur_domains


def patch_marketplace(product: dict[str, Any], config: VscPatchConfig):
    marketplace = config.extension_source
    if marketplace is None:
        return
    gallery = {}
    domains_remove = False
    match marketplace:
        case "openvsx":
            gallery = EXTENSIONS_OPENVSX_GALLERY
        case "microsoft":
            gallery = EXTENSIONS_MS_GALLERY
            domains_remove = True
        case _:
            pacwarn(" ", "Invalid marketplace:", marketplace)
            return
    if gallery:
        product["extensionsGallery"] = gallery
    if domains_remove:
        patch_marketplace_trusted_domains(product)


def patch_pkg(
    pkg: str,
    config: Optional[Config] = None,
    from_backup: bool = True,
):
    if config is None:
        config = get_config()
    editor = config.packages[pkg]
    patch_config = merge_patch_config(config.patch, editor.patch_override)

    # Check if we have any backups
    backups = get_backups(pkg)
    if not backups:
        # Create initial backup (snapshot of current state)
        backup_editor_data(pkg)
        backups = get_backups(pkg)  # Refresh list

    if from_backup:
        # Use latest backup
        if not backups:
            pacwarn("Warning", "Backup creation failed?")
            input_path = editor.meta.abs_product_json_path
        else:
            input_path = BACKUPS_DIR / pkg / backups[0]
    else:
        input_path = editor.meta.abs_product_json_path

    product = json_load(input_path)

    pacinfo("Patching", pkg)
    patch_features(product, patch_config)
    patch_marketplace(product, patch_config)
    patch_data_dir(product, patch_config)

    json_write(editor.meta.abs_product_json_path, product, indent=2)


def patch_pkgs(
    packages: list[str],
    from_backup: bool = True,
):
    config = get_config()
    conf_packages = config.packages
    changed_packages = [
        pkg
        for pkg in packages
        if pkg in conf_packages
    ]
    for pkg in changed_packages:
        patch_pkg(
            pkg,
            config=config,
            from_backup=from_backup,
        )
