"""
License validation via Lemon Squeezy API.

License key is stored locally in the user config directory.
Validated against the Lemon Squeezy API on every launch,
with a grace period for offline use.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Optional

# ── Lemon Squeezy settings ────────────────────────────────────────────────────
# No API key needed — the license endpoints are public (key + instance_id only).
_LS_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"
_LS_ACTIVATE_URL = "https://api.lemonsqueezy.com/v1/licenses/activate"

# Grace period: allow offline use for N days after last successful validation
_GRACE_DAYS = 7

# Local storage
_CONFIG_DIR  = os.path.join(os.path.expanduser("~"), ".pdf_editor")
_LICENSE_FILE = os.path.join(_CONFIG_DIR, "license.json")

# Machine fingerprint (used as activation instance name)
def _machine_id() -> str:
    import platform, socket
    raw = f"{platform.node()}-{platform.machine()}-{socket.gethostname()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


# ── Local persistence ─────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        with open(_LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> None:
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_stored_key() -> str:
    return _load().get("license_key", "")


# ── API calls ─────────────────────────────────────────────────────────────────

def _post(url: str, payload: dict, timeout: int = 8) -> dict:
    import urllib.request, urllib.error, urllib.parse
    import json as _json
    # Lemon Squeezy license API expects form-encoded body
    body = urllib.parse.urlencode(payload).encode()
    req  = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept":       "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return _json.loads(e.read())
        except Exception:
            return {}
    except Exception:
        return {}


def _activate(key: str) -> dict:
    """Activate the license on this machine."""
    return _post(_LS_ACTIVATE_URL, {
        "license_key":   key,
        "instance_name": f"PDFEditor-{_machine_id()}",
    })


def _validate(key: str, instance_id: str) -> dict:
    """Validate an already-activated license."""
    return _post(_LS_VALIDATE_URL, {
        "license_key": key,
        "instance_id": instance_id,
    })


# ── Main entry point ──────────────────────────────────────────────────────────

class LicenseResult:
    def __init__(self, valid: bool, reason: str = "", offline: bool = False) -> None:
        self.valid   = valid
        self.reason  = reason   # human-readable message
        self.offline = offline  # True = validated from grace period


def check_license(key: str) -> LicenseResult:
    """
    Full license check flow:
    1. Try to validate online against Lemon Squeezy.
    2. If offline/timeout, fall back to grace period.
    Returns a LicenseResult.
    """
    stored = _load()
    instance_id = stored.get("instance_id", "")

    # ── Step 1: activate if no instance_id yet ───────────────────────────
    if not instance_id:
        resp = _activate(key)
        if resp.get("activated"):
            instance_id = resp.get("instance", {}).get("id", "")
            _save({
                "license_key":     key,
                "instance_id":     instance_id,
                "last_valid_ts":   time.time(),
            })
            return LicenseResult(True, "Licence activée avec succès.")
        else:
            error = resp.get("error", "")
            if "already activated" in error.lower():
                # Key activated elsewhere — store instance_id if returned
                instance_id = (
                    resp.get("license_key", {})
                        .get("attributes", {})
                        .get("instances_count", "")
                )
                # Try to validate anyway
                pass
            return LicenseResult(False, error or "Clé de licence invalide.")

    # ── Step 2: validate existing activation ────────────────────────────
    resp = _validate(key, instance_id)

    if not resp:
        # Network error — check grace period
        return _grace_check(stored)

    valid = resp.get("valid", False)
    if valid:
        stored["last_valid_ts"] = time.time()
        _save(stored)
        return LicenseResult(True, "Licence valide.")

    # API returned invalid — check grace period before rejecting
    meta = resp.get("license_key", {}).get("attributes", {})
    status = meta.get("status", "")
    if status in ("disabled", "expired"):
        return LicenseResult(False, f"Licence {status}. Contactez le support.")

    return _grace_check(stored)


def _grace_check(stored: dict) -> LicenseResult:
    last_ts = stored.get("last_valid_ts", 0)
    elapsed_days = (time.time() - last_ts) / 86400
    if last_ts and elapsed_days <= _GRACE_DAYS:
        remaining = int(_GRACE_DAYS - elapsed_days) + 1
        return LicenseResult(
            True,
            f"Mode hors-ligne — {remaining} jour(s) restant(s).",
            offline=True,
        )
    return LicenseResult(
        False,
        "Impossible de valider la licence (hors-ligne depuis trop longtemps).",
    )


def clear_license() -> None:
    """Remove stored license data (for deactivation / uninstall)."""
    try:
        os.unlink(_LICENSE_FILE)
    except FileNotFoundError:
        pass
