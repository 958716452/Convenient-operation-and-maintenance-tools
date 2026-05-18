from PIL import Image

img = Image.open('icon.png')
img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
print('Icon converted successfully!')