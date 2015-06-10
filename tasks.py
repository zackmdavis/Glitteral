import os
from invoke import task, run


def compile(sourcefile, ir=False):
    run("bin/glitteralc {} {}".format(sourcefile, "--just-rust" if ir else ''),
        # rustc is believed to only output color if it thinks it's
        # connected to an actual terminal
        pty=True)

@task
def clean():
    # clean generated Rust
    run("rm -f preprototype/__*_compiled.rs eg/__*_compiled.rs")
    # clean compiled executables
    run("rm -f preprototype/demo")
    for filename in os.listdir("eg"):
        filepath = os.path.join("eg", filename)
        if os.access(filepath, os.X_OK):
            os.unlink(filepath)
    print("clean!")

@task
def test():
    run("cd preprototype/tests; python3 -m unittest")

@task
def demo(ir=False):
    compile("preprototype/demo.gltrl", ir=ir)

@task
def eg(example, ir=False):
    compile("eg/{}.gltrl".format(example), ir=ir)
