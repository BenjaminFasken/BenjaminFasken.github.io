import numpy as np
from PIL import Image

def invert_bw(input_path, output_path):
    """
    Inverts black and white values in an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save inverted image
    """
    # Open image
    img = Image.open(input_path)
    
    # Convert to numpy array
    data = np.array(img)
    
    # Handle different image modes
    if img.mode == 'RGBA':
        # For RGBA images, only invert RGB channels, preserve alpha
        rgb_data = data[..., :3]
        alpha = data[..., 3]
        
        # Invert RGB values
        inverted_rgb = 255 - rgb_data
        
        # Reconstruct RGBA
        inverted_data = np.dstack((inverted_rgb, alpha))
        
    elif img.mode == 'L':
        # For grayscale images, simple inversion
        inverted_data = 255 - data
        
    else:
        # For RGB or other formats
        inverted_data = 255 - data
    
    # Convert back to PIL Image
    inverted_img = Image.fromarray(inverted_data.astype('uint8'), mode=img.mode)
    
    # Save the result
    inverted_img.save(output_path)

# Example usage
if __name__ == "__main__":
    invert_bw('bus_icon.png', 'inverted.png')