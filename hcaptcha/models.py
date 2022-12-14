from PIL import Image
import time
from io import BytesIO

class Tile:
    id: str
    image_url: str
    index: int
    challenge: "Challenge"

    def __init__(self, id, image_url, index=None, challenge=None):
        self.id = id
        self.image_url = image_url
        self.index = index
        self.challenge = challenge
    
    def __repr__(self):
        return self.image_url

    def get_image(self, raw=False):
        t1 = time.time()
        data = self.challenge._get_tile_image(self.image_url)
        print("image download took " + str(time.time() - t1))
        if raw: return data
        image = Image.open(BytesIO(data))
        return image