import re
from PIL import Image
import os
import cssutils

def parse_color(color_str):
    """Convert CSS color to RGB tuple."""
    # Handle 3-digit hex
    if len(color_str) == 4:  # #fff format
        r = int(color_str[1] + color_str[1], 16)
        g = int(color_str[2] + color_str[2], 16)
        b = int(color_str[3] + color_str[3], 16)
        return (r, g, b)
    # Handle 6-digit hex
    elif len(color_str) == 7:  # #ffffff format
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        return (r, g, b)
    return None

def replace_colors(image, white_replacement, black_replacement):
    """Replace white and black colors in the image with given colors, preserving transparency."""
    # Convert to RGBA if not already
    img_data = image.convert('RGBA')
    width, height = img_data.size
    new_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    for x in range(width):
        for y in range(height):
            r, g, b, a = img_data.getpixel((x, y))
            
            # Skip fully transparent pixels
            if a == 0:
                continue
                
            # Check if pixel is white (or very close to white)
            if r > 250 and g > 250 and b > 250:
                new_img.putpixel((x, y), (*white_replacement, a))
            # Check if pixel is black (or very close to black)
            elif r < 10 and g < 10 and b < 10:
                new_img.putpixel((x, y), (*black_replacement, a))
            else:
                new_img.putpixel((x, y), (r, g, b, a))
    
    return new_img

def main():
    # Create output directory if it doesn't exist
    if not os.path.exists('bus_icon'):
        os.makedirs('bus_icon')

    # Parse CSS file
    stylesheet = cssutils.parseFile('bus_classes.css')
    
    # Load original icon
    original_icon = Image.open('bus_icon.png')
    
    # Process each rule in CSS
    for rule in stylesheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            # Extract class name
            class_name = rule.selectorText.split('.')[1].split('.')[0]
            
            # Extract colors
            bg_color = None
            text_color = None
            
            for prop in rule.style:
                if prop.name == 'background-color':
                    bg_color = parse_color(prop.value)
                elif prop.name == 'color':
                    text_color = parse_color(prop.value)
            
            if bg_color and text_color:
                # Create new icon with replaced colors
                new_icon = replace_colors(original_icon, bg_color, text_color)
                
                # Save the new icon with transparency
                output_path = os.path.join('pics/bus_icon', f'{class_name}.png')
                new_icon.save(output_path, 'PNG')
                print(f"Generated icon for {class_name}")

if __name__ == "__main__":
        # Copy bus_icon.png to 'bus_icon/undefined.png'
    undefined_output_path = os.path.join('pics/bus_icon', 'undefined.png')
    os.makedirs('pics/bus_icon', exist_ok=True)
    input_icon_path = 'bus_icon.png'
    if os.path.exists(input_icon_path):
        img = Image.open(input_icon_path)
        img.save(undefined_output_path, 'PNG')
        print(f"Copied {input_icon_path} to {undefined_output_path}")
    else:
        print(f"Input icon {input_icon_path} does not exist")
    main()