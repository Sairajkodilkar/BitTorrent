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

'''

def display_status(client, torrent, peer):

    while(torrent.get_status() != TorrentStatus.STOPPED):
        print("Completed %5.2f%%\n" % get_percentage_complete(
                                    torrent.get_completed_piece_count(),
                                    client.piece_count), )

        print("----------------------------------------------------------------------------------------------------\n")
        print("Peer Type".ljust(20)
               + "Peer Address".ljust(30)
               + "Download_speed(KBPS)".ljust(20)
               + "Upload_speed(KBPS)".ljust(20)
               )
               

        total_download_speed = 0
        total_upload_speed = 0

        clearlen = 0
        for peer in torrent.seeders:
            download_speed = bps_to_kbps(peer.get_download_speed())
            upload_speed = bps_to_kbps(peer.get_upload_speed())
            print("Seeder".ljust(20), end='')
            print(str(peer.peer_address).ljust(30), end='')
            print(f'{download_speed:20.2f}', end='')
            print(f'{upload_speed:20.2f}')
            total_download_speed += download_speed
            total_upload_speed += upload_speed
            clearlen += 1

        for peer in torrent.unchoked_peers:
            download_speed = bps_to_kbps(peer.get_download_speed())
            upload_speed = bps_to_kbps(peer.get_upload_speed())
            print("Seeder".ljust(20), end='')
            print(str(peer.peer_address).ljust(30), end='')
            print(f'{download_speed:20.2f}', end='')
            print(f'{upload_speed:20.2f}')
            total_download_speed += download_speed
            total_upload_speed += upload_speed
            clearlen += 1

        for peer in torrent.peers:
            download_speed = bps_to_kbps(peer.get_download_speed())
            upload_speed = bps_to_kbps(peer.get_upload_speed())
            print("Seeder".ljust(20), end='')
            print(str(peer.peer_address).ljust(30), end='')
            print(f'{download_speed:20.2f}', end='')
            print(f'{upload_speed:20.2f}')
            total_download_speed += download_speed
            total_upload_speed += upload_speed
            clearlen += 1

        print("----------------------------------------------------------------------------------------------------\n")
        print("Total Download Speed".ljust(30)
                        + f"{total_download_speed:20.2f} KBPS")
        print("Total Upload Speed".ljust(30)
                        + f"{total_upload_speed:20.2f} KBPS")


        # print((goback[2:])
        # sys.exit()
        if(not client.seeding and torrent.get_status() == TorrentStatus.SEEDER):
            yn = input("The torrent is completed now do you want to seed?")
            if(yn[0] == 'y'):
                client.seeding = True
                continue
            else:
                torrent.set_status(TorrentStatus.STOPPED)
        

        for i in range(clearlen + 8):
            print("\033[A", end='')
        #print(("==============================================================================", clearlen,
                #len(torrent.seeders))
        time.sleep(0.5)

    return
'''

def display_status(client, torrent, peer):

    while(torrent.get_status() != TorrentStatus.STOPPED):
        percentage_complete = get_percentage_complete(
                                    torrent.get_completed_piece_count(),
                                    client.piece_count)
        print("Completed %5.2f%%\t\t" % percentage_complete, end='')
        total_hash_count = 40
        hash_count = int((percentage_complete * 25.0) / 100.0)        
        print("[" + "#" * hash_count + '-' * (total_hash_count - hash_count) 
                + "]\r", end='')
        time.sleep(0.5)

