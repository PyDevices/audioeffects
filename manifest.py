"""Freeze audioeffects into a MicroPython firmware.

A firmware build that names audioeffects takes this file.

Only the package's own sources are frozen. A setuptools ``build/`` or
``*.egg-info`` left in a checkout holds a second copy of every module, and a
recursive ``package()`` would freeze that too.
"""

import os

if 0:

    def package(*args, **kwargs):
        pass


def _sources(name):
    root = os.path.join("lib", name)
    found = []
    for path, dirs, files in os.walk(root):
        dirs[:] = sorted(
            d for d in dirs if d not in ("build", "__pycache__") and not d.endswith(".egg-info")
        )
        rel = os.path.relpath(path, root)
        found += [f if rel == "." else os.path.join(rel, f) for f in sorted(files) if f.endswith(".py")]
    return found


package("audioeffects", files=_sources("audioeffects"), base_path="lib", opt=3)  # type: ignore[name-defined]  # noqa: PGH003
