# BitTorrent - A peer to peer file sharing protocol

# Main features 
- Requesting rarest first piece
- Unchoking of top 4 peers
- optimistic unchoking
- Seeding (in public networks only)
- limiting peer connection
- Announcing to HTTP and UDP tracker

# Installation from sources
To install the client in developer mode, write
```shell
make dev-install 
```
To install the client in user mode, write
```shell
make install
```

# Uninstallation 
To uninstall client in developer mode
```shell
make dev-uninstall
```

To uninstall client in user mode
```shell
make uninstall
```

# Usage
In Developer mode
```shell
./bittorrent-cli torrentfile [OPTIONS]
```
In user mode
```shell
bittorrent-cli torrentfile [OPTIONS]
```

# Background
The bittorrent is a peer to peer file sharing protocol. In the tradiation
server-client model there is limited bandwidth on the server side, hence as
the number of client increases, the bandwidth gets share between them, hence
each client get small throughput even they may have good amount of bandwidth.
To solve this problem the bittorrent protocol uses existing client to share
the files with each other. This reduces the burden on the server and
effectively utilizes the peers the bandwidth.

# Implementation details

## Parsing Torrent file
The torrent file contains the information about the torrent in B-Encoded format
which needs to be decoded. Generally the torrent file contains following
keys in the B-Encoded format.
| Key          | Description                                                                  |
| ---          | ---                                                                          |
| announce     | The url of the tracker                                                       |
| info         | This maps to the dictionary with keys below                                  |
| name         | Suggested name to save the file or directory                                 |
| piece length | length of the individual piece in bytes                                      |
| pieces       | Maps to the SHA1 of each piece                                               |
| length       | in case of single file, length of the file in bytes                          |
| files        | in case of multiple file, contains the list of dictionary of lenght and path |

## Announcing
there are two types of the tracker, HTTP and UDP,
For the HTTP tracker GET requet has the following keys:
| Key        | Description                                                                          |
| ---        | ---                                                                                  |
| info_hash  | The 20 byte sha1 hash of the bencoded form of the info value from the metainfo file. |
| peer_id    | The 20 byte randomly generated peer id by the client                                 |
| uploaded   | The total amount uploaded till now                                                   |
| downloaded | The total amount downloaded till now                                                 |
| left       | Number of the bytes client still has to download                                     |
| event      | specifies the event                                                                  |

The HTTP tracker sends the response containing the bencoded dictionary of
following keys
| Key      | Description                                                                                               |
| ---      | ---                                                                                                       |
| failure  | Human readable string explaining why query failed                                                         |
| interval | number of seconds the downloader should wait between regular rerequest                                    |
| peers    | contains the list of dictionaries corrosponding to the peer each of which containing peer_id, ip and port |


The UDP announce request is much more complex and can be found at
[bep_0015](https://www.bittorrent.org/beps/bep_0015.html) 

## Peer communication
After getting the list of the peer, the client start connecting to each peer
and create the thread for each of the peer. Each thread handles the
communication related to the specific peer. The peer protocol start by
exchanging the handshake. After completing the handshake there is optional
message called bitfield which gives the information about the pieces that the
peer already has. 
Along with each peer there are two three schedulers which scedules the regular 
keep alives, sending of the have messages, and requesting of the pieces.
All the peer thread communicate via global torrent object. which decides the
unchoking of the peer as well as the rarity of the piece.

### Rarest first
To determine the rarest first the bitfield recvd from the each peer is used.
when the peer thread recvs the bitfield it updates the torrent object. The
requesting tread sort the list of pieces on the basis of their count and
request them on the corrosponding peer. 

### Top 4
Each peer object maintains the length of the data received from that peer. This
information is used by the torrent object to unchoke the torrent by calculating
download speed of the torrent.

### Optimistic unchocking
After some interval the unchoked peer with the least download speed is choked
and the new peer from the peer list is unchoke, this peer is selected in round 
robin fashion.


## File IO
When peer completely recieves the piece it verifies the sha1 of that piece and
after verification it writes the piece to the file. While writing the piece the
fileio takes care of the overlapping piece since it has to be broken into the
two different chunk. 











