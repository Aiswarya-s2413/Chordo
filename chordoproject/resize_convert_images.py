from PIL import Image
import os

def resize_and_convert_images(input_folder, output_folder, size=(800, 800), output_format='JPEG'):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each image file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            # Construct the full file path
            file_path = os.path.join(input_folder, filename)

            # Open the image
            with Image.open(file_path) as img:
                # Resize the image
                img = img.resize(size)

                # Convert the image to the specified format
                output_filename = os.path.splitext(filename)[0] + '.' + output_format.lower()
                output_path = os.path.join(output_folder, output_filename)

                # Save the resized and converted image
                img.save(output_path, format=output_format)
                print(f"Processed {filename} -> {output_filename}")

            
if __name__ == '__main__':
    input_folder = 'images'  # Your input folder
    output_folder = 'processed_images'  # Your output folder
    resize_and_convert_images(input_folder, output_folder, size=(800, 800), output_format='JPEG')

