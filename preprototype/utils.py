import itertools

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


def twopartitions(sliceable):
    return zip(sliceable[::2], sliceable[1::2])
