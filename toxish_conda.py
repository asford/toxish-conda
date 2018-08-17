import os

import functools

import collections
from typing import Tuple

import invoke
from invoke import Collection

import attr


class Task(invoke.Task):
    """Workaround for invoke dedupe.

    Modified task subclass that *only* checks for body function equality, rather
    than deferring to function body comparison. Handles cases where task body
    depends on lexical closure or __self__.
    """

    def __eq__(self, other):
        """Compare body callable by equality."""
        if self.name != other.name:
            return False

        return self.body == other.body

    def __hash__(self):
        """Dispatch to super hash to support task-as-key."""
        return invoke.Task.__hash__(self)


# Bind workaround class into @task decorator.
task = functools.partial(invoke.task, klass=Task)


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
