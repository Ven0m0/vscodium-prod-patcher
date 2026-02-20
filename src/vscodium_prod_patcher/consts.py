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
