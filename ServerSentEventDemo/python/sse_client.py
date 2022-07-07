import json
import pprint
import sys
import sseclient_chunk
import requests
import logging
import http.client
import config


http.client.HTTPConnection.debuglevel = 1


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class ServerSentEventsClient(object):

    def __init__(self, path, query_string, last_event_id):
        self.token = ''
        self.path = path
        self.query_string = query_string
        self.last_event_id = last_event_id
        self.__login()

    def __with_request(self, url, headers):
        s = requests.session()
        return s.get(url, stream=True, headers=headers, verify=True)
    
    def __login(self):
        req_body = {'vendor_id': config.VENDOR_ID,
                    'vendor_member_id': config.MEMBER_ID}
        response = requests.post(f'{config.HOST}/login', json=req_body, verify=True)
        self.token = response.json()['access_token']

    def connect(self):
        url = f"{config.HOST}/sports/stream/v1/{self.path}{'' if self.query_string is None else '?'}{self.query_string}"
        headers = {'Accept': 'text/event-stream',
                   'Accept-Encoding': 'gzip',
                   'Authorization': f'Bearer {self.token}',
                   'Last-Event-ID': self.last_event_id} 
        response = self.__with_request(url, headers)
        client = sseclient_chunk.SSEClient(response)
        for event in client.events():
            json_data = json.loads(event.data)
            payload = json_data['payload']

            # events = payload['events']
            markets = payload['markets']
            # sports = payload['sports']
            # leagues = payload['leagues']
            # outrights = payload['outrights']

            status = json_data['status']

            # sports_payload = {
            #     'sport_add': [sport_add['sportType'] for sport_add in sports['add']],
            #     'sport_change': [sport_change['sportType'] for sport_change in sports['change']],
            #     'sport_remove': [sport_remove for sport_remove in sports['remove']],
            # }
            # leagues_payload = {
            #       'league_add': [league_add['leagueId'] for league_add in leagues['add']],
            #       'league_change': [league_change['leagueId'] for league_change in leagues['change']],
            #       'league_remove': [{league_remove['leagueId'], league_remove['isParlay']} for league_remove in leagues['remove']],
            #   }
            # events_payload = {
            #     'event_add': [event_add['eventId'] for event_add in events['add']],
            #     'event_change': [event_change['eventId'] for event_change in events['change']],
            #     'event_remove': [event_remove for event_remove in events['remove']],
            # }
            markets_payload = {
                'market_add': [{market_add['marketId'], market_add['eventId']} for market_add in markets['add']],
                'market_change': [market_change['marketId'] for market_change in markets['change']],
                'market_remove': [market_remove for market_remove in markets['remove']],
            }
            # outrights_payload = {
            #     'outright_add': [outright_add['leagueId'] for outright_add in outrights['add']],
            #     'outright_change': [outright_change['leagueId'] for outright_change in outrights['change']],
            #     'outright_remove': [outright_remove for outright_remove in outrights['remove']],
            # }

            pprint.pprint(status)
            pprint.pprint(event.id)
            # pprint.pprint(events_payload)
            pprint.pprint(markets_payload)
            # pprint.pprint(sports_payload)
            # pprint.pprint(leagues_payload)
            # pprint.pprint(outrights_payload)


if __name__ == '__main__':

    last_event_id = '' if len(sys.argv) == 3 else sys.argv[3]
    client = ServerSentEventsClient(sys.argv[1], sys.argv[2], last_event_id)
    client.connect()
