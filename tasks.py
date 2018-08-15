import shutil
import os
from invoke import task, Collection


def setup_env(col, name, packages):
    epath = f".env/{name}"

    @task
    def setup(c, clean=False):
        c.run("mkdir -p .env")

        if os.path.exists(epath) and clean:
            shutil.rmtree(epath)

        if not os.path.exists(epath):
            c.run(f"conda create -y -p {epath}")

        c.run(f"rm -f {epath}/conda-meta/pinned")
        for p in packages:
            c.run(f"echo {p} >> {epath}/conda-meta/pinned")

        c.run(f"conda env update -q -p {epath} -f environment.yml")

    @task(setup)
    def run(c):
        c.run(f"{epath}/bin/pytest")

    col.add_task(setup)
    col.add_task(run)

    return col


def setup_envs(col, envs):
    env_collections = [setup_env(Collection(n), n, p) for n, p in envs.items()]

    run_tasks = [ec.tasks.run for ec in env_collections]
    setup_tasks = [ec.tasks.setup for ec in env_collections]

    @task(*run_tasks)
    def run(c):
        pass

    @task(*setup_tasks)
    def setup(c):
        pass

    for e in env_collections:
        col.add_collection(e)

    col.add_task(run)
    col.add_task(setup)

    return col


envs = {
    "py27": ["python =2.7"],
    "py35": ["python =3.5"],
    "py36": ["python =3.6"],
    "py37": ["python =3.7"],
}

ns = setup_envs(Collection(), envs)
