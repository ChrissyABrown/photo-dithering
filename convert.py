import os
from PIL import Image, ImageOps
import argparse

def process_image(input_image, output_folder_landscape, output_folder_portrait, warm=False, display_direction=None, display_mode='scale', display_dither=Image.FLOYDSTEINBERG):
    # Get the original image size
    width, height = input_image.size

    # Default target size based on orientation
    if display_direction:
        if display_direction == 'landscape':
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
    else:
        # Automatically decide based on aspect ratio
        if width > height:
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800

    if display_mode == 'scale':
        # Compute scaling
        scale_ratio = max(target_width / width, target_height / height)
        resized_width = int(width * scale_ratio)
        resized_height = int(height * scale_ratio)

        output_image = input_image.resize((resized_width, resized_height))
        resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        left = (target_width - resized_width) // 2
        top = (target_height - resized_height) // 2
        resized_image.paste(output_image, (left, top))
    elif display_mode == 'cut':
        # Handle cropping and padding
        if width / height >= target_width / target_height:
            delta_width = int(height * target_width / target_height - width)
            padding = (delta_width // 2, 0, delta_width - delta_width // 2, 0)
            box = (0, 0, width, height)
        else:
            delta_height = int(width * target_height / target_width - height)
            padding = (0, delta_height // 2, 0, delta_height - delta_height // 2)
            box = (0, 0, width, height)

        resized_image = ImageOps.pad(input_image.crop(box), size=(target_width, target_height), color=(255, 255, 255), centering=(0.5, 0.5))

    # Choose palette based on the warm flag
    pal_image = Image.new("P", (1, 1))
    if warm:
            # Peachy warm palette
            pal_image.putpalette(
                (0, 0, 0,        # Black
                255, 255, 255,  # White
                255, 183, 176,  # Peach
                255, 105, 97,   # Soft Red
                255, 87, 51,    # Orange-Red
                255, 195, 160,  # Pale Peach
                255, 160, 122   # Light Coral
                ) + (0, 0, 0) * 249  # Fill remaining slots with black
            )
    else:
        # Default palette
        pal_image.putpalette((0, 0, 0, 255, 255, 255, 0, 255, 0, 0, 0, 255, 255, 0, 0, 255) + (0, 0, 0) * 250)

    # Apply quantization and dithering
    quantized_image = resized_image.quantize(dither=display_dither, palette=pal_image).convert('RGB')

    # Determine the correct output folder based on orientation (landscape or portrait)
    if width > height:
        output_folder = output_folder_landscape
    else:
        output_folder = output_folder_portrait

    # Construct output filename, ensuring it saves in the correct subfolder
    output_filename = os.path.join(output_folder, os.path.basename(input_image.filename))
    output_filename = os.path.splitext(output_filename)[0] + '_output.bmp'
    
    # Save output image
    quantized_image.save(output_filename)

    print(f'Successfully converted {input_image.filename} to {output_filename}')


def process_folder(folder_path, warm=False):
    if not os.path.isdir(folder_path):
        print(f'Error: {folder_path} is not a valid directory.')
        return

    # Create output folders for dithered images based on orientation
    suffix = "-warm" if warm else ""
    output_folder_landscape = os.path.join(folder_path, f'dithered-landscape{suffix}')
    output_folder_portrait = os.path.join(folder_path, f'dithered-portrait{suffix}')
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
                process_image(img, output_folder_landscape, output_folder_portrait, warm=warm)
        except Exception as e:
            print(f'Error processing {input_file_path}: {e}')

    print(f'All images processed. Output saved to {output_folder_landscape} and {output_folder_portrait}')


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process all images in a folder with defaults for conversion.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing images.')
    parser.add_argument('--warm', action='store_true', help='Use the warm palette.')

    # Parse arguments
    args = parser.parse_args()

    # Run processing with specified options
    process_folder(args.folder_path, warm=args.warm)



