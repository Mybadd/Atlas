import os
import io
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


STYLE_CONFIGS = {
    "technical": {
        "bg_color": (255, 255, 255),
        "line_enhance": 1.5,
        "sharpen": True,
        "border": True,
        "border_color": (30, 30, 30),
        "title_bg": (20, 40, 80),
        "title_fg": (255, 255, 255),
    },
    "blueprint": {
        "bg_color": (10, 40, 90),
        "line_enhance": 1.8,
        "sharpen": True,
        "border": True,
        "border_color": (100, 160, 255),
        "title_bg": (5, 20, 50),
        "title_fg": (100, 160, 255),
        "invert": True,  # invert lines to white-on-blue
    },
    "shaded": {
        "bg_color": (245, 245, 240),
        "line_enhance": 1.2,
        "sharpen": False,
        "border": True,
        "border_color": (80, 80, 80),
        "title_bg": (60, 60, 60),
        "title_fg": (240, 240, 240),
    },
}


def svg_to_image(svg_path: str, width: int = 1200) -> Image.Image:
    """Convert SVG file to a PIL Image via svglib."""
    drawing = svg2rlg(svg_path)
    
    # Scale up vector drawing to target width for crisp rasterization
    if drawing.width > 0:
        scale_factor = width / drawing.width
        # For reportlab graphics, we scale the transform
        drawing.scale(scale_factor, scale_factor)
        drawing.width *= scale_factor
        drawing.height *= scale_factor

    png_bytes = io.BytesIO()
    renderPM.drawToFile(drawing, png_bytes, fmt="PNG")
    png_bytes.seek(0)
    
    img = Image.open(png_bytes).convert("RGBA")
    return img


def apply_style(img: Image.Image, style: str = "technical") -> Image.Image:
    """Apply visual style to the image."""
    cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS["technical"])

    # Create white background canvas
    bg_color = cfg["bg_color"]
    bg_rgba = (bg_color[0], bg_color[1], bg_color[2], 255)
    background = Image.new("RGBA", img.size, bg_rgba)

    # For blueprint: invert the drawing lines
    if cfg.get("invert"):
        r, g, b, a = img.split()
        inv = Image.eval(r, lambda x: 255 - x)
        img = Image.merge("RGBA", (inv, inv, inv, a))
        # Tint lines to blueprint color
        tint = Image.new("RGBA", img.size, (100, 160, 255, 255))
        img = Image.blend(img, tint, alpha=0.35)

    # Composite drawing on background
    background.paste(img, mask=img.split()[3])
    result = background.convert("RGB")

    # Enhance contrast / sharpness
    enhancer = ImageEnhance.Contrast(result)
    result = enhancer.enhance(cfg["line_enhance"])

    if cfg.get("sharpen"):
        result = result.filter(ImageFilter.SHARPEN)

    return result


def add_title_block(
    img: Image.Image,
    title: str,
    view: str,
    style: str = "technical",
    callout: str = "",
) -> Image.Image:
    """Add a title block banner at the bottom of the image."""
    cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS["technical"])
    bar_height = 60
    new_h = img.height + bar_height
    canvas = Image.new("RGB", (img.width, new_h), cfg["bg_color"])
    canvas.paste(img, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Draw title bar background
    draw.rectangle([(0, img.height), (img.width, new_h)], fill=cfg["title_bg"])

    # Try to use a nice font, fall back to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    fg = cfg["title_fg"]
    view_label = view.upper()
    draw.text((16, img.height + 10), title, fill=fg, font=font_large)
    draw.text((16, img.height + 36), f"View: {view_label}  |  {callout}", fill=fg, font=font_small)

    # Add border lines
    if cfg.get("border"):
        bc = cfg["border_color"]
        draw.rectangle([(2, 2), (img.width - 3, img.height - 3)], outline=bc, width=3)

    return canvas


def add_callout_bubble(
    img: Image.Image,
    text: str,
    position: tuple = (100, 100),
    color: tuple = (220, 60, 60),
) -> Image.Image:
    """Add a numbered callout bubble at the specified position."""
    draw = ImageDraw.Draw(img)
    x, y = position
    r = 18
    draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=color, outline=(255, 255, 255), width=2)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2), text, fill=(255, 255, 255), font=font)
    return img


def save_image(
    img: Image.Image,
    output_path: str,
    fmt: str = "png",
    quality: int = 95,
) -> str:
    """Save a PIL image to PNG or JPEG."""
    fmt = fmt.lower()
    if fmt in ("jpg", "jpeg"):
        img = img.convert("RGB")
        img.save(output_path, format="JPEG", quality=quality)
    else:
        img.save(output_path, format="PNG")
    return output_path
