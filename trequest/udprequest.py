from packetization import *
import socket

class TrackerTimeoutError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

class UDPRequest:

    def __init__(self, tracer_address):

        self.tracker_address = tracer_address

        self.torrent_client_socket = socket.socket(socket.AF_INET, 
                                                    socket.SOCK_DGRAM)
        self.torrent_client_socket.setsockopt(socket.SOL_SOCKET,
                                                socket.SO_REUSEADDR, 1)

    def connect(self, transaction_id):

        connection_req_packet = paketize_connection_req(transaction_id)
        self.torrent_client_socket.sendto(connection_req_packet,
                                            self.tracker_address)

        timeout = 15
        count = 0
        while(1):
            if(count > 8):
                raise 
            self.torrent_client_socket.settimeout(timeout)
            try:
                print("waiting for server to respond...")
                connection_res_packet, address = (
                                    self.torrent_client_socket.recvfrom(1024))
            except socket.timeout:
                timeout *= 2
                count += 1
                continue
            break

        print(connection_res_packet)
        print(self.tracker_address, address)

        connection_response = unpaketize_request(connection_res_packet)

        print(connection_response)
        return connection_response

    def announce(self, connection_id, transaction_id, info_hash, peer_id,
            downloaded, left, uploaded, port, key, event=0, IP_address=0, num_want =
            -1):
        pass

    def scrap(self, connection_id, transaction_id, info_hash):
        pass
