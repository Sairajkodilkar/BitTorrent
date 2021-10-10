import ssl
import socket
import requests
import urllib

'''
GET_REQUEST = ("GET /announce HTTP/1.1\r\n" +\
        "Host: torrent.ubuntu.com\r\n" +\
        "Info_Hash:64a980abe6e448226bb930ba061592e44c3781a1\r\n"+ "\r\n").encode()
        '''

'''
GET_REQUEST2 ="GET: /favicon.ico\r\n" +\
        "HOST: torrent.ubuntu.com\r\n" +\
        "info_hash: 64a980abe6e448226bb930ba061592e44c3781a1\r\n" +\
        "peer_id: 12345678901234567890\r\n" +\
        "port: 8082\r\n" +\
        "uploaded: 0\r\n" + "downloaded: 0\r\n" +\
        "left: 2820000000\r\n\r\n"
        '''


def client(host, port, geturl, cafile=None):
    purpose = ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose, cafile=cafile)

    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.bind(('', 8082))
    raw_sock.connect((host, port))
    print('Connected to host {!r} and port {}'.format(host, port))

    ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
    ssl_sock.sendall(geturl)
    i = 0
    while(i < 10):
        data = ssl_sock.recv(10000)
        print(data)
        i+=1


#client("torrent.ubuntu.com", 443)

Info_hash = '64a980abe6e448226bb930ba061592e44c3781a1'
a = bytes.fromhex(Info_hash)
encoded = urllib.parse.quote(a)
print(encoded)


def createurl(info_hash):
    pass


headers= {
        "info_hash":bytes.fromhex(Info_hash),
        "peer_id":"12345678901234567890",
        "port":"8080",
        "uploaded":"0",
        "downloaded":"0",
        "left":"2820000000"}

scraper = "https://torrent.ubuntu.com/scraper"

GET_REQUEST = ( "GET /announce?info_hash={}&peer_id=2345678911234567890&port=8080&uploaded=0&downloaded=0&left=2820000000&event=started HTTP/1.1\r\n".format(encoded) +\
                "Host: torrent.ubuntu.com\r\n\r\n").encode()
#client("torrent.ubuntu.com", 443, GET_REQUEST)
url = "https://torrent.ubuntu.com/announce"
r = requests.get(url, params=headers)
print(r.content)
'''
print(r.headers)
print(r.url)
print(r.status_code)
print(GET_REQUEST)
print(r.content)
'''
'''
print(r.content)
decoder = bdencoder.Bdecoder(r.content, "b")
x = decoder.decode()
peers = x[0][b'peers']
print(peers)
'''

'''
i = 0
while(i < len(peers)):
    ip = peers[i:i+4]
    port = peers[i+4:i+6]
    print(socket.inet_ntoa(ip), int.from_bytes(port, "big"))
    i += 6

'''


gets = "GET {}?info_hash={} HTTP/1.1\r\nHost:torrent.ubuntu.com\r\n\r\n".format(scraper, encoded)


