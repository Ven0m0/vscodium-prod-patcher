NAME = "vscodium-prod-patcher"

ENCODING = "UTF-8"

FEATURE_CATEGORIES = {
    "api-proposals": ["extensionEnabledApiProposals"],
    "telemetry": ["tasConfig"],
    "extension-compatibility": [
        "extensionKind",
        "extensionPointExtensionKind",
        "extensionSyncedKeys",
        "extensionVirtualWorkspacesSupport"
    ],
    "auth": ["auth", "trustedExtensionAuthAccess"],
    "settings-sync": [
        "configurationSync.store",
        "editSessions.store",
        "tunnelApplicationName",
        "tunnelApplicationConfig"
    ],
}

FEATURE_CATEGORY_DESCRIPTIONS = {
    "api-proposals": "Extension API proposals (e.g. test APIs, Live Share)",
    "telemetry": "Telemetry/experiment config (tasConfig)",
    "extension-compatibility": "Extension kind and virtual workspace support overrides",
    "auth": "Auth providers and trusted extension auth access",
    "settings-sync": "Settings sync, edit sessions, tunnel app config",
}
