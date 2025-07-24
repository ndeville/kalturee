import os
import ollama
from generate_captions import generate_en_srt

# def extract_transcript_from_srt(video_path):

#     srt_path = video_path.rsplit(".", 1)[0] + ".srt"

#     try:
#         with open(srt_path, "r", encoding="utf-8") as f:
#             srt_content = f.read()
#     except FileNotFoundError:
#         print(f"\n❌ SRT file not found: {srt_path}")
#         return False
    
#     lines = srt_content.strip().split('\n')
#     transcript_parts = []
    
#     i = 0
#     while i < len(lines):
#         # Skip index lines (just numbers)
#         if lines[i].strip().isdigit():
#             i += 1
#             # Skip timestamp lines (containing -->)
#             if i < len(lines) and "-->" in lines[i]:
#                 i += 1
#                 # Collect text lines until we hit an empty line or end of file
#                 text_chunk = []
#                 while i < len(lines) and lines[i].strip():
#                     text_chunk.append(lines[i].strip())
#                     i += 1
#                 transcript_parts.append(" ".join(text_chunk))
#         else:
#             i += 1
    
#     # Join all transcript parts with spaces
#     return " ".join(transcript_parts)



# # TITLE
# def generate_title(video_path):
#     """Generate a title for a video based on the video's content."""

#     max_title_length = 100
#     max_attempts = 3

#     print(f"\t>>> Generating title for {video_path} with max {max_title_length} characters")

#     # Try to get transcript from the corresponding .txt file
#     txt_path = video_path.rsplit(".", 1)[0] + ".txt"
#     try:
#         with open(txt_path, "r", encoding="utf-8") as f:
#             transcript = f.read().strip()
#     except FileNotFoundError:
#         # If .txt file not found, try to generate SRT first
#         print(f"\nℹ️   No transcript .txt file found for {video_path}. Generating SRT file...\n")
#         generate_en_srt(video_path)
        
#         # Try again to read the .txt file
#         try:
#             with open(txt_path, "r", encoding="utf-8") as f:
#                 transcript = f.read().strip()
#         except FileNotFoundError:
#             print(f"\n❌ Transcript .txt file still not found after generating SRT: {txt_path}")
#             transcript = False
    
#     if transcript:

#         # Generate the title with OLLAMA
#         result = ollama.generate("llama3.3", f"""

# Below is the transcript of a video enclosed within <transcript> tags.

# Generate a concise and engaging video title in English (maximum {max_title_length} characters).
# Do NOT include 'Mayo Clinic' in the title.
# Do NOT summarize or explain; ONLY provide the title.
# Make it intriguing and likely to attract viewers.
# It is critical that the title is maximum {max_title_length} characters.


# <transcript>
# {transcript}
# </transcript>

#     """)

#         # Process the title from the model response
#         video_title = '\n'.join(line.strip() for line in result.response.splitlines())
        
#         # Check if title is too long and regenerate if necessary
#         attempts = 0
        
#         while len(video_title) > max_title_length and attempts < max_attempts:
#             attempts += 1
#             print(f"  ⚠️ Title too long ({len(video_title)} chars). Regenerating (attempt {attempts}/{max_attempts})...")
#             video_title = generate_title(video_path)
        
#         # Create a _title.txt file and write the video title into it
#         title_file_path = video_path.rsplit(".", 1)[0] + "_title.txt"
        
#         with open(title_file_path, 'w', encoding='utf-8') as title_file:
#             title_file.write(video_title)

#         return video_title
    
#     else:
#         print(f"\nℹ️   No transcript found for {video_path}. Generating SRT file...\n")
#         generate_en_srt(video_path)
#         return generate_title(video_path)




def get_transcript(video_path):
    """Get transcript from .txt file or generate it if not available."""
    
    # Try to get transcript from the corresponding .txt file
    txt_path = video_path.rsplit(".", 1)[0] + ".txt"
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            transcript = f.read().strip()
            return transcript
    except FileNotFoundError:
        # If .txt file not found, try to generate SRT first
        print(f"\nℹ️   No transcript .txt file found for {video_path}. Generating SRT file...\n")
        generate_en_srt(video_path)
        
        # Try again to read the .txt file
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
                return transcript
        except FileNotFoundError:
            print(f"\n❌ Transcript .txt file still not found after generating SRT: {txt_path}")
            return False




