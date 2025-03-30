import ollama
from generate_captions import generate_en_srt

def extract_transcript_from_srt(video_path):
    """
    Extract clean transcript text from an SRT file, removing timestamps and indices.
    
    Args:
        srt_path (str): Path to the SRT file
        
    Returns:
        str: Clean transcript text as a single string
    """

    srt_path = video_path.rsplit(".", 1)[0] + ".srt"

    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
    except FileNotFoundError:
        print(f"\n❌ SRT file not found: {srt_path}")
        return False
    
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

    
    transcript = extract_transcript_from_srt(video_path)
    
    if transcript:

        # Generate the title with OLLAMA
        result = ollama.generate("llama3.3", f"""

Below is the transcript of a video enclosed within <transcript> tags.

Generate a concise and engaging video title in English (maximum 100 characters).
Do NOT include 'Mayo Clinic' in the title.
Do NOT summarize or explain; ONLY provide the title.
Make it intriguing and likely to attract viewers.

<transcript>
{transcript}
</transcript>

    """)

        # Process the title from the model response
        video_title = '\n'.join(line.strip() for line in result.response.splitlines())
        
        # Check if title is too long and regenerate if necessary
        max_title_length = 200
        attempts = 0
        max_attempts = 3
        
        while len(video_title) > max_title_length and attempts < max_attempts:
            attempts += 1
            # This loop is incomplete - would need regeneration logic here
        
        # Create a _title.txt file and write the video title into it
        title_file_path = video_path.rsplit(".", 1)[0] + "_title.txt"
        
        try:
            with open(title_file_path, 'w', encoding='utf-8') as title_file:
                title_file.write(video_title)
            # print(f"  ✅ Title saved to: {os.path.basename(title_file_path)}")
        except Exception as e:
            print(f"  ❌ Error saving title to file: {str(e)}")

        return video_title
    
    else:
        print(f"\nℹ️   No transcript found for {video_path}. Generating SRT file...\n")
        generate_en_srt(video_path)
        return generate_title(video_path)


# ✅ DESCRIPTION
def generate_description(video_path):
    """Generate a description for a video based on the video's content."""

    # print(f"\n>>> Generating description for {video_path}")
    
    transcript = extract_transcript_from_srt(video_path)

    if transcript:

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
    
    else:
        return False


# ✅ TAGS
def generate_tags(video_path):
    """Generate tags for a video based on the video's content."""

    # print(f"\n>>> Generating tags for {video_path}")
    
    transcript = extract_transcript_from_srt(video_path)

    if transcript:

        # Generate the tags with OLLAMA
        result = ollama.generate("llama3.2", f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate multiple tags, in English, for this video.
Each tag should be two words maximum, but ideally one word.
Separate tags with commas.
Tags can be both what type of video it is and what it's about.
DO NOT include 'Mayo Clinic' in the tags.
DO NOT output anything else than the tags.
DO NOT share your reasoning.
Make sure the tags are relevant and concise.

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
    
    else:
        return False



if __name__ == "__main__":


    # Start Chrono
    import time
    start_time = time.time()
    import os

    # test_file = "/Users/nic/dl/yt/test/test.mp4"
    test_file = "/Users/nic/dl/yt/pharma-demo/Mayo Clinic Q&A podcast： January bringing an omicron surge.mp4"
    print(f"\n\nTESTING with {test_file}")
    print(f"\ntitle:\t{generate_title(test_file)}\n")
    # print(f"  description:\t{generate_description(test_file)}")
    # print(f"  tags:\t\t{generate_tags(test_file)}")

    # End Chrono
    run_time = round((time.time() - start_time), 3)
    minutes = int(run_time // 60)
    seconds = int(run_time % 60)
    print(f'\n{os.path.basename(__file__)} finished in {minutes}m {seconds}s.\n')