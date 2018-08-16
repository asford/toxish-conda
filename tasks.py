import os

import functools


import collections
from typing import Tuple

import invoke
from invoke import Collection

import attr


# Workaround for invoke dedupe only inspecting function body,
# and not respecting function closure or method __self__


@attr.s(hash=True)
class _fwrap:
    """Wrap a function in callable object, breaking six.get_function_body."""

    f = attr.ib()

    def __attrs_post_init__(self):
        functools.update_wrapper(self, self.f)

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


@functools.wraps(invoke.task)
def task(*args, **kwargs):
    """Wrap invoke.task to prevent task-dedupe of closures."""
    if len(args) == 1 and not isinstance(args[0], invoke.Task):
        return invoke.task(_fwrap(args[0]), **kwargs)
    else:

        def _wrap(f):
            return invoke.task(*args, **kwargs)(_fwrap(f))

        return _wrap


@functools.wraps(invoke.Task)
def Task(f, *args, **kwargs):
    """Wrap invoke.Task to prevent task-dedupe of closures."""
    return invoke.Task(_fwrap(f), *args, **kwargs)


def _tuple_str(s):
    return (s,) if isinstance(s, str) else tuple(s)


@attr.s(auto_attribs=True, frozen=True)
class CondaRun:
    commands: Tuple[str] = attr.ib(converter=_tuple_str)

    env_path: str
    env_pins: Tuple[str] = attr.ib(converter=_tuple_str)
    env_files: Tuple[str] = attr.ib(converter=_tuple_str)

    def clean(self, c):
        c.run(f"rm -rf {self.env_path} ")

    def setup(self, c):
        if not os.path.exists(self.env_path):
            c.run(f"conda create -y -p {self.env_path}")

        c.run(f"rm -f {self.env_path}/conda-meta/pinned")
        for p in self.env_pins:
            c.run(f"echo {p} >> {self.env_path}/conda-meta/pinned")

        for f in self.env_files:
            c.run(f"conda env update -q -p {self.env_path} -f {f}")

    def run(self, c):
        with c.prefix(f"eval `conda shell.posix activate {self.env_path}`"):
            for command in self.commands:
                c.run(command)

    def bind(self, collection):
        clean = Task(self.clean)
        setup = Task(self.setup)
        run = Task(self.run, pre=[setup], default=True)

        collection.add_task(clean)
        collection.add_task(setup)
        collection.add_task(run)

        return collection


def setup_envs(
    test_command,
    env_to_pins,
    env_prefix=".env",
    env_files="environment.yml",
    col=None,
):
    if col is None:
        col = Collection()

    all_tasks = collections.defaultdict(list)

    for env_name, env_pins in env_to_pins.items():
        run = CondaRun(
            test_command, f"{env_prefix}/{env_name}", env_pins, env_files
        )

        env_col = run.bind(Collection(env_name))

        col.add_collection(env_col)

        for task_name, env_task in env_col.tasks.items():
            all_tasks[task_name].append(env_task)

    for task_name, tasks in all_tasks.items():
        col.add_task(
            Task(
                lambda c: None,
                pre=tasks,
                name=task_name,
                default=(task_name == "run"),
            )
        )

    return col


ns = setup_envs(
    "pytest",
    {
        "py27": ["python=2.7"],
        "py35": ["python=3.5"],
        "py36": ["python=3.6"],
        "py37": ["python=3.7"],
    },
)

ns = setup_envs(Collection(), envs)
