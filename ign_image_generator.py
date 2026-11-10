from PIL import Image, ImageDraw, ImageFont
import io
import os
import discord

IGN_CIRCLE_CENTER = (156, 204)
IGN_CIRCLE_RADIUS = 110

def get_font(size: int, bold: bool = True):
    font_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/impact.ttf",
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
    try:
        avatar_bytes = await user.display_avatar.with_format("png").with_size(256).read()
        return Image.open(io.BytesIO(avatar_bytes))
    except Exception as e:
        print(f"Error fetching avatar for {user}: {e}")
        fallback = Image.new("RGBA", (256, 256), (30, 35, 45, 255))
        draw = ImageDraw.Draw(fallback)
        draw.ellipse((40, 40, 216, 216), fill=(100, 110, 130, 255))
        return fallback

def generate_ign_result_card(
    template_path: str,
    avatar_img: Image.Image,
    current_name: str,
    registered_name: str,
    level: str,
    reviewed_by: str,
    is_approved: bool
) -> io.BytesIO:
    base = Image.open(template_path).convert("RGBA")
    
    diameter = IGN_CIRCLE_RADIUS * 2
    cx, cy = IGN_CIRCLE_CENTER
    
    # 1. Overlay circular avatar
    circ_avatar, mask = create_circular_avatar(avatar_img, diameter)
    paste_pos = (cx - IGN_CIRCLE_RADIUS, cy - IGN_CIRCLE_RADIUS)
    base.paste(circ_avatar, paste_pos, mask)
    
    draw = ImageDraw.Draw(base)
    
    # Colors
    accent_color = (0, 255, 120, 255) if is_approved else (255, 50, 60, 255)
    white_color = (255, 255, 255, 255)
    shadow_color = (0, 0, 0, 230)
    
    # Helper to draw centered text with drop shadow
    def draw_centered_text(center_x, y, text, font, fill_color, max_width=None):
        active_font = font
        bbox = draw.textbbox((0, 0), text, font=active_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        if max_width and tw > max_width:
            new_size = max(12, int(active_font.size * (max_width / tw)))
            active_font = get_font(new_size, bold=True)
            bbox = draw.textbbox((0, 0), text, font=active_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
        pos_x = center_x - tw // 2
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, 2)]:
            draw.text((pos_x + ox, y + oy), text, font=active_font, fill=shadow_color)
        draw.text((pos_x, y), text, font=active_font, fill=fill_color)
        return tw, th

    # 2. CURRENT NAME (Applicant's Discord username)
    # Positioned below CURRENT NAME heading (around x=402, y=190)
    name_font = get_font(22, bold=True)
    draw_centered_text(402, 190, current_name, name_font, white_color, max_width=200)
    
    # 3. REGISTERED NAME (The registered in-game name, or "NONE" if declined)
    # Positioned below Registered Name heading (around x=778, y=190)
    display_reg_name = "NONE" if (not is_approved or not registered_name or registered_name.upper() == "NONE") else registered_name
    draw_centered_text(778, 190, display_reg_name, name_font, accent_color, max_width=200)
    
    # 4. LEVEL
    # Box spans (315, 272) to (555, 338). Icon is at (340, 290). Label 'LEVEL' is at (387, 293).
    # We place the level value prominently to the right of 'LEVEL' (around x=485, y=287)
    lvl_font = get_font(22, bold=True)
    lvl_str = str(level).strip()
    draw_centered_text(485, 287, lvl_str, lvl_font, accent_color, max_width=90)
    
    # 5. REVIEWED BY
    # Box spans (590, 272) to (840, 338). Label 'REVIEWED BY' is at (678, 293).
    # We place reviewer name directly inside the box at y=312
    rev_font = get_font(16, bold=True)
    rev_str = str(reviewed_by).strip()
    draw_centered_text(735, 312, rev_str, rev_font, accent_color, max_width=150)
    
    out_bytes = io.BytesIO()
    base.convert("RGB").save(out_bytes, format="PNG")
    out_bytes.seek(0)
    return out_bytes

if __name__ == "__main__":
    dummy = Image.new("RGBA", (300, 300), (20, 100, 220))
    d_draw = ImageDraw.Draw(dummy)
    d_draw.ellipse((50, 50, 250, 250), fill=(255, 220, 50))
    
    # Test approved
    out_app = generate_ign_result_card(
        'assets/ign_photo3_approved.jpg',
        dummy,
        current_name="Gulam_Scofield",
        registered_name="Manu_N12",
        level="42",
        reviewed_by="DC_Mod_John",
        is_approved=True
    )
    with open('assets/test_ign_approved_out.png', 'wb') as f:
        f.write(out_app.read())
        
    # Test declined
    out_dec = generate_ign_result_card(
        'assets/ign_photo4_declined.jpg',
        dummy,
        current_name="Gulam_Scofield",
        registered_name="Manu_N12",
        level="42",
        reviewed_by="DC_Mod_John",
        is_approved=False
    )
    with open('assets/test_ign_declined_out.png', 'wb') as f:
        f.write(out_dec.read())
        
    print("IGN Cards generated successfully!")
