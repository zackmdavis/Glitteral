import os
from invoke import task, run

# TODO: robustness to other current working directories

def compile(sourcefile, ir=False):
    run("bin/glitteralc {} {}".format(sourcefile, "--just-rust" if ir else ''),
        # rustc is believed to only output color if it thinks it's
        # connected to an actual terminal
        pty=True)

def examplestream():
    for filename in filter(lambda fn: fn.endswith(".gltrl"), os.listdir("eg")):
        yield filename[:-6]

@task
def clean():
    # clean generated Rust
    print("cleaning generated Rust ...")
    run("rm -f preprototype/__*_compiled.rs eg/__*_compiled.rs")
    # clean compiled executables
    print("cleaning executables ...")
    run("rm -f preprototype/demo")
    for example_name in examplestream():
        executable_path = os.path.join("eg", example_name)
        if os.access(executable_path, os.X_OK):
            print("removing {}".format(executable_path))
            os.unlink(executable_path)
    print("clean!")

@task
def test():
    print("running internal tests ...")
    run("cd preprototype/tests; python3 -m unittest")
    print("running output tests ...")
    run("cd eg/tests; python3 -m unittest")

@task
def demo(ir=False):
    compile("preprototype/demo.gltrl", ir=ir)

@task
def eg(example, ir=False):
    if example == "all":
        print("compiling all demos ...")
        for example_name in examplestream():
            print("compiling {} ...".format(example_name))
            compile("eg/{}.gltrl".format(example_name), ir=ir)
    else:
        print("compiling {} ...".format(example))
        compile("eg/{}.gltrl".format(example), ir=ir)
