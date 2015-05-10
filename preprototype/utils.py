import itertools

def push(generator, item):
    """Make-believe that we can push back on to a generator."""
    # Thanks to http://stackoverflow.com/a/2425347
    return itertools.chain([item], generator)
