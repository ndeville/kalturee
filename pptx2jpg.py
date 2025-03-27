import subprocess
import os
import sys

def convert_first_slide_to_jpg(pptx_path):
    if not pptx_path.endswith('.pptx'):
        raise ValueError("File must be a .pptx")

    abs_path = os.path.abspath(pptx_path)
    folder = os.path.dirname(abs_path)
    base_name = os.path.splitext(os.path.basename(pptx_path))[0]

    # Use LibreOffice to convert all slides to JPG
    subprocess.run([
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "--headless",
        "--convert-to", "jpg:draw_jpg_Export",
        # f"--filter:options=PixelWidth=1920,PixelHeight=1080",
        "--outdir", folder,
        abs_path
    ], check=True)

    # First slide typically named like "presentation_name.jpg"
    # or "presentation_name1.jpg" depending on version
    for suffix in ["", "1"]:
        candidate = os.path.join(folder, f"{base_name}{suffix}.jpg")
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError("First slide JPG not found after conversion")

if __name__ == "__main__":
    pptx_path = "/Users/nic/dl/file.pptx"

    output = convert_first_slide_to_jpg(pptx_path)
    print(f"\n✅ First slide saved as: {output}\n")