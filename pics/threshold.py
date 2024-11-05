import numpy as np
from PIL import Image

def threshold_image(input_path, output_path, threshold=128, invert=False):
    """
    Converts an image to binary (black and white) based on a threshold value.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save thresholded image
        threshold (int): Threshold value (0-255). Pixels above this become white, below become black
        invert (bool): If True, inverts the threshold (above becomes black, below becomes white)
    """
    # Open image and convert to grayscale
    img = Image.open(input_path).convert('L')
    
    # Convert to numpy array for easier processing
    data = np.array(img)
    
    # Create binary mask based on threshold
    if not invert:
        binary = data > threshold
    else:
        binary = data <= threshold
    
    # Convert boolean mask to 0 and 255 values
    result = binary.astype('uint8') * 255
    
    # Convert back to PIL Image
    binary_img = Image.fromarray(result)
    
    # If original image had alpha channel, preserve it
    original = Image.open(input_path)
    if original.mode == 'RGBA':
        # Create new RGBA image
        final_img = Image.new('RGBA', binary_img.size)
        # Get alpha channel from original
        alpha = original.split()[3]
        # Combine binary image with original alpha
        final_img.paste(binary_img, mask=alpha)
        final_img.putalpha(alpha)
        final_img.save(output_path, 'PNG')
    else:
        binary_img.save(output_path)

def adaptive_threshold(input_path, output_path, block_size=11, c=2):
    """
    Applies adaptive thresholding to an image.
    The threshold is calculated for smaller regions of the image, 
    which can give better results for images with varying brightness.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save thresholded image
        block_size (int): Size of pixel neighborhood used to calculate threshold value
        c (int): Constant subtracted from the mean (higher values = more white pixels)
    """
    # Open image and convert to grayscale
    img = Image.open(input_path).convert('L')
    data = np.array(img)
    
    # Ensure block_size is odd
    block_size = block_size if block_size % 2 == 1 else block_size + 1
    
    # Calculate padding size
    pad = block_size // 2
    
    # Create output array
    result = np.zeros_like(data)
    
    # Apply adaptive threshold
    for i in range(pad, data.shape[0] - pad):
        for j in range(pad, data.shape[1] - pad):
            # Get neighborhood
            neighborhood = data[i-pad:i+pad+1, j-pad:j+pad+1]
            # Calculate threshold for this pixel
            threshold = np.mean(neighborhood) - c
            # Apply threshold
            result[i, j] = 255 if data[i, j] > threshold else 0
    
    # Convert back to PIL Image
    binary_img = Image.fromarray(result)
    
    # Handle alpha channel as in the simple threshold function
    original = Image.open(input_path)
    if original.mode == 'RGBA':
        final_img = Image.new('RGBA', binary_img.size)
        alpha = original.split()[3]
        final_img.paste(binary_img, mask=alpha)
        final_img.putalpha(alpha)
        final_img.save(output_path, 'PNG')
    else:
        binary_img.save(output_path)

# Example usage
if __name__ == "__main__":
    # Simple threshold
    threshold_image(
        'output.png',
        'output_simple.png',
        threshold=128,  # middle value
        invert=False
    )
    
    # Adaptive threshold
    adaptive_threshold(
        'input.png',
        'output_adaptive.png',
        block_size=11,
        c=2
    )