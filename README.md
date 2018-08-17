# Tox-alike via Invoke & Conda

A simple proof-of-concept for [tox]-style multi-environment testing via conda environments.
Utilizes [invoke] to declare a matrix of [conda] environments covering multiple python versions.
This is *likely* package-agnostic, and could be used to declare a matrix of arbitrary dependency versions.

Environments are created under `.env`, with a version-specific prefix.
Each environment is updated to include the contents of `environment.yml`.
A configurable test command is then executed with each environment activated.

See the minimal demo project is available under [demo](./demo).

## Requirements

`conda` >= 4.5, `attrs`, `invoke` in current shell. Eg:

```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh

conda install invoke attrs
```

## Bugs

* Unlike [tox], does not perform `sdist` & `install`.
* ~~~`invoke`'s de-dupe logic doesn't mesh well with the use of lexical closures in `tasks.py`, This requires disabling dedupe via `invoke.yaml`.~~~


[invoke]: http://www.pyinvoke.org/
[conda]: https://conda.io/docs/
[tox]: https://tox.readthedocs.io
