#!/usr/bin/env python3
"""
Generate a bitmap font atlas for signs_fix mod
Creates a 16x6 grid of 96 ASCII characters (0x20 to 0x7E)
Each glyph is 6x10 pixels
"""

from PIL import Image, ImageDraw, ImageFont
import sys

# Configuration
GLYPH_WIDTH = 6
GLYPH_HEIGHT = 10
GRID_COLS = 16
GRID_ROWS = 6
FONT_SIZE = 8  # Small bitmap-style font

# Total image size
IMG_WIDTH = GLYPH_WIDTH * GRID_COLS
IMG_HEIGHT = GLYPH_HEIGHT * GRID_ROWS

def create_font_atlas():
    # Create transparent image
    img = Image.new('RGBA', (IMG_WIDTH, IMG_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a monospace font
    try:
        # Try different font options
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", FONT_SIZE)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", FONT_SIZE)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
    
    # Draw each character in the grid
    for i in range(96):
        char_code = 32 + i  # ASCII 0x20 to 0x7E
        char = chr(char_code)
        
        # Calculate grid position
        col = i % GRID_COLS
        row = i // GRID_COLS
        
        # Calculate pixel position
        x = col * GLYPH_WIDTH
        y = row * GLYPH_HEIGHT
        
        # Draw character (black text)
        # Center the character in its cell
        bbox = draw.textbbox((0, 0), char, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center horizontally and vertically
        char_x = x + (GLYPH_WIDTH - text_width) // 2
        char_y = y + (GLYPH_HEIGHT - text_height) // 2 - 1  # Slight adjustment
        
        draw.text((char_x, char_y), char, fill=(0, 0, 0, 255), font=font)
    
    return img

if __name__ == "__main__":
    print(f"Generating font atlas: {IMG_WIDTH}x{IMG_HEIGHT} pixels")
    print(f"Grid: {GRID_COLS}x{GRID_ROWS} = 96 glyphs")
    print(f"Glyph size: {GLYPH_WIDTH}x{GLYPH_HEIGHT} pixels")
    
    img = create_font_atlas()
    textures_dir = "devkorth_test_world/worldmods/signs_fix/textures"
    output_path = f"{textures_dir}/signs_fix_font.png"
    img.save(output_path)
    print(f"Saved atlas to: {output_path}")

    # Also export each glyph as an individual file to avoid [sheet] on clients
    # Files named: signs_fix_c<ascii>.png, e.g., signs_fix_c65.png for 'A'
    from PIL import Image
    for i in range(96):
        code = 32 + i
        col = i % GRID_COLS
        row = i // GRID_COLS
        x0 = col * GLYPH_WIDTH
        y0 = row * GLYPH_HEIGHT
        x1 = x0 + GLYPH_WIDTH
        y1 = y0 + GLYPH_HEIGHT
        crop = img.crop((x0, y0, x1, y1))
        glyph_path = f"{textures_dir}/signs_fix_c{code}.png"
        crop.save(glyph_path)
    print(f"Saved 96 glyph files to: {textures_dir}/signs_fix_c32..signs_fix_c126.png")