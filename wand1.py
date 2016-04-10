
from wand.image import Image
# Converting first page into JPG
with Image(filename="/sample.pdf") as img:
	img.save(filename="/temp.jpg")
# Resizing this image
with Image(filename="/temp.jpg") as img:
	img.resize(200, 150)
	img.save(filename="/thumbnail_resize.jpg")

