"""
Script to create a simple CSV2JSON application icon.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size=256):
    """Create a simple CSV2JSON icon."""
    # Create a new image with a white background
    img = Image.new('RGBA', (size, size), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for the CSV file (blue)
    csv_color = (41, 128, 185)  # Blue
    json_color = (39, 174, 96)  # Green
    arrow_color = (52, 73, 94)  # Dark gray
    
    # Calculate sizes
    padding = size // 10
    file_width = (size - 3 * padding) // 2
    file_height = size - 2 * padding
    corner_radius = size // 20
    
    # Draw CSV file (left)
    draw.rounded_rectangle(
        [(padding, padding), 
         (padding + file_width, padding + file_height)],
        fill=csv_color,
        radius=corner_radius
    )
    
    # Draw JSON file (right)
    draw.rounded_rectangle(
        [(size - padding - file_width, padding), 
         (size - padding, padding + file_height)],
        fill=json_color,
        radius=corner_radius
    )
    
    # Draw arrow
    arrow_width = padding
    arrow_x = size // 2
    arrow_y = size // 2
    arrow_size = size // 6
    
    # Arrow points
    points = [
        (arrow_x - arrow_size, arrow_y - arrow_size//2),  # Left top
        (arrow_x + arrow_size//2, arrow_y - arrow_size//2),  # Right top
        (arrow_x + arrow_size//2, arrow_y - arrow_size),  # Right upper
        (arrow_x + arrow_size, arrow_y),  # Right point
        (arrow_x + arrow_size//2, arrow_y + arrow_size),  # Right lower
        (arrow_x + arrow_size//2, arrow_y + arrow_size//2),  # Right bottom
        (arrow_x - arrow_size, arrow_y + arrow_size//2),  # Left bottom
    ]
    draw.polygon(points, fill=arrow_color)
    
    # Add text
    try:
        # Try to load a font
        font_size = size // 8
        font = ImageFont.truetype("arial.ttf", font_size)
        
        # Add CSV text
        draw.text((padding + file_width//2, padding + file_height//3), 
                 "CSV", fill="white", font=font, anchor="mm")
        
        # Add JSON text
        draw.text((size - padding - file_width//2, padding + file_height//3), 
                 "JSON", fill="white", font=font, anchor="mm")
    except Exception:
        # If font loading fails, skip text
        pass
    
    return img

def save_icons():
    """Create and save icons in different sizes."""
    # Create resources directory if it doesn't exist
    resources_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create and save icons in different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    for size in sizes:
        icon = create_icon(size)
        icon_path = os.path.join(resources_dir, f"icon_{size}.png")
        icon.save(icon_path)
        print(f"Created icon: {icon_path}")
    
    # Create ICO file for Windows
    icon = create_icon(256)
    ico_path = os.path.join(resources_dir, "csv2json.ico")
    icon.save(ico_path, format="ICO", sizes=[(size, size) for size in sizes])
    print(f"Created ICO file: {ico_path}")

if __name__ == "__main__":
    save_icons()
