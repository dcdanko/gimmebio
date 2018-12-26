

class ShortReadData:

    def next_batch(self, batch_size):
        pass


class FastqSeqData:

    def __init__(self):
        self.train = ShortReadData()
        self.test = ShortReadData()
