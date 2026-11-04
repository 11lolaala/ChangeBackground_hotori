from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageFont, ImageFilter

session = new_session("silueta")

decrease_index = 0.5


SIZE = 1080  # сторона квадрата, можно менять


def make_square(img):
    side = min(img.width, img.height)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    return img.crop((left, top, left + side, top + side)).resize((SIZE, SIZE))


def put_photo(background, photo):
    photo.thumbnail((int(SIZE), int(SIZE)))
    photo = remove(photo, session=session).convert("RGBA")
    x = (background.width - photo.width) // 2
    y = (background.height - photo.height) // 2
    background.paste(photo, (x, y), photo)
    return background


def process_hotori_base(photo):
    background = make_square(Image.open('backk2.jpg'))
    background = background.filter(ImageFilter.GaussianBlur(1)).convert("RGBA")
    background = put_photo(background, photo)

    overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype("MedievalSharp-Regular.ttf", 300)

    text_w = draw.textlength("hotori", font=font)
    bbox = draw.textbbox((0, 0), "hotori", font=font)
    text_h = bbox[3] - bbox[1]
    x = (background.width - text_w) // 2
    y = (background.height - text_h) // 2
    draw.text((x, y), "hotori", font=font, fill=(200, 200, 200, 140))
    return Image.alpha_composite(background, overlay)


def process_white(photo):
    background = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
    return put_photo(background, photo)