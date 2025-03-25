import whisperx
# from googletrans import Translator
import torch
import ollama


def generate_srt(mp4_path, source_lang="EN", output_lang="EN", model_name="large-v3"):
    source_lang = source_lang.lower()
    output_lang = output_lang.lower()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Specify compute_type based on device
    compute_type = "float16" if device == "cuda" else "float32"
    model = whisperx.load_model(model_name, device, compute_type=compute_type)
    result = model.transcribe(mp4_path, language=source_lang)
    
    # The alignment might need to be adjusted depending on the WhisperX version
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio=mp4_path, device=device)
    segments = result["segments"]
    
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    
    # Add Ollama translation function
    def translate_text(text, target_lang):
        # import requests

        result = ollama.generate("winkefinger/alma-13b", f"""

        Translate this from English to {target_lang}:

        English: {text}
        {target_lang}:                          

        """)

        output = '\n'.join(line.strip() for line in result.response.splitlines())

        return output  # fallback to original text if translation fails
    
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        if output_lang != source_lang:
            text = translate_text(text, output_lang)
        srt_lines.append(str(i))
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(text)
        srt_lines.append("")
    
    srt_content = "\n".join(srt_lines)
    # Modify the output path to include language code if not English
    base_path = mp4_path.rsplit(".", 1)[0]
    if output_lang.upper() != "EN":
        srt_path = f"{base_path}_{output_lang.upper()}.srt"
    else:
        srt_path = f"{base_path}.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"\n✅ Generated SRT file: {srt_path}\n")
    return srt_path


if __name__ == "__main__":
    generate_srt("/Users/nic/Downloads/temp/test_video.mp4", source_lang="EN", output_lang="FR", model_name="large-v3")
