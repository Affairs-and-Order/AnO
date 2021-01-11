# Resizes images

# Before
# Test image size - 4.57 mb
# Test image dimensions - 2520 x 1680

# After
# Test image size - 2.90 mb
# Test image dimensions - 1920 x 1280

from PIL import Image
from resizeimage import resizeimage
import os

def resize(filename):
    fd_img = open(filename, 'rb')
    img = Image.open(fd_img)
    img = resizeimage.resize_width(img, 1920)
    img.save(filename, img.format)
    fd_img.close()

# Changes folder to the images folder
cwd = os.getcwd()
cwd = cwd.replace("\\scripts", "")
os.chdir(cwd + "\\static\\images")
new_cwd = os.getcwd()
images = os.listdir()

for image in images:
    try:
        resize(image)
        print(f"Resized image: {image}")
    except:
        print(f"Failed to resize image: {image}")