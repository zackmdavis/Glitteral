from invoke import task, run

@task
def clean():
    run("rm __glitteral_compiled.rs demo")
