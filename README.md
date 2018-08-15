# Tox-alike via Invoke & Conda

A simple proof-of-concept for [tox]-style multi-environment testing via
conda environments. Utilizes [invoke] to declare a matrix of [conda]
environments covering multiple python versions. This is *likely*
package-agnostic, and could be used to declare a matrix of arbitrary
dependency versions.

Environments are created under `.env`, with a version-specific prefix.
Each environment is updated to include the contents of `environment.yml`
for before invoking `pytest.` See `tasks.py` for the meat-and-potatos.

## Examples

To list commands:

```sh
invoke -l
```

To run all test envs:

```sh
invoke -e run
```

To run a single test env:

```sh
invoke -e py36.run
```

To setup a test env:

```sh
invoke -e py27.setup
```

## Bugs

* `invoke`'s de-dupe logic doesn't mesh well with the use of lexical
  closures in `tasks.py`. This requires disabling dedupe via
  `invoke.yaml`.


[invoke]: http://www.pyinvoke.org/
[conda]: https://conda.io/docs/
[tox]: https://tox.readthedocs.io
