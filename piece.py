class Status:
    REQUESTED   = 1
    DOWNLOADING = 2
    COMPLETED   = 3

class BlockLengthError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Pieces(list):

    def __init__(self, *args, **kwargs):
        self.bitfield = bitfield
        super().__init__(*args, **kwargs)

    def add_bitfield(self, bitfield):
        bitfield_int = int.from_bytes(bitfield, "big")
        for pieces in self:
            bit = bitfield_int & 1
            bitfield_int = bitfield_int >> 1
            if(bit):
                pieces.piece_count += 1


class Piece:

    MAX_BLOCK_SIZE = 1<<32

    def __init__(self, index, length, sha, data=None, status=None):
        self.index          = index
        self._length        = length
        self.status         = status
        self.sha            = sha
        self.piece_count    = 0           #piece count shows the avalibility of
        self._data          = BYTEARRAY

    def __len__(self):
        return self._length

    @property
    def data(self):
        return self._data

    def add_block(self, begin, block):
        if(self._data == None):
            self._data = bytearray(self._length)
        self._data[begin:begin + len(block)] = block
        if(block_index == self._length):
            self.status = Status.COMPLETED
    
    def request(self, peer):
        start = 0
        while(start < self._length):
            length = min(self._length - start, MAX_PIECE_SIZE)
            peer.request(self.index, start, length)
            start += length
        return

    def discard_piece_data(self):
        self._data = None



