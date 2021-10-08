from packetization import *
import socket

class TrackerTimeoutError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

class UDPRequest:

    def __init__(self, tracker_address):

        self.tracker_address = tracker_address

        self.torrent_client_socket = socket.socket(socket.AF_INET, 
                                                    socket.SOCK_DGRAM)
        self.torrent_client_socket.setsockopt(socket.SOL_SOCKET,
                                                socket.SO_REUSEADDR, 1)

    def connect(self, transaction_id):

        connection_req_packet = paketize_connection_req(transaction_id)
        #TODO: take care of return value
        self.make_request(connection_req_packet)

        #TODO: check action number 
        connection_res_packet, address = self.get_response()
        connection_res = unpaketize_response(connection_res_packet)
        return connection_res

    def announce(connection_id, transaction_id, info_hash,
                peer_id, downloaded, left,
                uploaded, port, key,
                event=0, ip_address=0, num_want=-1):

        announce_req_packet = packetize_announce_req(
                                connection_id, transaction_id, info_hash, 
                                peer_id, downloaded, left,
                                uploaded, port, key,
                                event, ip_address, num_want)

        #TODO: take care of return value
        self.make_request(announce_req_packet)
        #TODO: check action number
        announce_res_packet = self.get_response()
        announce_res = unpaketize_response(announce_res_packet)
        return announce_res

    def scrape(self, connection_id, transaction_id, info_hash):

        scrape_req_packet = packetize_scrap_req(connection_id, 
                                            transaction_id,
                                            info_hash)

        #TODO: take care of return value
        self.make_request(scrape_req_packet)

        scrape_res_packet = self.get_response()
        #TODO: check action number
        scrape_res = unpaketize_response(scrape_req_packet)
        return scrape_res

    def make_request(self, req_packet):
        return self.torrent_client_socket.sendto(req_packet,
    
    def get_response(self):

        timeout = 15
        count = 0
        while(1):
            if(count > 8):
                raise 
            self.torrent_client_socket.settimeout(timeout)
            try:
                print("waiting for server to respond...")
                res_packet, address = (self.torrent_client_socket.recvfrom(1024))
            except socket.timeout:
                timeout *= 2
                count += 1
                continue
            break

        return  res_packet, address

