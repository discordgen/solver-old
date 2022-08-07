from .solutions import sk_recognition, resnet, yolo
import base64
import time
import asyncio
import requests
import aiohttp
import re
import os
from .hcaptcha import Challenge

PROJECT_ROOT = os.path.dirname(os.path.abspath("__file__"))
DIR_MODEL = PROJECT_ROOT + "/model"
PATH_RAINBOW = DIR_MODEL + "/rainbow.yaml"
LABEL_ALIAS = {
            "airplane": "airplane",
            "motorbus": "bus",
            "bus": "bus",
            "truck": "truck",
            "motorcycle": "motorcycle",
            "boat": "boat",
            "bicycle": "bicycle",
            "train": "train",
            "vertical river": "vertical river",
            "airplane in the sky flying left": "airplane in the sky flying left",
            "Please select all airplanes in the sky that are flying to the right": "airplanes in the sky that are flying to the right",
            "car": "car",
            "elephant": "elephant",
            "bird": "bird",
            "dog": "dog"
}
BAD_CODE = {
    "а": "a",
    "е": "e",
    "e": "e",
    "i": "i",
    "і": "i",
    "ο": "o",
    "с": "c",
    "ԁ": "d",
    "ѕ": "s",
    "һ": "h"
}

pom_handler = resnet.PluggableONNXModels(PATH_RAINBOW)
LABEL_ALIAS.update(pom_handler.label_alias['en'])
print(pom_handler.label_alias['en'])
pluggable_onnx_models = pom_handler.overload(
    DIR_MODEL, path_rainbow=PATH_RAINBOW
)
yolo_model = yolo.YOLO(DIR_MODEL, "yolov6s")

def label_cleaning(raw_label: str) -> str:
    clean_label = raw_label
    for c in BAD_CODE:
        clean_label = clean_label.replace(c, BAD_CODE[c])
    return clean_label

def split_prompt_message(prompt_message: str) -> str:
    prompt_message = label_cleaning(prompt_message)
    labels_mirror = {
        "en": re.split(r"containing a", prompt_message)[-1][1:].strip().replace(".", "")
        if "containing" in prompt_message
        else prompt_message,
    }
    return labels_mirror["en"]

def switch_solution(label):
    """Optimizing solutions based on different challenge labels"""
    sk_solution = {
        "vertical river": sk_recognition.VerticalRiverRecognition,
        "airplane in the sky flying left": sk_recognition.LeftPlaneRecognition,
        "airplanes in the sky that are flying to the right": sk_recognition.RightPlaneRecognition,
    }

    label_alias = LABEL_ALIAS.get(label)

    # Select ResNet ONNX model
    if pluggable_onnx_models.get(label_alias):
        return pluggable_onnx_models[label_alias]
    # Select SK-Image method
    if sk_solution.get(label_alias):
        return sk_solution[label_alias](PATH_RAINBOW)
    # Select YOLO ONNX model
    return yolo_model

def solveAI(prompt, tile) -> bool:
    label = split_prompt_message(prompt)
    solution = switch_solution(label)
    solution.download_model()
    return solution.solution(img_stream=tile.get_image(raw=True), label=label)

def solveAIS(label, stream) -> bool:
    print("Here's a cool query: " + label)
    solution = switch_solution(label)
    solution.download_model()
    return solution.solution(img_stream=stream, label=label)


async def fetch(session, ch, tile):
    if solveAI(ch.question['en'], tile):
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


async def solve(**args):
    ch = Challenge(**args)
    async with aiohttp.ClientSession() as session:
        t1 = time.time()
        await fetch_all(session, ch)
        print("solve took " + str(time.time() - t1))
        t1 = time.time()
        token = ch.submit()
        print("submit took " + str(time.time() - t1))
        return token
