#this code will contain all necessary functions to take a bmp (or really any image) and convert it into 2d Gcode

#How the process will work:
# 1) convert image to black and white
# 2)use thresholding to outine features
# 3) Trace image using Potrace --> gives list of paths

def Img_to_Gcode(OriginalImageAddress):


