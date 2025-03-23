import whisperx
# from googletrans import Translator
import torch


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
    
    translator = None
    if output_lang != source_lang:
        translator = Translator()

    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        if translator:
            text = translator.translate(text, dest=output_lang).text
        srt_lines.append(str(i))
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(text)
        srt_lines.append("")
    
    srt_content = "\n".join(srt_lines)
    srt_path = mp4_path.rsplit(".", 1)[0] + ".srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return srt_path


if __name__ == "__main__":
    generate_srt("/Users/nic/Downloads/temp/test_video.mp4")
