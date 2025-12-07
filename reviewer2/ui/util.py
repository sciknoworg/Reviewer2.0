from PIL import Image, ImageDraw
import base64
import io

def make_circle(image_path):
    # Ensure image is square
    image = Image.open(image_path)
    size = min(image.size)
    image = image.resize((size, size))
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new('RGBA', (size, size))
    result.paste(image, (0, 0), mask=mask)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return img_base64