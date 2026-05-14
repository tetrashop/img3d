from PIL import Image, ImageDraw
import os

os.makedirs('static', exist_ok=True)

# آیکون 192x192
img192 = Image.new('RGB', (192, 192), color='#007bff')
draw192 = ImageDraw.Draw(img192)
draw192.rectangle([30, 60, 162, 132], fill='white')
draw192.text((45, 80), "Img3D", fill='#007bff')
img192.save('static/icon-192.png')

# آیکون 512x512
img512 = Image.new('RGB', (512, 512), color='#007bff')
draw512 = ImageDraw.Draw(img512)
draw512.rectangle([80, 160, 432, 352], fill='white')
draw512.text((120, 210), "Img3D", fill='#007bff')
img512.save('static/icon-512.png')

print("Icons generated successfully!")
