from PIL import Image, ImageEnhance, ImageFilter
import os

# Set the path to your image folder
image_folder = r'I:\Chordo\chordoproject\product_images'
output_folder = r'I:\Chordo\chordoproject\processed_images'

# Make sure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Set the desired dimensions for resizing
upscale_factor = 2
new_size = (400 * upscale_factor, 400 * upscale_factor)

# Loop through all the files in the image folder
for filename in os.listdir(image_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):  # Process only certain image types
        img_path = os.path.join(image_folder, filename)
        with Image.open(img_path) as img:
            # Convert and resize the image
            img = img.resize(new_size, Image.LANCZOS)
            
            # Apply sharpening filter to enhance details
            img = img.filter(ImageFilter.SHARPEN)

            # Optionally, enhance contrast and sharpness further
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)  # Increase contrast slightly (adjust value as needed)

            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)  # Increase sharpness (adjust value as needed)

            # Convert and save as JPG
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.jpg')
            img = img.convert('RGB')  # Convert to RGB mode for saving as JPG
            img.save(output_path, 'JPEG', quality=95)  # Save as JPG with high quality
            print(f"Processed {filename} to {output_path}")
