#this code will contain all necessary functions to take a bmp (or really any image) and convert it into 2d Gcode

#How the process will work:
# 1) convert image to black and white
# 2)use thresholding to outine features
# 3) Trace image using Potrace --> gives list of paths

from PIL import Image
import numpy as np
import potrace

def Img_to_Gcode(OriginalImageAddress):

    img = Image.open(OriginalImageAddress)

    ary = np.array(img)

    # Split the three channels
    r, g, b = np.split(ary, 3, axis=2)
    r = r.reshape(-1)
    g = r.reshape(-1)
    b = r.reshape(-1)

    # Standard RGB to grayscale
    bitmap = list(map(lambda x: 0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2],
                      zip(r, g, b)))
    bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
    bitmap = np.dot((bitmap > 128).astype(float), 255)
    im = Image.fromarray(bitmap.astype(np.uint8))

    bmp = potrace.Bitmap(im)  # convert image array  into Pypotrace bitmap object

    path = bmp.trace()

Img_to_Gcode("Example Image.bmp")
