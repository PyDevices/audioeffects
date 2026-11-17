#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Decide what a release gate has to run.

    python tools/gate_plan.py REF [--mode auto|full]   # in a checkout of REF
    python tools/gate_plan.py --selftest

Prints `mode=reuse` or `mode=full`, `since=` and `why=...` as lines for
$GITHUB_OUTPUT. A reuse names in `since` the release tag before this one:
the gate then runs the tests scoped to what changed since it, besides the
wheel, the API validation and the library smoke it always runs.

A final release (`vX.Y.Z`) always runs the whole suite, and so does anything
this script cannot prove. A pre-release (`.devN`, `aN`, `bN`, `rcN`) may rely
on a full run its code already passed, when all of this holds:

1. walking back along main from the release commit, the first commit that has
   a Tests workflow run for a push has one that completed with `success`:
   that run is the full matrix, every supported Python and both other
   platforms, on that commit;
2. every file the release commit changed since that commit is one the Tests
   workflow ignores (`paths-ignore` in tests.yml: the release commit itself
   changes only VERSION and CHANGELOG.md), so no test could see a difference.

The proof is the commit's SHA and the run's conclusion, printed in the log.
"""

import fnmatch
import json
import os
import re
import subprocess
import sys

#: tests.yml's paths-ignore for push, kept here because a change to either
#: has to be made to both: _the_two_lists_agree checks it.
IGNORED = ("docs/**", "README.md", "ROADMAP.md", "CHANGELOG.md", "AGENTS.md",
           "LICENSE", "VERSION")

FINAL = re.compile(r"^v?\d+\.\d+\.\d+$")
LOOKBACK = 60


def is_final(ref):
    return bool(FINAL.match(ref.rsplit("/", 1)[-1]))


def ignored(path):
    return any(fnmatch.fnmatchcase(path, pat) for pat in IGNORED)


def decide(ref, mode, commits, push_runs, changed):
    """(mode, why). `commits` is the release commit and its ancestors on main,
    newest first; `push_runs(sha)` the Tests push runs for a commit as
    {"conclusion", "status", "url"} dicts; `changed(sha)` the paths that
    differ between `sha` and the release commit."""
    if mode == "full":
        return "full", "a full run was asked for"
    if is_final(ref):
        return "full", "%s is a final release: it runs the whole suite" % ref
    for sha in commits:
        runs = push_runs(sha)
        if not runs:
            continue
        good = [r for r in runs
                if r["status"] == "completed" and r["conclusion"] == "success"]
        if not good:
            return "full", "the Tests run for %s did not succeed (%s)" % (
                sha[:8], ", ".join("%s/%s" % (r["status"], r["conclusion"])
                                   for r in runs))
        loose = [p for p in changed(sha) if not ignored(p)]
        if loose:
            return "full", ("%s changed since the passing run on %s: %s"
                            % (", ".join(loose[:5]), sha[:8], ref))
        return "reuse", ("%s is a pre-release; the full Tests matrix passed on "
                         "%s (%s) and nothing the suite reads changed since"
                         % (ref, sha, good[0]["url"]))
    return "full", "no Tests push run in the last %d commits" % len(commits)


def git(*args):
    return subprocess.run(("git",) + args, check=True, capture_output=True,
                          text=True).stdout


def push_runs(sha):
    out = subprocess.run(
        ["gh", "api", "repos/%s/actions/workflows/tests.yml/runs" %
         os.environ["GITHUB_REPOSITORY"], "-X", "GET", "-f", "head_sha=" + sha,
         "-f", "event=push", "-f", "branch=main", "-f", "per_page=20"],
        check=True, capture_output=True, text=True).stdout
    return [{"status": r["status"], "conclusion": r["conclusion"],
             "url": r["html_url"]} for r in json.loads(out)["workflow_runs"]]


def selftest():
    run = lambda c: [{"status": "completed", "conclusion": c, "url": "u"}]
    none = lambda sha: []
    known = lambda table: (lambda sha: table.get(sha, []))
    cases = (
        # final release, whatever passed
        (("v1.2.3", "auto", ["a", "b"], known({"b": run("success")}),
          lambda s: []), "full"),
        # pre-release, release commit ignored files only
        (("v1.2.3.dev4", "auto", ["a", "b"], known({"b": run("success")}),
          lambda s: ["VERSION", "CHANGELOG.md", "docs/x.md"]), "reuse"),
        # pre-release, a code file changed since
        (("v1.2.3rc1", "auto", ["a", "b"], known({"b": run("success")}),
          lambda s: ["VERSION", "lib/audioeffects/fuzz.py"]), "full"),
        # the workflow itself changed
        (("v1.2.3a1", "auto", ["a", "b"], known({"b": run("success")}),
          lambda s: [".github/workflows/tests.yml"]), "full"),
        # the last run failed, an older one passed: stop at the failure
        (("v1.2.3.dev1", "auto", ["a", "b", "c"],
          known({"b": run("failure"), "c": run("success")}),
          lambda s: []), "full"),
        # no run at all
        (("v1.2.3.dev1", "auto", ["a", "b"], none, lambda s: []), "full"),
        # a full run asked for
        (("v1.2.3.dev1", "full", ["a"], known({"a": run("success")}),
          lambda s: []), "full"),
        # a ref that is not a tag name counts as a pre-release
        (("refs/heads/work", "auto", ["a"], known({"a": run("success")}),
          lambda s: []), "reuse"),
    )
    for args, want in cases:
        got = decide(*args)[0]
        assert got == want, (args[0], args[1], got, want)
    assert is_final("refs/tags/v0.5.2") and not is_final("v0.5.2.dev4")
    assert not is_final("v0.5.2rc1")
    text = open(os.path.join(os.path.dirname(__file__), "..", ".github",
                             "workflows", "tests.yml")).read()
    listed = re.findall(r"paths-ignore: \[(.*?)\]", text)
    assert listed, "tests.yml has no paths-ignore"
    for one in listed:
        assert tuple(re.findall(r"'([^']+)'", one)) == IGNORED, (
            "tools/gate_plan.py IGNORED differs from tests.yml's paths-ignore")
    print("gate_plan selftest ok")


def previous_tag(head):
    """The newest release tag before `head`, or None."""
    done = subprocess.run(["git", "describe", "--tags", "--abbrev=0",
                           "--match", "v[0-9]*", head + "^"],
                          capture_output=True, text=True)
    return done.stdout.strip() or None


def main(argv):
    if argv[1:] == ["--selftest"]:
        selftest()
        return 0
    ref = argv[1]
    mode = argv[argv.index("--mode") + 1] if "--mode" in argv else "auto"
    head = git("rev-parse", "HEAD").strip()
    commits = git("rev-list", "--first-parent", "-n", str(LOOKBACK),
                  head).split()
    mode, why = decide(
        ref, mode, commits, push_runs,
        lambda sha: git("diff", "--name-only", sha, head).split())
    since = ""
    if mode == "reuse":
        since = previous_tag(head) or ""
        if not since:
            mode, why = "full", "no release tag before %s to scope from" % ref
        else:
            why += "; the tests scoped to what changed since %s run" % since
    print("%s: %s" % (mode, why), file=sys.stderr)
    print("mode=" + mode)
    print("since=" + since)
    print("why=" + why.replace("\n", " "))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
