import requests

HTTP_ANNOUNCE_RESPONSE_NAMES = [
    "seeders",
    "leechers",
    "interval",
    "peers"
]


class HTTPGetError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HTTPScrapeError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HTTPRequest:

    def __init__(self, announce_url):

        self.announce_url = announce_url

    def announce(self, info_hash, peer_id, downloaded,
                 left, uploaded, port, compact="1",
                 event="started", **kwargs):
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
        params['compact'] = compact
        params['event'] = event
        params.update(kwargs)

        http_response = requests.get(self.announce_url, params=params)
        if(http_response.status_code != requests.codes.ok):
            raise HTTPGetError(
                    "Torrent Tracker says: {}"
                    .format(http_response.content.decode()))
        return http_response.content

    def scrape(self, info_hash: list):

        if(self.announce_url.find('/announce') == -1):
            raise HTTPScrapeError("Tracker does not support scraping")

        scrape_url = self.announce_url.replace("/announce", "/scrape")
        params = dict()
        params['info_hash'] = info_hash

        http_response = requests.get(scrape_url, params=params)
        if(http_response.status_code != requests.codes.ok):
            raise HTTPGetError(
                    "Torrent Tracker says: {}"
                    .format(http_response.content.decode()))
        return http_response.content
