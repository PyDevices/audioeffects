# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""pytest's view of the suite, for CI's parallel run (pytest-xdist).

The tests are plain unittest and `python -m unittest discover -s tests`
ignores this file. It changes only the order pytest hands the tests out in,
never which tests run.

The slowest files go first. The lifecycle matrix runs the whole matrix on
CPython in its setUpClass, the node matrix runs its nodes one after another
in its own (NodeFlanger alone takes minutes), and a few reverb and tape delay classes take
minutes each; started last, any of them would finish long after every other
worker had gone idle. With `--dist loadscope` each class stays on one worker,
so a setUpClass runs once.

CI_SHARD_UNITS names a file of unittest classes, one `path::Class` a line:
`tools/ci_shards.py` sets it so a shard runs only its share of the suite.
"""

import os

#: Files whose tests start first, slowest first.
SLOW_FIRST = ("test_lifecycle_matrix.py", "test_node_matrix.py",
              "test_cpython_effects_reverb.py",
              "test_cpython_effects_tapedelay.py")


def pytest_collection_modifyitems(config, items):
    def rank(item):
        name = item.path.name
        return SLOW_FIRST.index(name) if name in SLOW_FIRST else len(SLOW_FIRST)

    items.sort(key=rank)

    listed = os.environ.get("CI_SHARD_UNITS")
    if listed:
        with open(listed) as handle:
            wanted = set(line.strip() for line in handle if line.strip())
        keep, drop = [], []
        for item in items:
            unit = item.nodeid.rsplit("::", 1)[0]
            (keep if unit in wanted else drop).append(item)
        missing = wanted - set(item.nodeid.rsplit("::", 1)[0]
                               for item in keep)
        if missing:
            raise ValueError("CI_SHARD_UNITS names classes pytest did not "
                             "collect: %s" % ", ".join(sorted(missing)[:5]))
        if drop:
            config.hook.pytest_deselected(items=drop)
        items[:] = keep
