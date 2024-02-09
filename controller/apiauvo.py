import asyncio
import sys
import requests
import aiohttp
import json

import setup
from common.logger import LOGGER

rootLogger = LOGGER.rootLogger
class APIAUVO:
    uri: str = None
    apikey: str = None
    token: str = None
    headers: dict = None

    def __init__(self):
        self.uri = setup.auvo_api_url
        self.apikey = setup.auvo_api_key
        self.token = setup.auvo_api_token
        try:
            headers = {'content-type': 'application/json'}
            params = {'apiKey': self.apikey, 'apiToken': self.token}
            rootLogger.debug('Iniciando aquisição do token')
            r = requests.get(url=self.uri + '/login', params=params, headers=headers)
            rootLogger.debug(r)
            if r.status_code == 200:
                data = json.loads(r.content)
                if data:
                    self.headers = {'Authorization': f"Bearer {data['result']['accessToken']}",
                                    'content-type': 'application/json'}
        except Exception as e:
            rootLogger.error(e)

    async def consulttasks(self, endDate, page):
        ParamFilterDict = {'startDate': '2000-01-01T00:00:00', 'endDate': endDate}
        ParamFilterJson = json.dumps(ParamFilterDict)
        params = {'ParamFilter': ParamFilterJson,
                  'Page': str(page), 'PageSize': '100', 'Order': 'asc'}
        rootLogger.debug(f'Starting Session: headers: {self.headers}')
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for i in range(5):
                rootLogger.debug(f'GET START params = {params}')
                async with session.get(url=self.uri + '/Tasks', params=params) as r:
                    rootLogger.debug(f"Page {page} - Status: {r.status}")
                    if r.status == 200:
                        data = await r.json()
                        return data
                await asyncio.sleep(2)
            rootLogger.error(f'Erro page {page} - {r}')
            return None

    def consultusers(self):
        rootLogger.debug('Iniciando aquisição de users')
        params = {'page': 1, 'pageSize': 100, 'order': 'asc'}
        try:
            for i in range(5):
                r = requests.get(url=self.uri + '/users', params=params, headers=self.headers)
                rootLogger.debug(r)
                if r.status_code == 200:
                    return json.loads(r.content)
            rootLogger.error('Não foi possivel consultar os usuários')
            return None
        except Exception as e:
            rootLogger.error(e)
            return None