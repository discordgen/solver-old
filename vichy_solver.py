import hcaptcha
import base64
import time
import asyncio
import requests
import aiohttp

async def fetch(session, ch, tile):
    question = ch.question["en"].split()[-1]
    print(tile.image_url)
    print(question)
    link = "http://node01.proxies.gay:1337/check/" + base64.b64encode(question.encode('ascii')).decode() + "/" + base64.b64encode(tile.image_url.encode("ascii")).decode()
    async with session.get(link) as response:
        text = await response.text()
        print("Received response for question: "  + text)
        if text == "True":
          ch.answer(tile)

async def fetch_all(session, ch):
    tasks = []
    for tile in ch:
        task = asyncio.create_task(fetch(session, ch, tile))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results
    
async def main():    
    ch = hcaptcha.Challenge(
    site_key="c4305294-4b00-41e7-a50b-bed3c3aee5be",
    site_url="https://testzeber.pl/hcaptcha.php/",
    #http_proxy="user:pass@127.0.0.1:8888",
    #ssl_context=__import__("ssl")._create_unverified_context(),
    timeout=5
    )
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, ch)
        print(htmls)
    try:
      token = ch.submit()
      print(token)
    except hcaptcha.ChallengeError as err:
      print(err)
        
if __name__ == '__main__':
    asyncio.run(main())