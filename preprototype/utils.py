import itertools

def push(generator, item):
    """Make-believe that we can push back onto a generator."""
    # Thanks to http://stackoverflow.com/a/2425347
    return itertools.chain([item], generator)

def twopartitions(sliceable):
    return zip(sliceable[::2], sliceable[1::2])
