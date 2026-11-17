#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Split a test run across parallel CI jobs, so a full run finishes in
minutes instead of an hour.

    python tools/ci_shards.py run INDEX COUNT [PATHS...]   # run one shard
    python tools/ci_shards.py plan COUNT [PATHS...]        # print the split
    python tools/ci_shards.py matrix PYTHONS OTHERS [PATHS...]  # CI's jobs
    python tools/ci_shards.py weights REPORT...            # refresh weights

PATHS are the test files to run (default `tests`): the whole suite, or the
files `tools/scoped_tests.py --ci` chose for a pull request.

**The units.** Each unittest class is a unit, except the two lifecycle
matrices (`TestMatrix`, `TestNodeMatrix`), whose units are the effect
classes and audiodsp nodes they run: the classes and nodes their own scope
rules pick (LIFECYCLE_CHANGED_FROM, LIFECYCLE_CLASSES), cut into one unit
each. Units are dealt heaviest first onto the lightest shard, by
`tools/ci_weights.json` (seconds of one core, measured in CI; a unit not
listed weighs DEFAULT). Every shard computes the same deal from the same
collection, so every collected test runs in exactly one shard, and `run`
checks that before it starts.

**A shard** runs in three steps, one after another, so no step competes
with another for the runner's cores:

1. its unittest classes, under pytest-xdist on every core;
2. the classes in POOLED, which spread their own cells over every core
   (KIT_JOBS), one at a time;
