import cv2
import numpy as np
import time
from datetime import datetime
import imghdr

#template follow Homography
h = []
h0 = np.array([[8.91056275e-01, -8.86495948e-01, 1.18488350e+03],
        [8.86340685e-01, 9.40315188e-01, -5.88656909e+02],
        [-1.43646066e-05, 2.46904615e-05, 1.00000000e+00]])
h1 = np.array([[1.12316723e+00, -5.35059095e-01,  6.06803417e+02],
        [5.46968002e-01, 1.16352348e+00, -5.55583720e+02],
        [-4.03875369e-06,  2.28706266e-05,  1.00000000e+00]])
h2 = np.array([[1.17622835e+00, 5.07583951e-01, -6.95821421e+02],
        [-4.66610020e-01, 1.17209389e+00, 3.11141722e+02],
        [1.91036058e-05, 1.10270348e-05, 1.00000000e+00]])
h3 = np.array([[1.10457236e+00, 8.59425880e-01, -1.06498834e+03],
        [-7.96789412e-01, 1.09717454e+00, 7.64337278e+02],
        [2.94763276e-05, 1.96107050e-05, 1.00000000e+00]])

h.append(h0)
h.append(h1)
h.append(h2)
h.append(h3)

#Match templates
def chooseInput(number, path):
    d = datetime.now()
    unixtime = time.mktime(d.timetuple())
    img_name = str(unixtime).replace(".0", "")

    imghdr_ = imghdr.what('/home/totoro0098/Downloads/demo_03.jpg')
    img = cv2.imread(path)
    height, width, channels = img.shape
    im1Reg = cv2.warpPerspective(img, h[number], (width, height))
    cv2.imwrite('/home/totoro0098/Documents/OCR_Invoice/OCR_Invocie/demoTemplate/data/{}.jpg'.format(img_name), im1Reg)
    return './demoTemplate/data/{}.jpg'.format(unixtime)



