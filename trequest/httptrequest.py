import requests

'''
what should I provide request ?
    I should provide it url of torrent
    then dict of info_hash, peer_id, port, uploaded, downloaded, left and
    compact
'''

class HttpGetError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def httptget(url, params):
    r = requests.get(url, params=params)
    if(r.status_code != requests.codes.ok):
        raise HttpGetError("Torrent Tracker says: {}".format(r.content.decode()))
    return r.content

