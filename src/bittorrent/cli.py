from bittorrent.client import download
import argparse


def main():
    '''
    mandatory:
        torrent_file
    optional
        d: basedirectory --base-dir
        l: peer connection limit --max-connection-limit
        u: peer unchoke limit --max-unchoke-limit
        c: clean download --clean-download
        s: seeding --seeding
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('torrent_file', metavar="Torrent-file", type=str,
                        help="Torrent file to download the torrent")

    parser.add_argument('-d',  '--base-dir', metavar='dir name', type=str,
                        help='where to save download data',
                        required=False, default='')

    parser.add_argument('-l',  '--max-connection-limit', metavar='lim', 
                        type=int,
                        help='Set the limit for maximum peer connections',
                        required=False, default=20)

    parser.add_argument('-u', '--max-unchoke-limit', metavar='lim', type=int,
                        help='Set the limit for max unchoking',
                        required=False, default=5)

    parser.add_argument('-c', '--clean-download',
                        help='Ignore the previously downloaded data and download the file from start',
                        required=False, default=False,
                        action='store_true')

    parser.add_argument('-s', '--seeding', help='Seed the torrent',
                        required=False, default=False, action='store_true')

    args = parser.parse_args()

    download(args.torrent_file, args.max_connection_limit,
             args.max_unchoke_limit, args.base_dir, args.clean_download,
             args.seeding)


if(__name__ == "__main__"):
    main()
