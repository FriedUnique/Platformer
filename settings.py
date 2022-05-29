import os
from PIL import Image

colorToInt = {
    (255, 255, 255): 0,
    (0, 0, 0): 1,
    (255, 0, 0): 2,
    (205, 0, 255): 3,
    (0, 255, 0): 4,
    (255, 255, 0): 5
}

maps = []

def loadMaps():
    global maps
    for file in os.listdir("levels/"):
        if file.endswith(".png"):
            img = Image.open(os.path.join("levels", file))
            w, h = img.size
            maps.append(getPixels(img, w, h))

def getPixels(img, w, h):
    pixels = []
    for y in range(h):
        p = []
        for x in range(w):
            pixel = img.getpixel((x,y))
            try:
                p.append(colorToInt[pixel])
            except KeyError:
                p.append(0)

        pixels.append(p)
    return pixels

loadMaps()



BLOCKSIZE = 64
WIDTH = 960 # 15 blocks on screen in x direction
HEIGHT = len(maps[0])*BLOCKSIZE
ORIGINAL_SPEED = 10