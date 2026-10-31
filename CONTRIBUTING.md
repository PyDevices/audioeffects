# Contributing to audioeffects

audioeffects is a pure-Python package of 45 effects built on
[audiodsp](https://github.com/PyDevices/audiodsp)'s nodes. A small
documentation correction, a metadata improvement or a focused test for an
existing effect is a good first contribution. A new effect follows the
[runtime API](docs/reference/component-api.md) and declares its
[metadata](docs/reference/metadata.md) explicitly, rather than relying on how a
neighbouring module happens to work.

The package was part of audiocomponents until it moved here. Issue and pull
request numbers written as `audiocomponents#N` in comments and the changelog
refer to that archived repository, and they still resolve at
[PyDevices/audiocomponents](https://github.com/PyDevices/audiocomponents).

## Where things are

| Path | What's there |
|---|---|
| [`lib/audioeffects/`](lib/audioeffects/) | One module per effect, plus `_component.py` (the base every effect is built on) and `rebuilt/`, which only keeps the old `audioeffects.rebuilt.<module>` import paths working. |
| [`tools/validate_api.py`](tools/validate_api.py), [`tools/validate_metadata.py`](tools/validate_metadata.py) | The validators that enforce the runtime API and the metadata manifest. |
| [`tools/effect_probes/`](tools/effect_probes/) | The measurement kit's test signals and their manifest. The audio files are generated, never committed. |
| `tools/` | Rendering and measurement tools besides. |
| `tests/` | The suites. [`tests/support/KIT.md`](tests/support/KIT.md) describes the measurement kit and [`tests/support/LIFECYCLE.md`](tests/support/LIFECYCLE.md) the lifecycle matrix. |
| `docs/` | The documentation site. |
| `AUDIODSP_PIN` | The exact audiodsp commit every gate runs against. |
| `VERSION` | The version the next tag carries. |
| `.github/workflows/` | CI (`tests.yml`, `lint.yml`, `docs.yml`) and the release chain. |

The package keeps its own `pyproject.toml` under `lib/audioeffects/`. That is
what makes it a standalone distribution and what the MIP publisher expects, so
leave the layout alone. It carries the audiodsp floor,
`omnipython-audiodsp>=<release>`, the newest audiodsp *release* that contains the
pin. The floor is not the pin: `AUDIODSP_PIN` may name a commit ahead of it, and
the gates use the pin.

## Set up

```bash
python3 -m venv .venv
.venv/bin/pip install "git+https://github.com/PyDevices/audiodsp@<the commit AUDIODSP_PIN names>"
.venv/bin/pip install numpy pytest pytest-xdist
.venv/bin/pip install --no-deps -e lib/audioeffects
```

The commit is the first line of `AUDIODSP_PIN` that is not a comment. The pin
matters: with a floating core underneath, a failure is unattributable, because
you cannot tell a rewritten effect from a moved node beneath it. A TestPyPI
install of `omnipython-audiodsp` is fine for poking around, but it is not what a
gate result may be reported against.

## Run the tests

CI runs the structural contract:

```bash
python -m pytest tests -n auto --dist loadscope
python tools/validate_api.py
python tests/parity/effects_library_smoke.py
python -m flake8
```

The whole suite takes a long time. [`tools/scoped_tests.py`](tools/scoped_tests.py)
picks the files a change can break:

| Work | Scope |
|---|---|
| One class | `tools/scoped_tests.py class:DeEsser` (that class's tests plus the contract) |
| Kit, `__init__`, or `_component` | `tools/scoped_tests.py auto` (widens from `git diff`) |
| Every effect | `tools/scoped_tests.py effects` |
| Shared promises only | `tools/scoped_tests.py contract` |
| Gate, integration, audit, release | `tools/scoped_tests.py full` |

`--list` prints the choice and runs nothing.

A few tests render under a MicroPython or CircuitPython interpreter as well as
CPython, and skip when they find none. They look for a `bin/micropython` or
`bin/circuitpython` in a folder above the checkout, or for the paths in
`LIFECYCLE_MICROPYTHON` and `LIFECYCLE_CIRCUITPYTHON`. The interpreter has to
be built with the audiodsp commit `AUDIODSP_PIN` names; `tools/provenance_gate.py`
refuses one that is not, since a stale interpreter agrees with itself about
the wrong thing.

## Build the docs

```bash
pip install -r docs/requirements.txt
sphinx-build -W --keep-going -b html docs _site
```

`-W` fails on any warning, as Read the Docs does. The API pages under
[`docs/reference/`](docs/reference/) are generated on every build; don't edit or
commit them. The effects reference page includes
[`lib/audioeffects/README.md`](lib/audioeffects/README.md), which also goes into
the wheel.

## Release

The version is a maintainer's to name, in the release pull request, which
changes `VERSION` and `CHANGELOG.md`. `tag-release.yml` refuses to tag anything
that is not a release version. The chain lives in `.github/workflows/` and calls
the organization's reusable workflows:

1. `prepare-release.yml` opens the release pull request (`VERSION` and
   `CHANGELOG.md`).
2. `tag-release.yml` tags the merged `VERSION`.
3. `publish-release-packages.yml` runs the gates, builds the package from the
   tag, publishes `omnipython-audioeffects` to TestPyPI, requests the
   `audioeffects` MIP entry and, for a final release, uploads to PyPI from the
   `pypi` environment.

Moving `AUDIODSP_PIN` is its own change, with the gates re-run, never a side
effect of other work.
