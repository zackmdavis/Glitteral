import functools
import itertools
import logging
import os

class LookaheadStream:
    def __init__(self, generator):
        self.lookahead = None
        self.generator = iter(generator)

    def __iter__(self):
        return self

    def __next__(self):
        if self.lookahead is not None:
            the_next = self.lookahead
            self.lookahead = None
            return the_next
        else:
            return next(self.generator)

    def peek(self):
        if self.lookahead is None:
            self.lookahead = next(self)
        return self.lookahead

    def pop(self):
        return next(self)


def npartitions(n, sliceable):
    return zip(*(sliceable[slice(i, None, n)] for i in range(n)))

twopartitions = functools.partial(npartitions, 2)

def to_int_or_none(intable_maybe):
    try:
        return int(intable_maybe)
    except ValueError:
        return None

def get_logger(name):
    logger = logging.getLogger(name)
    glitteral_debug = os.environ.get('GLITTERAL_DEBUG', "NOTSET")
    level_from_environment = getattr(
        logging, glitteral_debug,
        to_int_or_none(glitteral_debug)
    )
    if level_from_environment is None:
        level_from_environment = logging.DEBUG
    logger.setLevel(level_from_environment)
    logger.addHandler(logging.StreamHandler())
    return logger

def oxford_series(items):
    conjuncts = [str(i) for i in items]
    if len(conjuncts) == 0:
        return ''
    if len(conjuncts) == 1:
        return conjuncts[0]
    if len(conjuncts) == 2:
        return ' and '.join(conjuncts)
    else:
        return ', and '.join(
            [', '.join(conjuncts[:-1]), conjuncts[-1]])
