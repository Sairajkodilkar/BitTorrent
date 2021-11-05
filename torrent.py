from bittorrent.fileio import FileArray,File
from bittorrent.piece import PieceStatus, Piece, Pieces
from bittorrent.peers.peer import Peer
from random import randint


class TorrentStatus:
    LEECHER = 1
    SEEDER = 2
    STOPPED = 3


class Torrent:

    def __init__(self, data_files: FileArray, 
                 peer_id: bytes, peers: list,
                 info_hash: bytes, pieces: Pieces, 
                 status=TorrentStatus.LEECHER):

        self.peers = peers
        self.pieces = pieces

        self._data_files     = data_files
        self._peer_id        = peer_id
        self._info_hash      = info_hash
        self._status         = status
        self._unchoked_peers = []

    def get_status(self):
        if(self._status == TorrentStatus.SEEDER
                or self._status == TorrentStatus.STOPPED):
            return self._status
        for piece in self.pieces:
            if(piece.get_status() != PieceStatus.COMPLETED):
                return TorrentStatus.LEECHER
        self._status = TorrentStatus.SEEDER
        return self._status

    def set_status(self, value):
        self._status = value
        return

    @property
    def peer_id(self):
        return self._peer_id

    @property
    def info_hash(self):
        return self._info_hash

    @property
    def data_files(self):
        return self._data_files

    def _sort_unchoked_peers(self):
        if(self._status == TorrentStatus.LEECHER):
            self._unchoked_peers.sort(
                key=Peer.get_download_speed, reverse=True)
        else:
            self._unchoked_peers.sort(key=Peer.get_upload_speed, reverse=True)

    def unchoke_top_peers(self, peer_limit=5):
        if(not self._unchoked_peers):
            tmp = []
            for i in range(len(self.peers)):
                if(len(tmp) >= peer_limit):
                    break
                if(self.peers[i].pieces.is_complete()):
                    continue
                else:
                    tmp.append(i)
            for i in tmp:
                peer = self.peers.pop(i)
                self._unchoked_peers.append(peer)
                peer.choke(False)

        elif(self.peers):
            self._sort_unchoked_peers()
            slowest_peer = self._unchoked_peers.pop()
            slowest_peer.choke(True)
            # unchoke peers in cyclic manner 
            # this is achieved by appending unchoke peer at last 
            peer = self.peers.pop(0)
            peer.choke(False)
            self.peers.append(slowest_peer)
            self._unchoked_peers.append(peer)
        return

    def add_peers(self, peers):
        self.peers.append(peers)

    def get_completed_piece_count(self):
        count = 0
        for piece in self.pieces:
            if(piece.get_status() == PieceStatus.COMPLETED):
                count += 1
        return count
