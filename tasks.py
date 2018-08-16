import shutil
import os

import collections
from typing import Tuple

from invoke import task, Collection

import attr


@attr.s(frozen=True, auto_attribs=True)
class CondaRun:
    env_path: str
    env_pins: Tuple[str] = attr.ib(
        converter=lambda s: (s,) if isinstance(s, str) else tuple(s)
    )
    env_files: Tuple[str] = attr.ib(
        converter=lambda s: (s,) if isinstance(s, str) else tuple(s)
    )

    command: str

    def clean(self, c):
        """Remove target environment."""
        shutil.rmtree(self.env_path)

    def setup(self, c):
        """Create and setup target conda environment."""
        if not os.path.exists(self.env_path):
            c.run(f"conda create -y -p {self.env_path}")

        c.run(f"rm -f {self.env_path}/conda-meta/pinned")
        for p in self.env_pins:
            c.run(f"echo {p} >> {self.env_path}/conda-meta/pinned")

        for f in self.env_files:
            c.run(f"conda env update -q -p {self.env_path} -f {f}")

    def run(self, c):
        """Run command within conda environment."""
        with c.prefix(f"eval `conda shell.posix activate {self.env_path}`"):
            c.run(self.command)

    def bind(self, collection):
        setup = task(self.setup)
        run = task(setup, default=True)(self.run)

        collection.add_task(setup)
        collection.add_task(run)

        return collection


def setup_envs(col, envs):
    all_tasks = collections.defaultdict(list)

    for env_name, env_pins in envs.items():
        run = CondaRun(
            f".env/{env_name}", env_pins, "environment.yml", "pytest"
        )

        env_col = run.bind(Collection(env_name))

        col.add_collection(env_col)

        for task_name, env_task in env_col.tasks.items():
            all_tasks[task_name].append(env_task)

    for task_name, tasks in all_tasks.items():
        col.add_task(
            task(*tasks, name=task_name, default=task_name == "run")(
                lambda c: None
            )
        )

    return col


envs = {
    "py27": ["python=2.7"],
    "py35": ["python=3.5"],
    "py36": ["python=3.6"],
    "py37": ["python=3.7"],
}

ns = setup_envs(Collection(), envs)
