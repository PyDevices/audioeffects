#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Write catalog.json: every effect's patches and macro names, as data.

    python tools/make_catalog.py           # write lib/audioeffects/catalog.json
    python tools/make_catalog.py --check   # exit 1 if it is out of date

A DAW or MIDI host reads the file to show an effect's patch and macro names
without loading the audio stack, and the wheel carries it. The classes are the
source: change a class's `PATCHES`, `MACRO_LABELS` or `DISPLAY_NAME` and run
this again.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "lib"))

import audioeffects  # noqa: E402

CATALOG = os.path.join(ROOT, "lib", "audioeffects", "catalog.json")


def entry(name):
    """One effect in the catalog."""
    cls = getattr(audioeffects, name)
    labels = tuple(getattr(cls, "MACRO_LABELS", ()))
    modes = dict(getattr(cls, "MACRO_MODES", {}))
    return {
        "name": name,
        "display_name": getattr(cls, "DISPLAY_NAME", None) or name,
        "categories": list(getattr(cls, "CATEGORIES", ())),
        "macros": [{"label": label, "mode": modes[i]} for i, label in enumerate(labels)],
        "patches": [
            {"index": i, "name": p[0], "values": [int(v) for v in p[1]]}
            for i, p in sorted(getattr(cls, "PATCHES", {}).items())
        ],
    }


def catalog():
    """The file's text. One line a macro and a patch, so a diff shows the patch
    that changed."""
    def one(value):
        return json.dumps(value, ensure_ascii=False)

    def item(e):
        fields = []
        for key, value in e.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                rows = ",\n".join("    " + one(v) for v in value)
                fields.append('   "%s": [\n%s\n   ]' % (key, rows))
            else:
                fields.append('   "%s": %s' % (key, one(value)))
        return "  {\n%s\n  }" % ",\n".join(fields)

    items = ",\n".join(item(entry(n)) for n in audioeffects.ALL)
    return ('{\n "format": 1,\n "package": "audioeffects",\n "effects": [\n%s\n ]\n}\n'
            % items)


def main(argv):
    body = catalog()
    try:
        with open(CATALOG, encoding="utf-8") as f:
            current = f.read()
    except OSError:
        current = None
    if current == body:
        print("catalog.json is up to date")
        return 0
    if "--check" in argv:
        print("catalog.json is out of date: run tools/make_catalog.py")
        return 1
    with open(CATALOG, "w", encoding="utf-8") as f:
        f.write(body)
    print("catalog.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
