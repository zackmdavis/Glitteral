import os
from invoke import task, run

# TODO: robustness to other current working directories

def compile(sourcefile, ir=False):
    run("bin/glitteralc {} {}".format(sourcefile, "--just-rust" if ir else ''),
        # rustc is believed to only output color if it thinks it's
        # connected to an actual terminal
        pty=True)

def eg_executable_paths():
    for filename in os.listdir("eg"):
        filepath = os.path.join("eg", filename)
        if os.access(filepath, os.X_OK) and not os.path.isdir(filepath):
            yield filepath

@task
def clean():
    # clean generated Rust
    print("cleaning generated Rust ...")
    run("rm -f preprototype/__*_compiled.rs eg/__*_compiled.rs")
    # clean compiled executables
    print("cleaning executables ...")
    run("rm -f preprototype/demo")
    for executable_path in eg_executable_paths():
        os.unlink(executable_path)
    print("clean!")

@task
def test():
    print("running internal tests ..")
    run("cd preprototype/tests; python3 -m unittest")
    print("running output tests ...")
    run("cd eg/tests; python3 -m unittest")

@task
def demo(ir=False):
    compile("preprototype/demo.gltrl", ir=ir)

@task
def eg(example, ir=False):
    print("compiling {} ...".format(example))
    compile("eg/{}.gltrl".format(example), ir=ir)
