import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_splash_screen():
    """Create a professional splash screen for the application"""
    
    # Create a new image with a gradient background
    width = 600
    height = 400
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create gradient background
    for y in range(height):
        r = int(36 + (y / height) * 20)  # Dark blue gradient
        g = int(41 + (y / height) * 20)
        b = int(46 + (y / height) * 20)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add title text
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        # Fallback to default font if Helvetica not available
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw title
    title_text = "Radiology AI Assistant"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 150), title_text, fill='white', font=title_font)
    
    # Draw subtitle
    subtitle_text = "Advanced Medical Image Analysis"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, 220), subtitle_text, fill='#4CAF50', font=subtitle_font)
    
    # Add loading text
    loading_text = "Initializing AI Models..."
    loading_bbox = draw.textbbox((0, 0), loading_text, font=subtitle_font)
    loading_width = loading_bbox[2] - loading_bbox[0]
    loading_x = (width - loading_width) // 2
    draw.text((loading_x, 320), loading_text, fill='#cccccc', font=subtitle_font)
    
    # Save the image
    image.save('splash.png')
    print("Splash screen created: splash.png")

if __name__ == "__main__":
    create_splash_screen()
