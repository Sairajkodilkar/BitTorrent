class Status:
    REQUESTED = 1
    DOWNLOADING = 2
    COMPLETED = 3

MAX_BLOCK_SIZE =  

class BlockLengthError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Piece:

    def __init__(self, index, length, sha, data=None, status=None):

        self.index        = index
        self.length       = length
        self.status       = status
        self.piece_count  = 0           #piece count shows the avalibility of
        self.data = data
        self.sha = sha
                                        #the piece in the torrent

def get_block(piece, start, length):
    if(start + length > len(piece):
            raise BlockLengthError("Block lenght exceeds the piece length")
    return piece.data[start][start + length]


