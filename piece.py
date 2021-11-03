import hashlib

class PieceStatus:
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
        index = len(self) - 1
        while(bitfield_int):
            bit = bitfield_int & 0x01
            self[index].piece_count += bit
            bitfield_int >>= 1
            index -= 1
        return

    def get_bitfield(self):
        bitfield = 0
        currentbit = 1
        for piece in self:
            if piece.get_status() == PieceStatus.COMPLETED:
                bitfield = bitfield | currentbit 
            currentbit = currentbit << 1
        total_pieces = len(self)
        total_bytes = int(total_pieces // 8 + total_pieces % 8)
        bitfield_bytes = bitfield.to_bytes(total_bytes, "big")
        return bitfield_bytes

class Piece:

    MAX_BLOCK_SIZE = 1<<14

    def __init__(self, index, length, sha1:bytes, data=None, status=None):
        self.index          = index
        self.piece_count    = 0           #piece count shows the avalibility of

        self._length = length
        self._status = status
        self._sha1   = sha1
        self._data   = data

    def __len__(self):
        return self._length

    def __lt__(self, piece2):
        return self.piece_count < piece2.piece_count

    @property
    def data(self):
        return self._data

    def get_status(self):
        return self._status
    
    def set_status(self, value):
        self._status = value
    
    def add_block(self, begin, block):
        if(self._data == None):
            self._status = PieceStatus.DOWNLOADING
            self._data = bytearray(self._length)
        self._data[begin:begin + len(block)] = block
        if(begin + len(block) == self._length): 
            piece_sha1 = hashlib.sha1(self._data).digest()
            if(self._sha1 != piece_sha1):
                self._data = None
                self._status = None
            else:
                self._status = PieceStatus.COMPLETED
        return

    def request(self, peer):
        start = 0
        self._status = PieceStatus.REQUESTED
        while(start < self._length):
            length = min(self._length - start, self.MAX_BLOCK_SIZE)
            peer.request(self.index, start, length)
            start += length
        return

    def discard_data(self):
        if(self._status == PieceStatus.DOWNLOADING):
            raise PieceDiscardingError("Cant Discard data while the piece is downloading")
        self._data = None



