import ollama
import os

# Add Ollama translation function
def translate_text(text, target_lang):

    # result = ollama.generate("llama3.3", f"""
    result = ollama.generate("winkefinger/alma-13b", f"""

    Translate this from English to {target_lang} and make sure to keep the original line breaks. You must return the exact same number of lines as the original text.

    English: 
    
    <start_of_text>
    {text}
    <end_of_text>

    {target_lang}:                          

    """)

    output = '\n'.join(line.strip() for line in result.response.splitlines())

    return output  # fallback to original text if translation fails

def generate_translated_srt(srt_path, target_lang):
    """
    Based on having a .srt file and a .txt file with the same name, this function will translate the .txt file and save the result as a new .srt file with the timestamps from the original .srt.
    Both the original English .srt and .txt files are created by the generate_captions.py script.
    """
    
    # Normalize target language to lowercase for consistency
    target_lang = target_lang.lower()
    
    # Create output path with language code
    base_path = srt_path.rsplit(".", 1)[0]
    output_path = f"{base_path}_{target_lang}.srt"
    txt_path = f"{base_path}.txt"
    
    # Skip if translation already exists
    if os.path.exists(output_path):
        print(f"⏩ Skipping translation - File already exists: {os.path.basename(output_path)}")
        return output_path
    
    # Check if the .txt file exists
    if not os.path.exists(txt_path):
        print(f"❌ Error: Text file not found: {txt_path}")
        return None
    
    print(f"\n🔄 Translating content to {target_lang.upper()}: {srt_path}")
    
    try:
        # Read the original SRT file to get timestamps and structure
        with open(srt_path, "r", encoding="utf-8") as f:
            srt_lines = f.readlines()
        
        # Read the .txt file for translation
        with open(txt_path, "r", encoding="utf-8") as f:
            txt_content = f.read().strip()
        
        # Count the number of segments in the SRT file
        segment_count = 0
        for line in srt_lines:
            if line.strip() and line.strip().isdigit():
                segment_count += 1
        
        # Count the number of lines in the TXT file
        txt_lines = txt_content.split('\n')
        txt_line_count = len(txt_lines)
        
        # Check if the number of segments matches the number of lines in the TXT file
        if segment_count != txt_line_count:
            print(f"⚠️ Warning: Number of segments in SRT ({segment_count}) does not match number of lines in TXT ({txt_line_count})")
            print(f"⚠️ This may cause misalignment in translations")
        # else:
            # print(f"✅ Verified: Number of segments in SRT ({segment_count}) matches number of lines in TXT ({txt_line_count})")
        
        # Translate the entire text content at once
        print(f"\n> Translating text content...")
        translated_content = translate_text(txt_content, target_lang)
        print(f"> Translation completed")
        
        # Split the translated content into lines
        translated_text_lines = translated_content.split('\n')
        
        # Check if the number of translated lines matches the original
        if len(translated_text_lines) != txt_line_count:
            print(f"⚠️ Warning: Number of translated lines ({len(translated_text_lines)}) does not match original ({txt_line_count})")
            # Adjust translated lines to match original count if needed
            if len(translated_text_lines) < txt_line_count:
                # Add empty lines if we have fewer translated lines
                translated_text_lines.extend([""] * (txt_line_count - len(translated_text_lines)))
            else:
                # Truncate if we have more translated lines
                translated_text_lines = translated_text_lines[:txt_line_count]
        
        # Create the new SRT file with original timestamps but translated text
        translated_srt_lines = []
        text_line_index = 0
        
        i = 0
        while i < len(srt_lines):
            line = srt_lines[i].rstrip('\n')
            
            # Add segment number
            if line and line[0].isdigit() and line.isdigit():
                segment_number = int(line)
                translated_srt_lines.append(line)
                i += 1
                
                # Add timestamp line
                if i < len(srt_lines) and '-->' in srt_lines[i]:
                    translated_srt_lines.append(srt_lines[i].rstrip('\n'))
                    i += 1
                    
                    # Add translated text for this segment, ensuring alignment
                    if text_line_index < len(translated_text_lines):
                        # Ensure we're using the correct line for this segment
                        if text_line_index + 1 != segment_number:
                            print(f"⚠️ Alignment issue: Expected segment {segment_number}, using line {text_line_index + 1}")
                        
                        translated_srt_lines.append(translated_text_lines[text_line_index])
                        text_line_index += 1
                    else:
                        # If we run out of translated lines, use empty line
                        print(f"⚠️ Missing translation for segment {segment_number}")
                        translated_srt_lines.append("")
                    
                    # Add empty line after segment
                    translated_srt_lines.append("")
                    
                    # Skip original text lines until empty line
                    while i < len(srt_lines) and srt_lines[i].strip():
                        i += 1
                    
                    # Skip the empty line
                    if i < len(srt_lines):
                        i += 1
            else:
                i += 1
        
        # Write the translated content to the output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(translated_srt_lines))
        
        print(f"✅ Generated translated SRT file: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error translating SRT file: {str(e)}")
        return None


if __name__ == "__main__":

    # Start Chrono
    import time
    start_time = time.time()
    import os

    srt_path = "/Users/nic/dl/yt/test/test.srt"
    target_lang = "FR"
    output_path =generate_translated_srt(srt_path, target_lang)

    print(f"\nTranslated SRT file: {output_path}")

    # End Chrono
    run_time = round((time.time() - start_time), 3)
    minutes = int(run_time // 60)
    seconds = int(run_time % 60)
    print(f'\n{os.path.basename(__file__)} finished in {minutes}m {seconds}s.\n')