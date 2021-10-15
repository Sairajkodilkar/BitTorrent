import requests
import urllib

'''
what should I provide request ?
    I should provide it url of torrent
    then dict of info_hash, peer_id, port, uploaded, downloaded, left and
    compact
'''

class THttpGetError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class THttpScrapeError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class THttp:

    def __init__(self, announce_url):

        self.announce_url = announce_url

    def announce(self, info_hash, peer_id, port,
                uploaded, downloaded, left, compact = "1",
                event = "started", **kwargs):

        '''
        kwargs = {no_peer_id, ip, num_want, key, announce_id}
        '''
        params = dict()
        params['info_hash'] = info_hash
        params['peer_id'] = peer_id
        params['port'] = port
        params['uploaded'] = uploaded
        params['downloaded'] = downloaded
        params['left'] = left
        #params['compact'] = compact
        #params['event'] = event
        #params.update(kwargs)

        http_response = requests.get(self.announce_url, params=params)
        if(http_response.status_code != requests.codes.ok):
            raise THttpGetError("Torrent Tracker says: {}"
                                    .format(http_response.content.decode()))
        return http_response.content

    def scrape(self, info_hash:list):

        if(self.announce_url.find('/announce') == -1):
            raise HTTPScrapeError("Tracker does not support scraping")
            
        scrape_url = self.announce_url.replace("/announce", "/scrape")
        params = dict()
        params['info_hash'] = info_hash

        print("sending http request")
        #TODO:change request.get and write your own 
        http_response = requests.get(scrape_url, params=params)
        if(http_response.status_code != requests.codes.ok):
            raise THttpGetError("Torrent Tracker says: {}"
                                    .format(http_response.content.decode()))

        return http_response.content


