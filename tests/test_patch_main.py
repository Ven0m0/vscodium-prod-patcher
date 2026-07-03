import sys
from unittest.mock import MagicMock

class MockDataClassMixin:
    @classmethod
    def from_dict(cls, d):
        return MagicMock()

    def to_dict(self):
        return {}

# Mock dependencies that might not be available in the environment
mock_modules = {
    "mashumaro": MagicMock(),
    "mashumaro.mixins": MagicMock(),
    "mashumaro.mixins.toml": MagicMock(DataClassTOMLMixin=MockDataClassMixin),
    "mashumaro.mixins.dict": MagicMock(DataClassDictMixin=MockDataClassMixin),
    "tomli_w": MagicMock(),
    "pyalpm": MagicMock(),
    "pycman": MagicMock(),
    "pycman.config": MagicMock(),
    "inquirer": MagicMock(),
}

for mod_name, mock_obj in mock_modules.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_obj

from vscodium_prod_patcher.config.schema import VscPatchConfig  # noqa: E402
from vscodium_prod_patcher.patch.extension_galleries import (  # noqa: E402
    EXTENSIONS_MS_GALLERY,
    EXTENSIONS_OPENVSX_GALLERY,
    EXTENSIONS_OPENVSX_TRUSTED,
)
from vscodium_prod_patcher.patch.main import (  # noqa: E402
    TDKEY,
    patch_marketplace,
    patch_marketplace_trusted_domains,
)


def test_patch_marketplace_trusted_domains_missing():
    product = {}
    patch_marketplace_trusted_domains(product)
    assert TDKEY not in product


def test_patch_marketplace_trusted_domains_remove_some():
    product = {
        TDKEY: [
            "https://open-vsx.org",
            "https://example.com",
        ],
    }
    patch_marketplace_trusted_domains(product)
    assert product[TDKEY] == ["https://example.com"]


def test_patch_marketplace_trusted_domains_remove_all():
    product = {
        TDKEY: [
            "https://open-vsx.org",
        ],
    }
    patch_marketplace_trusted_domains(product)
    assert TDKEY not in product


def test_patch_marketplace_trusted_domains_keep_all():
    product = {
        TDKEY: [
            "https://example.com",
        ],
    }
    patch_marketplace_trusted_domains(product)
    assert product[TDKEY] == ["https://example.com"]


def test_patch_marketplace_none():
    product = {"extensionsGallery": "old"}
    config = VscPatchConfig(extension_source=None)
    patch_marketplace(product, config)
    assert product["extensionsGallery"] == "old"


def test_patch_marketplace_openvsx():
    product = {}
    config = VscPatchConfig(extension_source="openvsx")
    patch_marketplace(product, config)
    assert product["extensionsGallery"] == EXTENSIONS_OPENVSX_GALLERY
    assert TDKEY not in product


def test_patch_marketplace_microsoft():
    product = {
        TDKEY: EXTENSIONS_OPENVSX_TRUSTED + ["https://example.com"],
    }
    config = VscPatchConfig(extension_source="microsoft")
    patch_marketplace(product, config)
    assert product["extensionsGallery"] == EXTENSIONS_MS_GALLERY
    assert product[TDKEY] == ["https://example.com"]


def test_patch_marketplace_invalid(capsys):
    product = {"extensionsGallery": "old"}
    config = VscPatchConfig(extension_source="invalid")
    patch_marketplace(product, config)
    assert product["extensionsGallery"] == "old"
    captured = capsys.readouterr()
    assert "Invalid marketplace: invalid" in captured.out
