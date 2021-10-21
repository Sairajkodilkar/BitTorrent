class Status:
    REQUESTED = 1
    DOWNLOADING = 2
    COMPLETED = 3

class Piece:

    def __init__(self, index, status=None):

        self.index        = index
        self.status       = status
        self.piece_count  = 0           #piece count shows the avalibility of
                                        #the piece in the torrent



