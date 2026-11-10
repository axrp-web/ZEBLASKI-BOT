from PIL import Image, ImageDraw, ImageFont
import io
import os
import aiohttp
import discord

# Template coordinates:
# Photo 3 & 4 resolution: 1024 x 341 (or 342)
# Circle center: x=147, y=150
# Circle radius: ~87 px
CIRCLE_CENTER = (147, 150)
CIRCLE_RADIUS = 87

def get_font(size: int, bold: bool = True):
    font_candidates = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf"
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_circular_avatar(avatar_img: Image.Image, diameter: int):
    """Resize avatar and clip it into an antialiased circular image with RGBA."""
    scale = 3
    big_size = diameter * scale
    
    avatar_resized = avatar_img.convert("RGBA").resize((big_size, big_size), Image.Resampling.LANCZOS)
    
    mask = Image.new("L", (big_size, big_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, big_size, big_size), fill=255)
    
    mask = mask.resize((diameter, diameter), Image.Resampling.LANCZOS)
    avatar_final = avatar_resized.resize((diameter, diameter), Image.Resampling.LANCZOS)
    
    output = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    output.paste(avatar_final, (0, 0), mask)
    return output, mask

async def fetch_user_avatar(user: discord.User | discord.Member) -> Image.Image:
    """Fetch user avatar and return as PIL Image, with fallback to default avatar."""
    try:
        avatar_bytes = await user.display_avatar.with_format("png").with_size(256).read()
        return Image.open(io.BytesIO(avatar_bytes))
    except Exception as e:
        print(f"Error fetching avatar for {user}: {e}")
        # Generate clean fallback avatar
        fallback = Image.new("RGBA", (256, 256), (30, 35, 45, 255))
        draw = ImageDraw.Draw(fallback)
        draw.ellipse((40, 40, 216, 216), fill=(100, 110, 130, 255))
        return fallback

def generate_result_card(template_path: str, avatar_img: Image.Image, username: str, is_approved: bool) -> io.BytesIO:
    """
    Overlays applicant avatar into the circular frame and draws applicant username.
    Returns BytesIO object containing PNG image.
    """
    base = Image.open(template_path).convert("RGBA")
    
    diameter = CIRCLE_RADIUS * 2
    cx, cy = CIRCLE_CENTER
    
    # 1. Overlay circular avatar
    circ_avatar, mask = create_circular_avatar(avatar_img, diameter)
    paste_pos = (cx - CIRCLE_RADIUS, cy - CIRCLE_RADIUS)
    base.paste(circ_avatar, paste_pos, mask)
    
    # 2. Draw applicant's username
    glow_color = (0, 255, 100, 255) if is_approved else (255, 40, 50, 255)
    
    draw = ImageDraw.Draw(base)
    
    # Format username display
    # Clean up name if too long
    clean_username = username.strip()
    user_text = f"APPLICANT: {clean_username}"
    
    font_size = 28
    font = get_font(font_size, bold=True)
    
    # Measure text
    bbox = draw.textbbox((0, 0), user_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Adjust font size if text is too wide
    max_tw = 400
    if tw > max_tw:
        font_size = max(16, int(font_size * (max_tw / tw)))
        font = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), user_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
    # Place in center under ZEBLASKI logo
    box_x = 535 - tw // 2
    box_y = 278
    
    pad_x = 18
    pad_y = 6
    pill_box = (box_x - pad_x, box_y - pad_y, box_x + tw + pad_x, box_y + th + pad_y)
    
    pill_overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pill_draw = ImageDraw.Draw(pill_overlay)
    pill_draw.rounded_rectangle(pill_box, radius=12, fill=(10, 10, 15, 215), outline=glow_color, width=2)
    
    base = Image.alpha_composite(base, pill_overlay)
    draw = ImageDraw.Draw(base)
    
    for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, 2)]:
        draw.text((box_x + ox, box_y + oy), user_text, font=font, fill=(0, 0, 0, 240))
        
    draw.text((box_x, box_y), user_text, font=font, fill=(255, 255, 255, 255))
    
    # Also draw @username under avatar ring for clear identification
    avatar_tag = f"@{clean_username}"
    small_font = get_font(18, bold=True)
    s_bbox = draw.textbbox((0, 0), avatar_tag, font=small_font)
    s_tw = s_bbox[2] - s_bbox[0]
    s_th = s_bbox[3] - s_bbox[1]
    
    s_x = cx - s_tw // 2
    s_y = 252
    
    s_pill_box = (s_x - 10, s_y - 3, s_x + s_tw + 10, s_y + s_th + 3)
    s_pill_overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    s_pill_draw = ImageDraw.Draw(s_pill_overlay)
    s_pill_draw.rounded_rectangle(s_pill_box, radius=8, fill=(10, 10, 15, 210), outline=glow_color, width=1)
    base = Image.alpha_composite(base, s_pill_overlay)
    draw = ImageDraw.Draw(base)
    
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.text((s_x + ox, s_y + oy), avatar_tag, font=small_font, fill=(0, 0, 0, 240))
    draw.text((s_x, s_y), avatar_tag, font=small_font, fill=(255, 255, 255, 255))

    out_bytes = io.BytesIO()
    base.convert("RGB").save(out_bytes, format="PNG")
    out_bytes.seek(0)
    return out_bytes
