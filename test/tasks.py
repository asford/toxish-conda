from invoke import task
from toxish_conda import setup_envs

ns = setup_envs(
    "pytest src/proj",
    {
        "py27": ["python=2.7"],
        "py35": ["python=3.5"],
        "py36": ["python=3.6"],
        "py37": ["python=3.7"],
    },
)


@task(ns["py37.setup"])
def ipython(c):
    c.run(".env/py37/bin/ipython", pty=True)


ns.add_task(ipython)
