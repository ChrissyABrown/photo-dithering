import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import colorsys

def generate_filtered_palette(image, num_colors=7, min_distance=30):
    """
    Generate a filtered and enhanced palette from the image's dominant colors.
    """
    # Convert image to RGB and flatten it
    image_data = np.array(image.convert('RGB'))
    image_data = image_data.reshape((-1, 3))  # Reshape to a list of RGB pixels

    # Use KMeans clustering to find dominant colors
    kmeans = KMeans(n_clusters=num_colors * 2, random_state=0).fit(image_data)
    dominant_colors = kmeans.cluster_centers_

    # Filter colors to ensure minimum distance
    filtered_colors = []
    for color in dominant_colors:
        color = tuple(map(int, color))
        if all(np.linalg.norm(np.array(color) - np.array(existing)) > min_distance for existing in filtered_colors):
            filtered_colors.append(color)
        if len(filtered_colors) >= num_colors:
            break

    # Adjust colors to enhance warmth and brightness
    enhanced_colors = []
    for r, g, b in filtered_colors:
        # Convert RGB to HLS for adjustment
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        
        # Shift hue slightly toward red/orange and boost saturation
        h = (h + 0.05) % 1.0  # Adjust hue (warmth)
        s = min(s * 1.2, 1.0)  # Boost saturation
        l = min(l * 1.1, 1.0)  # Slightly increase brightness
        
        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        enhanced_colors.append((int(r * 255), int(g * 255), int(b * 255)))

    # Flatten the palette and pad to 256 colors
    palette = []
    for color in enhanced_colors:
        palette.extend(color)
    palette += [0, 0, 0] * (256 - len(enhanced_colors))
    return palette[:256 * 3]  # Ensure palette size is correct

def apply_palette(image, palette):
    """
    Apply a custom palette to an image.
    """
    # Create a new palette image
    pal_image = Image.new("P", (1, 1))
    pal_image.putpalette(palette)

    # Quantize the original image using the new palette
    quantized_image = image.quantize(palette=pal_image)
    return quantized_image.convert('RGB')

def process_image_with_dynamic_palette(input_image, output_folder_landscape, output_folder_portrait, num_colors=8):
    """
    Process an image by generating and applying a filtered, enhanced dynamic palette,
    and save it into the appropriate subfolder based on its orientation.
    """
    # Generate a filtered and enhanced palette
    palette = generate_filtered_palette(input_image, num_colors)

    # Apply the palette to the image
    quantized_image = apply_palette(input_image, palette)

    # Determine orientation and save to the appropriate folder
    width, height = input_image.size
    if width > height:
        output_folder = output_folder_landscape
    else:
        output_folder = output_folder_portrait

    # Construct output filename and save
    output_filename = os.path.join(output_folder, os.path.splitext(os.path.basename(input_image.filename))[0] + '_output.bmp')
    quantized_image.save(output_filename)

    print(f"Saved processed image to {output_filename}")

def process_folder(folder_path, num_colors=8):
    """
    Process all images in a folder, saving results into portrait and landscape subfolders.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    # Create output subfolders
    output_folder_landscape = os.path.join(folder_path, "dithered-landscape")
    output_folder_portrait = os.path.join(folder_path, "dithered-portrait")
    os.makedirs(output_folder_landscape, exist_ok=True)
    os.makedirs(output_folder_portrait, exist_ok=True)

    # Process each image in the folder
    for file_name in os.listdir(folder_path):
        input_file_path = os.path.join(folder_path, file_name)

        # Skip non-image files
        if not file_name.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png')):
            continue

        try:
            with Image.open(input_file_path) as img:
                img.filename = file_name  # Preserve filename for saving
                process_image_with_dynamic_palette(img, output_folder_landscape, output_folder_portrait, num_colors)
        except Exception as e:
            print(f"Error processing {input_file_path}: {e}")

    print(f"All images processed. Output saved to {output_folder_landscape} and {output_folder_portrait}")

if __name__ == "__main__":
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process images in a folder with dynamic palettes.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing images.')
    parser.add_argument('--num_colors', type=int, default=7, help='Number of colors in the dynamic palette.')

    # Parse arguments
    args = parser.parse_args()

    # Run processing
    process_folder(args.folder_path, args.num_colors)