# TITLE

# llm_model_for_title_generation = "cognitivetech/obook_title"
llm_model_for_title_generation = "gemma3"

def generate_title(video_path, title_source: str = "filename", source_language: str = "EN"): # title_source: "filename" or "transcript" or "json" or "channel_name"
    """
    250330-1300: currently generates clean title from filename as attempts to generate from transcript were not working for free with Ollama (only with paid-for GPT-4).
    TODO:
    - logic to extract title from .info.json file
    - logic to generate title from transcript if no .info.json file is found
    - mechanism to decide which logic to use between "from_json" and "from_transcript" and "from_filename"
    """
    global llm_model_for_title_generation

    max_title_length = 200

    system_prompt = f"""
You are a helpful assistant tasked to come up with the best title for a video, given the transcript of a video.
It is critical that your output is maximum {max_title_length} characters long.
Make sure that 'Mayo Clinic' is NOT in your output.
Make sure that the title is in {source_language}.
ONLY output the title in {source_language}, nothing else.
        """

    if title_source == "filename":

        file_name = os.path.basename(video_path)
        
        print(f"\n>>> Generating title for {video_path} from filename.")
            
        prompt = f"""{system_prompt}
Generate a concise and engaging video title in English (maximum {max_title_length} characters) using the file name provided below.
Do NOT include 'Mayo Clinic' in the title.
Do NOT summarize or explain; ONLY provide the title.
Make it intriguing and likely to attract viewers.

<file_name>
{file_name}
</file_name>
"""

        result = ollama.generate(llm_model_for_title_generation, prompt)

    elif title_source == "channel_name":

        # Get the channel name from the filename
        channel_name = "?????????"

        print(f"\n>>> Generating title for {video_path} based on channel name: {channel_name}")
        input(f"❌ generate_metadata.py > generate_title() > Logic not implemented yet. Not title generated from channel name. Press Enter to continue...")



    video_title = '\n'.join(line.strip() for line in result.response.splitlines())

    # Remove any quotes from the title
    video_title = video_title.replace('"', '').replace("'", "")
    
    
    print(f"\tℹ️   Title generated with {len(video_title)} chars:\t> {video_title}")

    if len(video_title) <= max_title_length:
        # Write successful title to file
        title_file_path = video_path.rsplit(".", 1)[0] + "_title.txt"
        with open(title_file_path, 'w', encoding='utf-8') as title_file:
            title_file.write(video_title)
        print(f"✅   Title saved to: {title_file_path}")
        return video_title
    
    else:
        print(f"\n\n❌❌❌ FAILURE: Title is {len(video_title)} characters long.:\n{video_title=}\nTrying again...\n")
        generate_title(video_path)
            
    return video_title  # Return the last attempt








# ✅ DESCRIPTION

llm_model_for_description = "gemma3"
# llm_model_for_description = "llama3.3"

