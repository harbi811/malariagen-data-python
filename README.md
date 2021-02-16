# `malariagen_data` - access MalariaGEN public data from Python

This Python package provides convenience methods for accessing public data from MalariaGEN.

Installation:

```bash
$ pip install --pre malariagen-data
```

Usage:

```python
import malariagen_data
ag3 = malariagen_data.Ag3("gs://vo_agam_release/")
```

## Developer notes

Fork and clone this repo:

```bash
$ git clone git@github.com:[username]/malariagen-data-python.git
```

Install [poetry](https://python-poetry.org/docs/#installation) somehow, e.g.:

```bash
$ pip3 install poetry
```

Create development environment:

```bash
$ cd malariagen-data-python
$ poetry install
```

Run tests:

```bash
$ poetry run pytest
```

Bump version, build and publish to PyPI:

```bash
$ poetry version prerelease
$ poetry build
$ poetry publish
```

## Release notes

### Next release (TODO)

* Make public the `Ag3.open_genome()`, `Ag3.open_snp_sites()`, `Ag3.open_site_filters()` and `Ag3.open_snp_genotypes()` methods.
* Add the `Ag3.cross_metadata()` method.

### v0.3.1

* Fix compatibility issue in recent fsspec/gcsfs release.

### v0.3.0

First release with basic functionality in the `Ag3` class for accessing Ag1000G phase 3 data.
