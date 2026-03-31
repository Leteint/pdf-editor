"""
Tests for Windows shell integration (utils/shell_integration.py).
Skipped automatically on non-Windows platforms.
"""
from __future__ import annotations

import sys
import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="Windows registry tests only run on Windows"
)


@pytest.fixture(autouse=True)
def cleanup_registry():
    """Ensure registry entries are removed after each test."""
    from utils.shell_integration import unregister
    yield
    unregister()


class TestShellIntegration:
    def test_not_registered_initially(self):
        from utils.shell_integration import is_registered, unregister
        unregister()  # clean slate
        assert not is_registered()

    def test_register_sets_is_registered(self):
        from utils.shell_integration import register, is_registered
        register()
        assert is_registered()

    def test_unregister_clears_is_registered(self):
        from utils.shell_integration import register, unregister, is_registered
        register()
        unregister()
        assert not is_registered()

    def test_register_is_idempotent(self):
        from utils.shell_integration import register, is_registered
        register()
        register()  # second call must not raise
        assert is_registered()

    def test_unregister_when_not_registered_is_noop(self):
        from utils.shell_integration import unregister
        unregister()
        unregister()  # must not raise

    def test_all_extensions_registered(self):
        """Each supported extension must have a registry key after register()."""
        import winreg
        from utils.shell_integration import register, EXTENSIONS, _VERB
        register()
        for ext in EXTENSIONS:
            key_path = rf"Software\Classes\SystemFileAssociations\{ext}\shell\{_VERB}"
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path).Close()
            except FileNotFoundError:
                pytest.fail(f"Extension {ext} not registered")

    def test_command_contains_to_pdf_flag(self):
        """The registered command must include --to-pdf."""
        import winreg
        from utils.shell_integration import register, _VERB
        register()
        cmd_path = rf"Software\Classes\SystemFileAssociations\.jpg\shell\{_VERB}\command"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cmd_path) as k:
            cmd, _ = winreg.QueryValueEx(k, "")
        assert "--to-pdf" in cmd
