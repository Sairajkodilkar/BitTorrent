from bittorrent.torrent import TorrentStatus
import sys
import time


def bps_to_kbps(speed):
    return speed / 10e3


def bps_to_mbps(speed):
    return speed / 10e6


def bps_to_gbps(speed):
    return speed / 10e9


def get_percentage_complete(downloaded_piece_count, total_piece_count):
    return (downloaded_piece_count / total_piece_count) * 100


def display_status(client, torrent, peer):

    while(torrent.get_status() != TorrentStatus.STOPPED):
        if(not client.seeding and torrent.get_status() == TorrentStatus.SEEDER):
            print("Torrent is completed now")
            yn = print("Do you want to seed [y/n]?")
            if(yn[0] == 'y'):
                client.seeding = True
                continue
            else:
                torrent.set_status(TorrentStatus.STOPPED)
                print("Please wait till all the threads closes")
                continue

        percentage_complete = get_percentage_complete(
                                    torrent.get_completed_piece_count(),
                                    client.piece_count)
        print("Completed %5.2f%%\t\t" % percentage_complete, end='')

        total_hash_count = 40
        hash_count = int((percentage_complete * 25.0) / 100.0)        
        print("[" + "#" * hash_count + '-' * (total_hash_count - hash_count) 
                + "]\r", end='')
        time.sleep(0.5)

