from solutions import sk_recognition, resnet, yolo
import base64
import time
import asyncio
import requests
import aiohttp
import re
import os
import hcaptcha

PROJECT_ROOT = os.path.dirname(os.path.abspath("__file__"))
DIR_MODEL = PROJECT_ROOT + "/model"
PATH_RAINBOW = DIR_MODEL + "/rainbow.yaml"
LABEL_ALIAS = {
    "en": {
        "car": "car",
        "seaplane": "seaplane",
        "ѕeaplane": "seaplane",
        "airplane": "airplane",
        "аirplane": "airplane",
        "motorbus": "bus",
        "mοtorbus": "bus",
        "bus": "bus",
        "truck": "truck",
        "truсk": "truck",
        "motorcycle": "motorcycle",
        "mοtorcycle": "motorcycle",
        "boat": "boat",
        "bicycle": "bicycle",
        "train": "train",
        "trаin": "train",
        "vertical river": "vertical river",
        "airplane in the sky flying left": "airplane in the sky flying left",
        "Please select all airplanes in the sky that are flying to the rіght": "airplanes in the sky that are flying to the right",
        "Please select all airplanes in the sky that are flying to the right": "airplanes in the sky that are flying to the right",
        "Please select all the elephants drawn with lеaves": "elephants drawn with leaves",
        "Please select all the elephants drawn with leaves": "elephants drawn with leaves",
    },
}


def split_prompt_message(prompt_message: str) -> str:
    labels_mirror = {
        "en": re.split(r"containing a", prompt_message)[-1][1:].strip()
        if "containing" in prompt_message
        else prompt_message,
    }
    return labels_mirror["en"]


def switch_solution(label, onnx_prefix="yolov5n6"):
    label = LABEL_ALIAS.get(label)
    if label in ["seaplane"]:
        return resnet.ResNetSeaplane(DIR_MODEL)
    if label in ["elephants drawn with leaves"]:
        return resnet.ElephantsDrawnWithLeaves(DIR_MODEL, path_rainbow=PATH_RAINBOW)
    if label in ["vertical river"]:
        return sk_recognition.VerticalRiverRecognition(path_rainbow=PATH_RAINBOW)
    if label in ["airplane in the sky flying left"]:
        return sk_recognition.LeftPlaneRecognition(path_rainbow=PATH_RAINBOW)
    if label in ["airplanes in the sky that are flying to the right"]:
        return sk_recognition.RightPlaneRecognition(path_rainbow=PATH_RAINBOW)
    if label in ["horses drawn with flowers"]:
        return resnet.HorsesDrawnWithFlowers(DIR_MODEL, path_rainbow=PATH_RAINBOW)
    return yolo.YOLOWithAugmentation(label, DIR_MODEL, onnx_prefix, path_rainbow=PATH_RAINBOW)


def solve(prompt, tile) -> bool:
    label = split_prompt_message(prompt)
    solution = switch_solution(label)
    solution.download_model()
    return solution.solution(img_stream=tile.get_image(raw=True), label=label)


async def fetch(session, ch, tile):
    if solve(ch.question['en'], tile):
        print("Solved tile: True")
        ch.answer(tile)
    else:
        print("Solved tile: False")


async def fetch_all(session, ch):
    tasks = []
    for tile in ch:
        task = asyncio.create_task(fetch(session, ch, tile))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def main():
    ch = hcaptcha.Challenge(
        site_key="c4305294-4b00-41e7-a50b-bed3c3aee5be",
        site_url="https://testzeber.pl/hcaptcha.php/",
        # http_proxy="user:pass@127.0.0.1:8888",
        # ssl_context=__import__("ssl")._create_unverified_context(),
        timeout=5
    )
    async with aiohttp.ClientSession() as session:
        t1 = time.time()
        await fetch_all(session, ch)
        print("solve took " + str(time.time() - t1))
        try:
            t1 = time.time()
            token = ch.submit()
            print("submit took " + str(time.time() - t1))
            resp = requests.get('https://hcaptcha.com/siteverify', data={
                'secret': '0x58398062e6395b25bbA0957CA88BE5CFBC2BC878',
                'response': token
            })
            print(resp.text)
        except hcaptcha.ChallengeError as err:
            print(err)

if __name__ == '__main__':
    asyncio.run(main())
