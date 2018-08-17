## Toxish-Conda Demo

To list commands:

```sh
invoke -l
```

To run all test envs:

```sh
invoke -e
```

To launch ipython within an env:

```sh
invoke -l ipython
```

To run a single test env:

```sh
invoke -e py36
```

To setup a test env:

```sh
invoke -e py27.setup
```
