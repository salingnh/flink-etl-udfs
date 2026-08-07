# Deploying `flink-etl-udfs` to Apache Flink

This document describes how Python dependencies are packaged for the Flink cluster and why the repository uses separate requirements files.

## Dependency audit

At version `0.3.0`, the source tree has the following dependency profile:

- `flink_etl_udfs.core.*`: Python standard library only.
- `flink_etl_udfs.udfs.*`: imports `pyflink.table.udf`.
- `flink_etl_udfs.registry`: imports PyFlink types lazily / for registration.
- No current scalar UDF imports `phonenumbers`, `pydicom`, `hl7apy`, `xarray`, `astropy`, `rapidfuzz`, or other third-party domain libraries.

This means the library wheel is lightweight. Domain-specific parsers should remain outside the scalar UDF process unless the UDF implementation actually imports them.

## Requirements files

### `requirements.txt`

Production third-party dependencies that must be installed in the remote Python UDF worker when using Flink dependency management.

Current version: intentionally contains no active package because all scalar transformations are standard-library-only.

When a new UDF starts importing a third-party package, pin it here, for example:

```text
phonenumbers==9.0.10
```

Do not add test/build tools to this file.

### `requirements-flink.txt`

Provides the `pyflink` Python package for environments that must bootstrap PyFlink themselves:

```text
apache-flink==2.3.0
```

The package version must match the Flink cluster version. A custom Docker image, virtualenv archive, developer workstation, or standalone Python runtime can install this file.

Do not normally pass this file as per-job `--pyRequirements` to a matching Flink distribution. Flink's Python runtime is part of the execution environment; reinstalling a large `apache-flink` wheel for every job/worker is unnecessary and can create version conflicts.

### `requirements-dev.txt`

Only for local tests, linting, type checking, and wheel builds.

## Recommended deployment: Flink distribution already provides the matching PyFlink runtime

Build the UDF wheel:

```bash
python -m pip install -r requirements-dev.txt
python -m build
```

Submit the job with the library wheel and worker requirements:

```bash
./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.3.0-py3-none-any.whl \
  --pyRequirements requirements.txt
```

`--pyFiles` places the wheel on the Python path of the client and remote Python UDF workers. `--pyRequirements` installs worker-side third-party dependencies defined by `requirements.txt`.

Because `requirements.txt` currently has no active packages, the command is safe today and is already prepared for future UDF dependencies.

## Custom Docker image or Python virtualenv

If your container/venv does not already contain PyFlink, bootstrap both layers explicitly:

```bash
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install --no-deps dist/flink_etl_udfs-0.3.0-py3-none-any.whl
```

Verify that PyFlink matches the cluster:

```bash
python -c "import pyflink; print(pyflink.__version__)"
./bin/flink --version
```

Both should be on the same Flink release line, currently `2.3.0` for this repository.

## Offline / restricted cluster

Prepare packages on a machine with package-index access using the same operating system, architecture, and Python version as the Flink workers:

```bash
mkdir -p wheelhouse
python -m pip download -r requirements.txt -d wheelhouse
```

Then provide the requirements file and cache directory to the Flink job. Flink supports a requirements cache for clusters without package-index access.

For a custom Python environment, you can also install directly from the cache:

```bash
python -m pip install \
  --no-index \
  --find-links wheelhouse \
  -r requirements.txt
```

If you also need to bootstrap PyFlink itself in an offline custom image, prepare `requirements-flink.txt` separately because the Apache Flink Python package has many transitive dependencies and must match the cluster release.

## What belongs in pip requirements vs connector JARs

Python requirements do **not** replace Flink connector JARs.

Examples:

- Kafka SQL connector -> Flink connector JAR / plugin.
- Elasticsearch connector -> Flink connector JAR.
- JDBC driver -> Java JAR.
- `phonenumbers`, `pydicom`, `rapidfuzz` used inside a Python UDF -> `requirements.txt`.
- `flink-etl-udfs` itself -> wheel via `--pyFiles`, or install the wheel in the custom Python environment.

## Adding a new dependency

When adding a third-party import to `src/`:

1. Pin the pip package in the correct requirements file.
2. Keep the package version compatible with Python 3.9-3.12 and the target Flink worker platform.
3. Add tests for the code path using the dependency.
4. If the dependency is large or performs I/O, reconsider whether it belongs inside a scalar UDF.
5. Update `tests/test_dependencies.py` so the import-to-pip mapping remains explicit.
6. For offline deployments, refresh the wheel/package cache.

The dependency-contract test intentionally fails if source code introduces an unknown external import without declaring how it is supplied to the cluster.

## Parser libraries from the research roadmap

The research documents mention libraries such as `pydicom`, `hl7apy`, `stix2`, `xarray`, `cfgrib`, `astropy`, and geospatial/tooling libraries. They are not installed by default because the current implementation only normalizes scalar identifiers/metadata.

If those parsers are introduced into a separate ingestion service, keep their dependencies with that service instead of installing them on every Flink Python worker. Add them to this repository only when runtime code here directly imports them.
