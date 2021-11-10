import hashlib


class PieceStatus:
    REQUESTED = 1
    DOWNLOADING = 2
    COMPLETED = 3


class BlockLengthError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PieceDiscardingError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Pieces(list):

    def __init__(self, *args, **kwargs):
        self._total_completed_pieces = 0
        super().__init__(*args, **kwargs)

    def __copy__(self):
        copy = Pieces()
        for piece in self:
            piece_copy = piece.__copy__()
            copy.append(piece_copy)
        return copy

    @property
    def total_completed_pieces(self):
        return self._total_complete_pieces

    def add_bitfield(self, bitfield):
        print(len(self))
        bitfield_int = int.from_bytes(bitfield, "big")
        bitfield_int >>= len(bitfield) * 8 - len(self)
        index = len(self) - 1
        while(bitfield_int):
            bit = bitfield_int & 0x01
            if(self[index].piece_count == 0 and bit):
                self._total_completed_pieces += 1
            self[index].piece_count += bit
            print(bit, self[index].piece_count, index)
            bitfield_int >>= 1
            index -= 1
        '''
        for pieces in self:
            print(pieces.index, pieces.piece_count)
            '''
        return

    def get_bitfield(self):
        bitfield = 0
        currentbit = 1
        for piece in reversed(self):
            if piece.piece_count > 0:
                bitfield = bitfield | currentbit
            currentbit = currentbit << 1
        total_pieces = len(self)
        total_bytes = int(total_pieces // 8) + ((total_pieces % 8) > 0)
        bitfield_bytes = bitfield.to_bytes(total_bytes, "big")
        return bitfield_bytes
    
    def add_piece(self, index):
        if(self[index].piece_count == 0):
            self._total_completed_pieces += 1
        self[index].piece_count += 1
        self[index].set_status(PieceStatus.COMPLETED)
        return

    def have_all(self):
        for i in len(self):
            self.add_piece(i)
        return

    def have_none(self):
        self._total_completed_pieces = 0
        for piece in self:
            piece.piece_count = 0
            piece.set_status(None)
        return

    def is_complete(self):
        return self._total_completed_pieces == len(self)



class Piece:

    MAX_BLOCK_SIZE = 1 << 14

    def __init__(self, index, length, sha1: bytes, data=None, status=None):
        self.index = index
        self.piece_count = 0  # piece count shows the avalibility of

        self._length = length
        self._status = status
        self._sha1 = sha1
        self._data = data

    def __len__(self):
        return self._length

    def __lt__(self, piece2):
        return self.piece_count < piece2.piece_count

    def __copy__(self):
        return Piece(self.index, self._length, self.sha1, self.data,
                self._status)

    @property
    def sha1(self):
        return self._sha1

    @property
    def data(self):
        return self._data

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    def add_block(self, begin, block):
        if(self._data is None):
            self._status = PieceStatus.DOWNLOADING
            self._data = bytearray(self._length)
        self._data[begin:begin + len(block)] = block
        if(begin + len(block) == self._length):
            piece_sha1 = hashlib.sha1(self._data).digest()
            if(self._sha1 != piece_sha1):
                self._data = None
                self._status = None
            else:
                self.piece_count += 1
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
            raise PieceDiscardingError(
                "Cant Discard data while the piece is downloading")
        self._data = None
