import ollama
# import subprocess


"""
TODO:
- generate titles/subtitles with more randomness in the topic by passing a list of already generated titles/subtitles
"""

def generate_title_with_ollama(theme):

    result = ollama.generate("llama3.3", f"""

Generate a creative and concise title for a presentation part of the following theme: {theme}.
Only return the title, no other text.
This will be inserted into the title slide of a PowerPoint presentation.
                                                            
    """)

    output = '\n'.join(line.strip() for line in result.response.splitlines())

    # Remove any quotes at the beginning and end of title
    if output:
        output = output.strip('"\'')

    print(f"generate_title_with_ollama > {output}\n\n")

    return output



def generate_subtitle_with_ollama(title):

    result = ollama.generate("llama3.3", f"""

Generate a creative and concise subtitle for a presentation with title: '{title}'.
Only return the subtitle, no other text.
This will be inserted into the subtitle text field in the title slide of a PowerPoint presentation.
                                                            
    """)

    output = '\n'.join(line.strip() for line in result.response.splitlines())

    # Remove any quotes at the beginning and end of subtitle
    if output:
        output = output.strip('"\'')

    print(f"generate_subtitle_with_ollama > {output}\n\n")

    return output