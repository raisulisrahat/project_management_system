import random
from django import template
from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

register = template.Library()

@register.filter(name='letter_avatar')
def letter_avatar(user, size=100):
    # Generate random RGB color for background
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Create an image with Pillow
    if user.first_name:
        letter = user.first_name[0].upper()  # Get the first letter of the first name
    else:
        letter = 'U'  # Default letter if no first name is set

    # Create an empty image with a random background color
    image = Image.new('RGB', (size, size), color=random_color)

    # Get a drawing context to add text
    draw = ImageDraw.Draw(image)

    # Set the path to the font file (assuming it's in the static directory)
    font_path = settings.BASE_DIR / 'static' / 'fonts' / 'Roboto-Regular.ttf'

    # Try to use the downloaded font, fallback to default if not found
    try:
        font = ImageFont.truetype(str(font_path), size=int(size / 2))
    except IOError:
        font = ImageFont.load_default()

    # Get text width and height to center the letter
    text_width, text_height = draw.textsize(letter, font=font)
    position = ((size - text_width) / 2, (size - text_height) / 2)

    # Draw the letter
    draw.text(position, letter, (255, 255, 255), font=font)

    # Save the image to a BytesIO object
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)

    # Convert to InMemoryUploadedFile to work with Django's ImageField
    avatar = InMemoryUploadedFile(image_io, None, 'avatar.png', 'image/png', image_io.getbuffer().nbytes, None)

    return avatar