def generate_description(video_path, based_on="filename", source_language="EN"): # based_on: "transcript" or "filename"
    """
    250330-1311: currently generates clean description from transcript.
    TODO:
    - logic to extract description from .info.json file
    - mechanism to decide which logic to use between "from_json" and "from_transcript"
    """
    global llm_model_for_description
    
    if based_on == "transcript":
        transcript = get_transcript(video_path)

        if transcript:

            print(f"\n>>> Generating description for {video_path} from transcript.")

            # Generate the description with OLLAMA
            result = ollama.generate(llm_model_for_description, f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate a description, in {source_language}, for this video. 
DO NOT include 'Mayo Clinic' in the description.
DO NOT output anything else than the description.
DO NOT share your reasoning.
DO NOT mention "the transcript discusses.." or similar. Write the description of what to expect in the video based on the transcript.
DO NOT start or end the description with quotes.
DO NOT format your output with markdown.
OUTPUT ONLY THE DESCRIPTION, which will be displayed as is in the video portal.
Make sure that the output does not have any Markdown formatting.
Make sure that the output is in {source_language}.
ONLY output the description, nothing else.
DO NOT provide a transcript, but just a summary.
Keep it short and concise - ideally around 500 characters.

<transcript>
{transcript}
</transcript>

Make sure that the output does not have any Markdown formatting.

    """, stream=False)  # Add stream=False to ensure complete response
        
    elif based_on == "filename":

        file_name = os.path.basename(video_path)

        result = ollama.generate(llm_model_for_description, f"""
Come up with a description of 500 characters or less, in {source_language}, for a video with the filename {file_name}.
DO NOT output anything else than the description.
DO NOT share your reasoning.
DO NOT start or end the description with quotes.
DO NOT format your output with markdown.
OUTPUT ONLY THE DESCRIPTION, which will be displayed as is in the video portal.
Make sure that the output does not have any Markdown formatting.
Make sure that the output is in {source_language}.
ONLY output the description, nothing else.
    """, stream=False)  # Add stream=False to ensure complete response


        # The description - ensure we get the full response
        if hasattr(result, 'response'):
            video_description = result.response.strip()
        else:
            print(f"❌ Error generating description: {str(result)}")
            video_description = str(result).strip()

        # Remove any quotes (single or double) at the beginning or end of the description
        video_description = video_description.strip('"\'')

        print(f"\nℹ️   Description generated with {len(video_description)} chars (using {llm_model_for_description}):\n{video_description}")

        # Create a _description.txt file and write the video description into it
        description_file_path = video_path.rsplit(".", 1)[0] + "_description.txt"
        
        try:
            with open(description_file_path, 'w', encoding='utf-8') as description_file:
                description_file.write(video_description)
            print(f"\n✅ Description saved to: {description_file_path}")
        except Exception as e:
            print(f"\n❌ Error saving description to file: {str(e)}")

        return video_description
    
    else:
        return False






# ✅ TAGS

# llm_model_for_tags_generation = "cognitivetech/obook_title"
llm_model_for_tags_generation = "gemma3"

def generate_tags(video_path, based_on="filename", source_language="EN"): # based_on: "transcript" or "filename"
    """Generate tags for a video based on the video's content."""

    print(f"\n>>> Generating tags for {video_path}")
    
    if based_on == "transcript":
        transcript = get_transcript(video_path)

        if transcript:

            # Generate the tags with OLLAMA
            result = ollama.generate(llm_model_for_tags_generation, f"""

The content provided below between the <transcript> tags is a transcript of a video.
Generate multiple tags, in {source_language}, for this video.
Each tag should be two words maximum, but ideally one word.
Separate tags with commas.
Maximum 5 tags.
Tags can be both what type of video it is and what it's about.
DO NOT include 'Mayo Clinic' in the tags.
DO NOT output anything else than the tags.
DO NOT share your reasoning.
Make sure the tags are relevant and concise.
Make sure the tags are in {source_language}.

<transcript>
{transcript}
</transcript>

    """)
            
    elif based_on == "filename":

        file_name = os.path.basename(video_path)

        # Generate the tags
        result = ollama.generate(llm_model_for_tags_generation, f"""
Come up with 3 tags, in {source_language}, for a video with the filename {file_name}.
Each tag should be two words maximum, but ideally one word.
Separate tags with commas.
Maximum 5 tags.
Tags can be both what type of video it is and what it's about.
DO NOT include 'Mayo Clinic' in the tags.
DO NOT output anything else than the tags.
DO NOT share your reasoning.
Make sure the tags are relevant and concise.
Make sure the tags are in {source_language}.
    """, stream=False)  # Add stream=False to ensure complete response



    # The tags 
    video_tags = '\n'.join(line.strip() for line in result.response.splitlines())

    print(video_tags)

    # Create a _tags.txt file and write the video tags into it
    tags_file_path = video_path.rsplit(".", 1)[0] + "_tags.txt"
    
    try:
        with open(tags_file_path, 'w', encoding='utf-8') as tags_file:
            tags_file.write(video_tags)
        print(f"✅ Tags saved to: {tags_file_path}")
    except Exception as e:
        print(f"  ❌ Error saving tags to file: {str(e)}")

    return video_tags





if __name__ == "__main__":


    # Start Chrono
    import time
    start_time = time.time()
    import os

    test_file = "/Users/nic/dl/yt/test/test.mp4"
    print(f"  tags:\t\t{generate_tags(test_file)}")

    # End Chrono
    run_time = round((time.time() - start_time), 3)
    minutes = int(run_time // 60)
    seconds = int(run_time % 60)
    print(f'\n{os.path.basename(__file__)} finished in {minutes}m {seconds}s.\n')