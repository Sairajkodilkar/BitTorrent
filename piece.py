import hashlib

class Status:
    REQUESTED   = 1
    DOWNLOADING = 2
    COMPLETED   = 3

class BlockLengthError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PieceDiscardingError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Pieces(list):

    def add_bitfield(self, bitfield):
        bitfield_int = int.from_bytes(bitfield, "big")
        for piece in reversed(self):
            bit = bitfield_int & 1
            bitfield_int = bitfield_int >> 1
            if(bit):
                piece.piece_count += 1

    def get_bitfield(self):
        bitfield = 0
        currentbit = 1
        for piece in self:
            if piece.status == Status.COMPLETED:
                bitfield = bitfield | currentbit 
            currentbit = currentbit << 1
        total_pieces = len(self.pieces_list)
        total_bytes = total_pieces / 8 + total_pieces % 8
        bitfield_bytes = bitfield.to_bytes(total_bytes, "big")
        return bitfield

class Piece:

    MAX_BLOCK_SIZE = 1<<14

    def __init__(self, index, length, sha:bytes, data=None, status=None):
        self.index          = index
        self._length        = length
        self.status         = status
        self.sha            = sha
        self.piece_count    = 0           #piece count shows the avalibility of
        self._data          = data

    def __len__(self):
        return self._length

    @property
    def data(self):
        return self._data

    def add_block(self, begin, block):
        if(self._data == None):
            self.status = Status.DOWNLOADING
            self._data = bytearray(self._length)
        self._data[begin:begin + len(block)] = block
        if(begin + len(block) == self._length): 
            self.status = Status.COMPLETED
            if(self.sha != y.digest()):
                self._data = None
                self.status = None
        return

    
    def request(self, peer):
        start = 0
        self.status = Status.REQUESTED
        while(start < self._length):
            length = min(self._length - start, self.MAX_BLOCK_SIZE)
            peer.request(self.index, start, length)
            start += length
        return

    def __lt__(self, piece2):
        return self.piece_count < piece2.piece_count

    def discard_data(self):
        if(self.status == Status.DOWNLOADING):
            raise PieceDiscardingError("Cant Discard data while the piece is downloading")
        self.status = None
        self._data = None