3. its share of the two matrices, each cell group in a process of its own
   (LIFECYCLE_CLASSES, the matrix's own subset switch).

It exits non-zero if any step failed, and writes what each unit cost to
`shard-times-INDEX.json` for `weights`.
"""

import json
import math
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEIGHTS_FILE = os.path.join(ROOT, "tools", "ci_weights.json")
LIFECYCLE = "tests/test_lifecycle_matrix.py::TestMatrix"
NODE = "tests/test_node_matrix.py::TestNodeMatrix"

#: Unittest classes whose slow test spreads its cells over KIT_JOBS
#: processes (kit_ceiling.run). They run on their own, after the rest.
POOLED = (
    "tests/test_cpython_effects_flanger.py::TheSurface",
    "tests/test_cpython_effects_chorus.py::TheSurface",
)

#: Seconds of one core for a unit `ci_weights.json` does not list yet.
DEFAULT = {"test": 5.0, "class": 120.0, "node": 60.0}

#: Seconds of test time a shard aims at: with the job's setup, about
#: 20 minutes from start to finish.
TARGET = 900.0

#: Cores a hosted Linux runner has; `matrix` plans for it.
CORES = 4

#: How long a unit takes on each runner, against the Linux runner the
#: weights were measured on.
SPEED = {"ubuntu-latest": 1.0, "windows-latest": 1.6, "macos-latest": 0.6}

MAX_SHARDS = 8


def _env():
    return dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                PYTHONPATH=os.pathsep.join(
                    [ROOT] + [p for p in [os.environ.get("PYTHONPATH")]
                              if p]))


def collect(paths):
    """The unittest classes pytest collects under `paths`, as node ids."""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider"] + list(paths),
        cwd=ROOT, env=_env(), capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit("collection failed:\n%s%s" % (done.stdout[-3000:],
                                                       done.stderr[-3000:]))
    found = []
    for line in done.stdout.splitlines():
        parts = line.split("::")
        if len(parts) == 3:
            unit = parts[0] + "::" + parts[1]
            if unit not in found:
                found.append(unit)
        elif "::" in line:
            raise SystemExit("a test outside a class: %s" % line)
    return found


def matrix_names():
    """(classes, nodes) the two matrices run, by their own scope rules."""
    sys.path.insert(0, ROOT)
    from tests.test_lifecycle_matrix import classes
    from tests.test_node_matrix import names
    return classes(), names()


def units(paths):
    """[(kind, name)]: every unit of the run, sorted."""
    found = []
    tests = collect(paths)
    classes = nodes = ()
    if LIFECYCLE in tests or NODE in tests:
        classes, nodes = matrix_names()
    for unit in tests:
        if unit == LIFECYCLE and classes:
            found += [("class", name) for name in classes]
        elif unit == NODE and nodes:
            found += [("node", name) for name in nodes]
        else:
            # A matrix with nothing in its scope still runs once, as a
            # plain test: it checks the empty selection.
            found.append(("test", unit))
    return sorted(set(found))


def load_weights():
    with open(WEIGHTS_FILE) as handle:
        table = json.load(handle)
    return {(kind, name): seconds for kind, names in table.items()
            for name, seconds in names.items()}


def weight(weights, unit):
    return weights.get(unit, DEFAULT[unit[0]])


def deal(found, count, weights):
    """[[unit]] per shard and each shard's load: heaviest first onto the
    lightest shard."""
    shards = [[] for _ in range(count)]
    load = [0.0] * count
    for unit in sorted(found, key=lambda u: (-weight(weights, u), u)):
        i = min(range(count), key=lambda k: (load[k], k))
        shards[i].append(unit)
        load[i] += weight(weights, unit)
    return shards, load


def count_for(found, weights, speed=1.0):
    total = sum(weight(weights, u) for u in found) * speed
    return max(1, min(MAX_SHARDS, math.ceil(total / CORES / TARGET)))


def matrix(pythons, others, paths):
    """The test jobs, as a JSON list for `strategy.matrix.include`: every
    Python in `pythons` on Linux and the first of them on each runner in
    `others`, each cut into as many shards as its share of the weights
    needs (or CI_SHARDS each, when it is set)."""
    weights = load_weights()
    found = units(paths)
    runs = [("ubuntu-latest", py) for py in pythons]
    runs += [(os_, pythons[0]) for os_ in others]
    fixed = int(os.environ.get("CI_SHARDS") or 0)
    jobs = []
    for os_, py in runs:
        count = fixed or count_for(found, weights, SPEED[os_])
        for index in range(1, count + 1):
            jobs.append({"os": os_, "python": py, "shard": index,
                         "of": count})
    return jobs


def _junit_times(path):
    """{unit: seconds} from a pytest junit file."""
    out = {}
    if not os.path.isfile(path):
        return out
    for case in ET.parse(path).getroot().iter("testcase"):
        cls = case.get("classname", "")
        module, _, name = cls.rpartition(".")
        unit = module.replace(".", "/") + ".py::" + name
        out[unit] = out.get(unit, 0.0) + float(case.get("time") or 0)
    return out


def _lifecycle_times(path):
    out = {}
    if os.path.isfile(path):
        with open(path) as handle:
            for line in handle:
                name, seconds = line.split()
                out[name] = out.get(name, 0.0) + float(seconds)
    return out


def _pytest(label, args, extra, failed):
    argv = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"] + args
    print("::group::%s" % label, flush=True)
    for name, value in sorted(extra.items()):
        print("  %s=%s" % (name, value), flush=True)
    began = time.monotonic()
    done = subprocess.run(argv, cwd=ROOT, env=dict(_env(), **extra))
    print("::endgroup::", flush=True)
    seconds = time.monotonic() - began
    print("%s: exit %d after %.0f s" % (label, done.returncode, seconds),
          flush=True)
    if done.returncode != 0:
        failed.append(label)
    return seconds


def run(index, count, paths):
    weights = load_weights()
    found = units(paths)
    shards, load = deal(found, count, weights)
    assert sorted(u for s in shards for u in s) == found, "a unit was lost"
    share = shards[index]
    print("shard %d of %d: %d of %d units, %.0f of %.0f core seconds" % (
        index + 1, count, len(share), len(found), load[index], sum(load)),
        flush=True)
    jobs = str(os.cpu_count() or 1)
    scratch = os.path.join(ROOT, ".shard")
    os.makedirs(scratch, exist_ok=True)
    failed = []
    times = {"test": {}, "class": {}, "node": {}}

    plain = [n for k, n in share if k == "test" and n not in POOLED]
    pooled = [n for k, n in share if k == "test" and n in POOLED]
    if plain:
        listed = os.path.join(scratch, "units.txt")
        with open(listed, "w") as handle:
            handle.write("\n".join(plain) + "\n")
        files = sorted(set(n.split("::")[0] for n in plain))
        junit = os.path.join(scratch, "plain.xml")
        _pytest("unittest classes", files + [
            "-n", "auto", "--dist", "loadscope", "--durations=25",
            "--junitxml", junit], {"CI_SHARD_UNITS": listed}, failed)
        times["test"].update(_junit_times(junit))
    for unit in pooled:
        junit = os.path.join(scratch, "pooled.xml")
        seconds = _pytest(unit, [unit, "--durations=10", "--junitxml", junit],
                          {"KIT_JOBS": jobs}, failed)
        times["test"][unit] = seconds * int(jobs)
    for kind, target in (("class", LIFECYCLE), ("node", NODE)):
        names = [n for k, n in share if k == kind]
        if not names:
            continue
        spent = os.path.join(scratch, kind + ".times")
        if os.path.exists(spent):
            os.remove(spent)
        _pytest("%s matrix: %s" % (kind, ", ".join(names)),
                [target, "--durations=5"],
                {"LIFECYCLE_CLASSES": ",".join(names),
                 "LIFECYCLE_TIMES": spent}, failed)
        times[kind].update(_lifecycle_times(spent))

    report = os.path.join(ROOT, "shard-times-%d.json" % (index + 1))
    with open(report, "w") as handle:
        json.dump(times, handle, indent=1, sort_keys=True)
    if failed:
        print("shard %d failed: %s" % (index + 1, "; ".join(failed)))
        return 1
    return 0


def refresh(reports):
    """Fold shard reports into ci_weights.json: a unit's new weight is the
    largest a report gives it, so a slow runner errs towards balance."""
    weights = {"test": {}, "class": {}, "node": {}}
    for path in reports:
        with open(path) as handle:
            got = json.load(handle)
        for kind, names in got.items():
            for name, seconds in names.items():
                old = weights[kind].get(name, 0.0)
                weights[kind][name] = round(max(old, seconds), 1)
    with open(WEIGHTS_FILE, "w") as handle:
        json.dump(weights, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print("wrote %s: %d units" % (WEIGHTS_FILE, sum(len(v) for v in
                                                    weights.values())))
    return 0


def main(argv):
    if len(argv) >= 4 and argv[1] == "run":
        return run(int(argv[2]) - 1, int(argv[3]), argv[4:] or ["tests"])
    if len(argv) >= 3 and argv[1] == "plan":
        count = int(argv[2])
        shards, load = deal(units(argv[3:] or ["tests"]), count,
                            load_weights())
        for i, share in enumerate(shards):
            print("shard %d: %.0f core seconds, %d units" % (
                i + 1, load[i], len(share)))
        return 0
    if len(argv) >= 4 and argv[1] == "matrix":
        print(json.dumps(matrix(json.loads(argv[2]), json.loads(argv[3]),
                                argv[4:] or ["tests"])))
        return 0
    if len(argv) >= 3 and argv[1] == "weights":
        return refresh(argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
