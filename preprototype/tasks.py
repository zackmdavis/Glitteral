from invoke import task, run

@task
def clean():
    run("rm __glitteral_compiled.rs demo")
    print("clean!")

def compile(sourcefile, ir=False):
    run("./glitteralc {} {}".format(sourcefile, "--just-rust" if ir else ''))

@task
def demo(ir=False):
    compile("demo.gltrl", ir=ir)

@task
def eg(example, ir=False):
    compile("../eg/{}.gltrl".format(example), ir=ir)
