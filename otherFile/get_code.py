import asyncio
import json
import os

from pyquery import PyQuery as pq

import aiohttp

# from lxml import etree

class AioInterface:
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    }

    def __init__(self, downpath=''):
        self.downpath = downpath


    async def get(self, url, **kwargs):
        session = aiohttp.ClientSession(headers=self.head)
        if kwargs:
            response = await session.post(url, **kwargs)
        else:
            response = await session.get(url)
        if kwargs.get("json"):
            result = await response.json()
        else:
            result = await response.text
        await asyncio.sleep(0.1)
        res = result["data"]
        session.close()
        return res

    async def request(self, url, **kwargs):
        # print('Waiting for', url)
        result = await self.get(url, **kwargs)
        # result = await get(url, data)
        return result


class GetCode(AioInterface):
    url = "http://code.mcdvisa.com/save.php?action=getcode&i=1&w={}"
    code = [[f"{i*10-9+j:0>4}" for j in range(10)if i*10-9+j < 10000] for i in range(1, 1001)]
    downpath = os.path.dirname(__file__)
    
    def get_code_data(self):
        for co in self.code:
            tasks = [asyncio.ensure_future(self.request(self.url.format(data))) for data in co]
            self.loop = asyncio.get_event_loop()
            result = self.loop.run_until_complete(asyncio.wait(tasks))
            result = self.get_result(result[0])
            break

    def get_result(self, result):
        return [result.pop().result() for i in range(len(result))]

        
    def __del__(self):
        if hasattr(self, "loop"):
            self.loop.close()

def main():
    downpath = os.path.dirname(__file__)
    g = GetCode(downpath)
    g.get_code_data()

if __name__ == '__main__':
    main()