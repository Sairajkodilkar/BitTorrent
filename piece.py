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
        self._status         = status
        self.sha            = sha
        self.piece_count    = 0           #piece count shows the avalibility of
        self._data          = data

    def __len__(self):
        return self._length

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value
    
    def add_block(self, begin, block):
        print("addding block")
        if(self._data == None):
            self.status = Status.DOWNLOADING
            self._data = bytearray(self._length)
        self._data[begin:begin + len(block)] = block
        if(begin + len(block) == self._length): 
            piece_sha1 = hashlib.sha1(self._data).digest()
            #print(self.index, piece_sha1)
            if(self.sha != piece_sha1):
                #print("wrong sha1")
                self._data = None
                self.status = None
            else:
                #print("sha matched completed")
                self.status = Status.COMPLETED
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
            self.status = None
            raise PieceDiscardingError("Cant Discard data while the piece is downloading")
        self._data = None



