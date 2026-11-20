"""Find API keys saved for the Windows user account.

A key saved with [Environment]::SetEnvironmentVariable(name, value, "User") only reaches
programs started after it was saved. This reads the saved value from the registry when the
variable is missing, so an already open terminal or editor can use it too.
"""
import os
import sys

KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def load_saved_keys(names=KEY_NAMES):
    if sys.platform != "win32":
        return
    import winreg

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
    except OSError:
        return
    with key:
        for name in names:
            if os.environ.get(name):
                continue
            try:
                value, _ = winreg.QueryValueEx(key, name)
            except OSError:
                continue
            if value:
                os.environ[name] = value
