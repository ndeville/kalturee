import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import ollama

from generate_titles import generate_title_with_ollama, generate_subtitle_with_ollama


# VIDEO THUMBNAIL

def frame_score(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)
    return sharpness * (0.5 + brightness / 255)  # weighted combo

def generate_video_thumbnail(video_path, fractions=[0.25, 0.5, 0.75]):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    best_score = -1
    best_frame = None

    for f in fractions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total_frames * f))
        success, frame = cap.read()
        if success:
            score = frame_score(frame)
            if score > best_score:
                best_score = score
                best_frame = frame

    cap.release()
    if best_frame is not None:
        output_path = video_path.rsplit(".", 1)[0] + ".jpg"
        cv2.imwrite(output_path, best_frame)
        print(f"\n✅ Thumbnail saved to: {output_path}\n")



# PPT THUMBNAIL


def generate_ppt_thumbnail(background_image_path, theme, output_path=None):
    # Load background image
    background_image = Image.open(background_image_path).convert("RGBA")

    def get_fitting_font_size(draw, text, max_width, font_path, start_size, min_size):
        font_size = start_size
        font = ImageFont.truetype(font_path, size=font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        while text_width > max_width and font_size > min_size:
            font_size -= 5
            font = ImageFont.truetype(font_path, size=font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        
        return font_size

    def wrap_text(draw, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Check width with current word added
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width > max_width:
                # Remove last word and save line
                current_line.pop()
                if current_line:  # Only save if there are words in current_line
                    lines.append(' '.join(current_line))
                current_line = [word]  # Start new line with current word
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    # Create a drawing context
    draw = ImageDraw.Draw(background_image)

    # Define font paths
    font_path = "/System/Library/Fonts/Helvetica.ttc"

    # Define fixed font sizes
    TITLE_FONT_SIZE = 80
    SUBTITLE_FONT_SIZE = 40

    # Load fonts with fixed sizes
    title_font = ImageFont.truetype(font_path, size=TITLE_FONT_SIZE)
    subtitle_font = ImageFont.truetype(font_path, size=SUBTITLE_FONT_SIZE)

    # Define text
    title_text = generate_title_with_ollama(theme)
    subtitle_text = generate_subtitle_with_ollama(title_text)

    # Calculate maximum allowed width (80% of image width)
    max_width = int(background_image.width * 0.8)

    # Wrap text into multiple lines
    title_lines = wrap_text(draw, title_text, title_font, max_width)
    subtitle_lines = wrap_text(draw, subtitle_text, subtitle_font, max_width)

    # Calculate total height of text blocks
    title_line_height = TITLE_FONT_SIZE * 1.2  # Add 20% spacing between lines
    subtitle_line_height = SUBTITLE_FONT_SIZE * 1.2

    total_title_height = len(title_lines) * title_line_height
    total_subtitle_height = len(subtitle_lines) * subtitle_line_height

    # Calculate starting Y position to center everything
    total_height = total_title_height + total_subtitle_height + 50  # 50px gap between title and subtitle
    start_y = (background_image.height - total_height) // 2

    # Draw title lines
    current_y = start_y
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (background_image.width - text_width) // 2
        draw.text((x, current_y), line, fill="white", font=title_font)
        current_y += title_line_height

    # Add gap between title and subtitle
    current_y += 50

    # Draw subtitle lines
    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        x = (background_image.width - text_width) // 2
        draw.text((x, current_y), line, fill="white", font=subtitle_font)
        current_y += subtitle_line_height

    # Set default output path if none provided
    if output_path is None:
        output_path = os.path.splitext(background_image_path)[0] + "_thumbnail.jpg"
    
    # Convert RGBA to RGB before saving as JPEG
    background_image = background_image.convert('RGB')
    background_image.save(output_path)

    print(f"\n✅ Thumbnail saved to: {output_path}\n")

    # # Get and print image dimensions and file size
    # with Image.open(output_path) as img:
    #     width, height = img.size
    #     print(f"Image dimensions: {width}x{height} pixels")

    # # Get file size in KB
    # file_size_bytes = os.path.getsize(output_path)
    # file_size_kb = file_size_bytes / 1024
    # print(f"File size: {file_size_kb:.2f} KB\n\n")
    
    return (output_path, title_text, subtitle_text)




# PDF THUMBNAIL


def generate_pdf_thumbnail(pdf_path, output_path=None):
    """Generate a 16:9 thumbnail from the first page of a PDF with transparent background."""
    try:
        # Set default output path if none provided
        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + ".png"
        
        # Use PyMuPDF (fitz) for better image quality
        import fitz
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        
        # Create a pixmap with 16:9 aspect ratio
        target_width = 1280  # HD width
        target_height = 720  # HD height (16:9 ratio)
        
        # Render the page to a pixmap
        pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Create a blank 16:9 canvas with transparent background
        thumbnail = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        
        # Resize the PDF image maintaining aspect ratio to fit within the 16:9 canvas
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider than 16:9
            new_width = target_width
            new_height = int(new_width / img_ratio)
        else:
            # Image is taller than 16:9
            new_height = target_height
            new_width = int(new_height * img_ratio)
            
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Center the image on the canvas
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        thumbnail.paste(img_resized, (paste_x, paste_y))
        
        # Save the thumbnail as PNG to preserve transparency
        thumbnail.save(output_path, "PNG")

        print(f"\n✅ Thumbnail saved to: {output_path}\n")
        
        return output_path
    
    except Exception as e:
        print(f"Error generating PDF thumbnail: {e}")
        import traceback
        traceback.print_exc()
        return None




def generate_thumbnails_for_folder(folder_path):
    """
    Generate thumbnails for all PDF files in a folder that don't already have a corresponding JPG.
    
    Args:
        folder_path (str): Path to the folder containing PDF files
        
    Returns:
        int: Number of thumbnails generated
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return 0
        
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{folder_path}'.")
        return 0
        
    count = 0
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        jpg_path = os.path.splitext(pdf_path)[0] + '.jpg'
        
        # Check if JPG already exists
        if not os.path.exists(jpg_path):
            print(f"Generating thumbnail for {pdf_file}...")
            result = generate_pdf_thumbnail(pdf_path)
            if result:
                count += 1
                print(f"✅ Created thumbnail: {os.path.basename(jpg_path)}")
            else:
                print(f"❌ Failed to create thumbnail for {pdf_file}")
        else:
            print(f"Skipping {pdf_file} - thumbnail already exists")
            
    print(f"\nCompleted: Generated {count} new thumbnails out of {len(pdf_files)} PDF files.")
    return count







if __name__ == "__main__":

    # extract_best_thumbnail("/Users/nic/dl/yt/test/test.mp4")
    # generate_pdf_thumbnail("/Users/nic/Dropbox/Kaltura/events/reuters_pharma/250425 How Video can Transform HCP Engagement_Reuters AI Takeaways.pdf")
    generate_thumbnails_for_folder("/Users/nic/Dropbox/Kaltura/nic-mediaspace/pdfs/")