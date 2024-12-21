from PIL import Image, ImageDraw
import os

def create_logo():
    """Create a simple logo"""
    img = Image.new('RGB', (32, 32), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a medical cross
    draw.rectangle([14, 6, 18, 26], fill='#3498db')  # Vertical
    draw.rectangle([6, 14, 26, 18], fill='#3498db')  # Horizontal
    
    img.save('logo.png')

def create_menu_icon():
    """Create a hamburger menu icon"""
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw three lines
    for y in [6, 12, 18]:
        draw.rectangle([4, y-1, 20, y+1], fill='#2c3e50')
    
    img.save('menu.png')

def create_dropdown_icon():
    """Create a dropdown arrow icon"""
    img = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw arrow
    draw.polygon([(2, 4), (10, 4), (6, 8)], fill='#2c3e50')
    
    img.save('dropdown.png')

def main():
    # Create assets directory if it doesn't exist
    if not os.path.exists('.'):
        os.makedirs('.')
    
    # Create assets
    create_logo()
    create_menu_icon()
    create_dropdown_icon()
    
    print("Assets created successfully!")

if __name__ == '__main__':
    main()
