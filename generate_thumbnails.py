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

    # # Get and print image dimensions and file size
    # with Image.open(output_path) as img:
    #     width, height = img.size
    #     print(f"Image dimensions: {width}x{height} pixels")

    # # Get file size in KB
    # file_size_bytes = os.path.getsize(output_path)
    # file_size_kb = file_size_bytes / 1024
    # print(f"File size: {file_size_kb:.2f} KB\n\n")
    
    return (output_path, title_text, subtitle_text)

























if __name__ == "__main__":

    extract_best_thumbnail("/Users/nic/dl/yt/test/test.mp4")