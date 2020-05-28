
import random
import asyncio
import sys

import aiohttp
from aiohttp import ClientConnectorError

# to run:
# pip install aiohttp requests


def main():

    request_urls = []

    loop = asyncio.get_event_loop()

    # generate and append 5 random urls
    for i in range(5):
        request_urls.append(get_response("https://postman-echo.com/delay/" + str(random.randint(1, 5))))

    request_urls.append(get_response("http://www.dmoz.org/eee"))

    loop.run_until_complete(asyncio.gather(*request_urls))


async def get_response(url):
    print("REQUEST TO: " + url)

    async with aiohttp.ClientSession() as session:

        try:
            async with session.get(url) as response:

                if response.status == 200:
                    print("RESPONSE FROM %s, status code: %s" % (url, response.status))
                else:
                    print("RESPONSE FROM %s, status code: %s" % (url, response.status))

        except ClientConnectorError:
            print(url + " did not respond due to network error")

# running

main()
