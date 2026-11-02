from rembg import remove
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def process(photo):
    background = Image.open('backk2.jpg')
    background = background.filter(ImageFilter.GaussianBlur(3))
    k = 0.7
    photo = photo.resize((int(photo.width * k), int(photo.height * k)))
    photo = remove(photo)
    x_cord_photo = (background.width - photo.width) // 2
    y_cord_photo = (background.height - photo.height) // 2
    background.paste(photo, (x_cord_photo, y_cord_photo), photo)

    background = background.convert("RGBA")
    overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = ImageFont.truetype("MedievalSharp-Regular.ttf",220)

    text_w = draw.textlength("hotori", font=font)
    bbox = draw.textbbox((0, 0), "hotori", font=font)
    text_h = bbox[3] - bbox[1]

    x_cord_text = (background.width - text_w) // 2
    y_cord_text = (background.height - text_h) // 2
    draw.text((x_cord_text,y_cord_text),"hotori",font=font,fill=(200,200,200,120))
    result = Image.alpha_composite(background, overlay)
    return result

