import ollama

def extract_transcript_from_srt(srt_path):
    """
    Extract clean transcript text from an SRT file, removing timestamps and indices.
    
    Args:
        srt_path (str): Path to the SRT file
        
    Returns:
        str: Clean transcript text as a single string
    """
    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
    except FileNotFoundError:
        print(f"SRT file not found: {srt_path}")
        return ""
    
    lines = srt_content.strip().split('\n')
    transcript_parts = []
    
    i = 0
    while i < len(lines):
        # Skip index lines (just numbers)
        if lines[i].strip().isdigit():
            i += 1
            # Skip timestamp lines (containing -->)
            if i < len(lines) and "-->" in lines[i]:
                i += 1
                # Collect text lines until we hit an empty line or end of file
                text_chunk = []
                while i < len(lines) and lines[i].strip():
                    text_chunk.append(lines[i].strip())
                    i += 1
                transcript_parts.append(" ".join(text_chunk))
        else:
            i += 1
    
    # Join all transcript parts with spaces
    return " ".join(transcript_parts)


# ✅ TITLE
def generate_title(video_path):
    """Generate a title for a video based on the video's content."""

    # print(f"\n>>> Generating title for {video_path}")

    # Get the SRT file path from the video path
    srt_path = video_path.rsplit(".", 1)[0] + ".srt"
    
    transcript = extract_transcript_from_srt(srt_path) # 250327-2152 works

    # Generate the title with OLLAMA
    result = ollama.generate("llama3.2", f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate a title, in English, for this video. 
DO NOT include 'Mayo Clinic' in the title.
DO NOT output anything else than the title.
DO NOT share your reasoning.
Make sure the title is not too long (it will be displayed in a video portal)

<transcript>
{transcript}
</transcript>

    """)

    # The title 

    video_title = '\n'.join(line.strip() for line in result.response.splitlines())

    # Create a _title.txt file and write the video title into it
    title_file_path = video_path.rsplit(".", 1)[0] + "_title.txt"
    
    try:
        with open(title_file_path, 'w', encoding='utf-8') as title_file:
            title_file.write(video_title)
        # print(f"  ✅ Title saved to: {os.path.basename(title_file_path)}")
    except Exception as e:
        print(f"  ❌ Error saving title to file: {str(e)}")


    return video_title



def generate_description(video_path):
    """Generate a description for a video based on the video's content."""

    # print(f"\n>>> Generating description for {video_path}")

    # Get the SRT file path from the video path
    srt_path = video_path.rsplit(".", 1)[0] + ".srt"
    
    transcript = extract_transcript_from_srt(srt_path)

    # Generate the description with OLLAMA
    result = ollama.generate("llama3.2", f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate a description, in English, for this video. 
DO NOT include 'Mayo Clinic' in the description.
DO NOT output anything else than the description.
DO NOT share your reasoning.
OUTPUT ONLY THE DESCRIPTION, which will be displayed as is in the video portal.
Make sure the description is concise but informative.

<transcript>
{transcript}
</transcript>

    """)

    # The description 
    video_description = '\n'.join(line.strip() for line in result.response.splitlines())

    # Create a _description.txt file and write the video description into it
    description_file_path = video_path.rsplit(".", 1)[0] + "_description.txt"
    
    try:
        with open(description_file_path, 'w', encoding='utf-8') as description_file:
            description_file.write(video_description)
        # print(f"  ✅ Description saved to: {os.path.basename(description_file_path)}")
    except Exception as e:
        print(f"  ❌ Error saving description to file: {str(e)}")

    return video_description



def generate_tags(video_path):
    """Generate tags for a video based on the video's content."""

    # print(f"\n>>> Generating tags for {video_path}")

    # Get the SRT file path from the video path
    srt_path = video_path.rsplit(".", 1)[0] + ".srt"
    
    transcript = extract_transcript_from_srt(srt_path)

    # Generate the tags with OLLAMA
    result = ollama.generate("llama3.2", f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate tags, in English, for this video.
Each tag should be two words maximum, but ideally one word.
Tags can be both what type of video it is and what it's about.
DO NOT include 'Mayo Clinic' in the tags.
DO NOT output anything else than the tags.
DO NOT share your reasoning.
Make sure the tags are relevant and concise.
Separate tags with commas.

<transcript>
{transcript}
</transcript>

    """)

    # The tags 
    video_tags = '\n'.join(line.strip() for line in result.response.splitlines())

    # Create a _tags.txt file and write the video tags into it
    tags_file_path = video_path.rsplit(".", 1)[0] + "_tags.txt"
    
    try:
        with open(tags_file_path, 'w', encoding='utf-8') as tags_file:
            tags_file.write(video_tags)
        # print(f"  ✅ Tags saved to: {os.path.basename(tags_file_path)}")
    except Exception as e:
        print(f"  ❌ Error saving tags to file: {str(e)}")

    return video_tags



