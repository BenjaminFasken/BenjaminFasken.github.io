import numpy as np
from PIL import Image

def modify_edge_color(input_path, output_path, new_edge_color, kernel_size=5):
    """
    Modifies the color of pixels that are on the edge of non-transparent areas in a PNG.
    
    Args:
        input_path (str): Path to input PNG image
        output_path (str): Path to save modified image
        new_edge_color (tuple): RGB tuple for new edge color (e.g., (255, 0, 0) for red)
        kernel_size (int): Size of the kernel for edge detection (odd number)
    """
    # Ensure kernel_size is odd
    kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    
    # Open image and convert to RGBA if not already
    img = Image.open(input_path).convert('RGBA')
    
    # Convert to numpy array for easier processing
    data = np.array(img)
    
    # Create alpha mask (True where pixel is not transparent)
    alpha_mask = data[:, :, 3] > 0
    
    # Create edge detection kernel
    kernel = np.ones((kernel_size, kernel_size))
    kernel[kernel_size//2, kernel_size//2] = 0
    
    # Find edges by convolving with kernel
    edges = np.zeros_like(alpha_mask)
    pad = kernel_size // 2
    
    for i in range(pad, alpha_mask.shape[0] - pad):
        for j in range(pad, alpha_mask.shape[1] - pad):
            if alpha_mask[i, j]:  # Only check non-transparent pixels
                # Get neighborhood of kernel_size x kernel_size
                neighborhood = alpha_mask[i-pad:i+pad+1, j-pad:j+pad+1]
                # If any neighbor is transparent, this is an edge
                if not np.all(neighborhood):
                    edges[i, j] = 1
    
    # Create modified image array
    modified_data = data.copy()
    
    # Change color of edge pixels
    modified_data[edges == 1] = [*new_edge_color, 255]  # RGB + full opacity
    
    # Convert back to PIL Image and save
    modified_img = Image.fromarray(modified_data)
    modified_img.save(output_path, 'PNG')

# Example usage
if __name__ == "__main__":
    # Example with black edges
    modify_edge_color(
        'bus_icon.png',
        'output.png',
        (0, 0, 0),  # Black
        kernel_size=7  # Increased kernel size
    )