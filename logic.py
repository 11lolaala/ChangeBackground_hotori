from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageFont, ImageFilter

session = new_session("silueta")


def process(photo):
    background = Image.open('backk2.jpg')
    background = background.filter(ImageFilter.GaussianBlur(1))
    k = 0.7
    photo = photo.resize((int(photo.width * k), int(photo.height * k)))
    photo = remove(photo, session=session)
    photo = photo.convert("RGBA")
    x_cord_photo = (background.width - photo.width) // 2
    y_cord_photo = (background.height - photo.height) // 2
    background.paste(photo, (x_cord_photo, y_cord_photo), photo)

    background = background.convert("RGBA")
    overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = ImageFont.truetype("MedievalSharp-Regular.ttf", 300)

    text_w = draw.textlength("hotori", font=font)
    bbox = draw.textbbox((0, 0), "hotori", font=font)
    text_h = bbox[3] - bbox[1]

    x_cord_text = (background.width - text_w) // 2
    y_cord_text = (background.height - text_h) // 2
    draw.text((x_cord_text, y_cord_text), "hotori", font=font, fill=(200, 200, 200, 140))
    result = Image.alpha_composite(background, overlay)
    return result
