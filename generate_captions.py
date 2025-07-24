import whisperx
# from googletrans import Translator
import torch
import ollama
import json

# Clean up warnings printouts
# import logging
# logging.getLogger("speechbrain.utils.quirks").setLevel(logging.WARNING)
# import warnings
# warnings.filterwarnings("ignore", message="Model was trained with")
# warnings.filterwarnings("ignore", message="Lightning automatically upgraded")

# import os
# # Set this BEFORE importing speechbrain or related libraries.
# os.environ["SB_DISABLE_QUIRKS"] = "1"

# import logging
# logging.getLogger("speechbrain").setLevel(logging.WARNING)
# logging.getLogger("pytorch_lightning").setLevel(logging.WARNING)

# import warnings
# warnings.filterwarnings("ignore", message="Model was trained with")
# warnings.filterwarnings("ignore", message="Lightning automatically upgraded")



def generate_en_srt(mp4_path, language=None):
    """
    250329-1756 FINAL SOLUTION:
    - generate only a .json output with word-level timestamps from whisperx
    - post-process the .json output to create a new .srt file with a more reasonable number of words per segment
    - create a clean .txt version of the SRT file (that can be used for translation)
    """

    import os
    import subprocess
    
    output_dir = os.path.dirname(mp4_path)
    
    # WhisperX Configuration
    
    # LANGUAGE = "EN"
    VERBOSE = "False"
    MODEL = "turbo"
    MODEL_CACHE_ONLY = "False"
    MODEL_DIR = None
    DEVICE = "cpu"  # Changed from "cuda" to "cpu". Only "cpu" is available on my Mac Studio.
    DEVICE_INDEX = "0"
    ALIGN_MODEL = "WAV2VEC2_ASR_LARGE_LV60K_960H"
    BATCH_SIZE = "16"
    COMPUTE_TYPE = "int8"
    MAX_LINE_WIDTH = "45"
    MAX_LINE_COUNT = "1"
    TASK = "transcribe"
    INTERPOLATE_METHOD = "nearest"
    # NO_ALIGN = "False"
    # RETURN_CHAR_ALIGNMENTS = "False"
    VAD_METHOD = "pyannote" # or "silero" / # pyannote provides robust, precise segmentation for challenging audio (at higher computational cost) while silero is lighter and faster but may be less accurate in complex scenarios.
    VAD_ONSET = "0.500"
    VAD_OFFSET = "0.363"
    CHUNK_SIZE = "30"
    # DIARIZE = "False"
    # MIN_SPEAKERS = None
    # MAX_SPEAKERS = None
    TEMPERATURE = "0"
    BEST_OF = "5"
    BEAM_SIZE = "5"
    PATIENCE = "1.0"
    LENGTH_PENALTY = "1.0"
    SUPPRESS_TOKENS = "-1"
    SUPPRESS_NUMERALS = "False"
    # INITIAL_PROMPT = None
    # CONDITION_ON_PREVIOUS_TEXT = "False"
    # FP16 = "True"
    TEMPERATURE_INCREMENT_ON_FALLBACK = "0.2"
    COMPRESSION_RATIO_THRESHOLD = "2.4"
    LOGPROB_THRESHOLD = "-1.0"
    NO_SPEECH_THRESHOLD = "0.6"
    # HIGHLIGHT_WORDS = "False"
    SEGMENT_RESOLUTION = "chunk"
    THREADS = "8"
    # HF_TOKEN = None
    OUTPUT_FORMAT = "json" # "all" or "json" or "srt" / Output json-only and do post-processing to create a new .srt file with a more reasonable number of words per segment. Or output all formats to get also the clean .txt and delete unneeded files in post-processing.
    PRINT_PROGRESS = "False"
    

    if language is None:
        cmd = [
            "whisperx",
            mp4_path,
            "--verbose", VERBOSE,
            "--model", MODEL,
            "--device", DEVICE,
            "--device_index", DEVICE_INDEX,
            # "--align_model", ALIGN_MODEL, # 250329-1534 removing to try to fix the overlapping segments issue
            "--batch_size", BATCH_SIZE,
            "--compute_type", COMPUTE_TYPE,
            "--max_line_width", MAX_LINE_WIDTH,
            "--max_line_count", MAX_LINE_COUNT,
            # "--language", LANGUAGE,
            "--task", TASK,
            # "--interpolate_method", INTERPOLATE_METHOD, # 250329-1534 removing to try to fix the overlapping segments issue
            # "--no_align", NO_ALIGN,
            # "--return_char_alignments", RETURN_CHAR_ALIGNMENTS,
            # "--vad_method", VAD_METHOD, # 250329-1534 removing to try to fix the overlapping segments issue
            # "--vad_onset", VAD_ONSET, # 250329-1534 removing to try to fix the overlapping segments issue
            # "--vad_offset", VAD_OFFSET, # 250329-1534 removing to try to fix the overlapping segments issue
            # "--chunk_size", CHUNK_SIZE, # 250329-1534 removing to try to fix the overlapping segments issue
            # "--diarize", DIARIZE,
            # "--min_speakers", MIN_SPEAKERS,
            # "--max_speakers", MAX_SPEAKERS,
            # "--temperature", TEMPERATURE,
            # "--best_of", BEST_OF,
            # "--beam_size", BEAM_SIZE,
            # "--patience", PATIENCE,
            # "--length_penalty", LENGTH_PENALTY,
            # "--suppress_tokens", SUPPRESS_TOKENS,
            # "--initial_prompt", INITIAL_PROMPT,
            # "--condition_on_previous_text", CONDITION_ON_PREVIOUS_TEXT,
            # "--fp16", FP16,
            # "--temperature_increment_on_fallback", TEMPERATURE_INCREMENT_ON_FALLBACK,
            # "--compression_ratio_threshold", COMPRESSION_RATIO_THRESHOLD,
            # "--logprob_threshold", LOGPROB_THRESHOLD,
            # "--no_speech_threshold", NO_SPEECH_THRESHOLD,
            # "--highlight_words", HIGHLIGHT_WORDS,
            # "--segment_resolution", SEGMENT_RESOLUTION,
            # "--threads", THREADS,
            # "--hf_token", HF_TOKEN,
            # "--print_progress", PRINT_PROGRESS,
            "--output_dir", output_dir,
            "--output_format", OUTPUT_FORMAT
        ]
    else:
        cmd = [
            "whisperx",
            mp4_path,
            "--verbose", VERBOSE,
            "--model", MODEL,
            "--device", DEVICE,
            "--device_index", DEVICE_INDEX,
            "--batch_size", BATCH_SIZE,
            "--compute_type", COMPUTE_TYPE,
            "--max_line_width", MAX_LINE_WIDTH,
            "--max_line_count", MAX_LINE_COUNT,
            "--language", language,
            "--task", TASK,
            "--output_dir", output_dir,
            "--output_format", OUTPUT_FORMAT
        ]

    # Add boolean flags without values
    # if MODEL_CACHE_ONLY.lower() == "true":
    #     cmd.append("--model_cache_only")
    # if VERBOSE.lower() == "true":
    #     cmd.append("--verbose")
    # if SUPPRESS_NUMERALS.lower() == "true":
    #     cmd.append("--suppress_numerals")
    
    # print(f"\n🔊 Generating 🇬🇧 English SRT for: {os.path.basename(mp4_path)}\n")
    subprocess.run(cmd, check=True)
    
    # Determine the output SRT path
    base_name = os.path.basename(mp4_path).rsplit(".", 1)[0]
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    json_path = os.path.join(output_dir, f"{base_name}.json")

    print(f"\n✅ Generated JSON file: {json_path}")

    # Post-processing to create a new .srt file with a more reasonable number of words per segment using the json output from whisperx
    with open(json_path, "r") as f:
        data = json.load(f)

        # data["segments"] has a list of segments, each with "words" that have individual timestamps.
        new_segments = []
        max_words_per_segment = 10

        for seg in data["segments"]:
            words = seg["words"]
            current_chunk = []
            for word_info in words:
                # Skip words without timestamp data
                if "start" not in word_info or "end" not in word_info:
                    continue
                current_chunk.append(word_info)
                if len(current_chunk) >= max_words_per_segment:
                    # finalize chunk
                    start_ts = current_chunk[0]["start"]
                    end_ts = current_chunk[-1]["end"]
                    text = " ".join([w["word"] for w in current_chunk])
                    new_segments.append((start_ts, end_ts, text))
                    current_chunk = []

            # leftover words in this segment
            if current_chunk:
                start_ts = current_chunk[0]["start"]
                end_ts = current_chunk[-1]["end"]
                text = " ".join([w["word"] for w in current_chunk])
                new_segments.append((start_ts, end_ts, text))

        # now write new_segments to SRT format:
        def srt_time(sec):
            """Convert float seconds to SRT time format (HH:MM:SS,mmm)"""
            hours = int(sec // 3600)
            minutes = int((sec % 3600) // 60)
            seconds = int(sec % 60)
            milliseconds = int((sec * 1000) % 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

        with open(srt_path, "w") as srt:
            for i, (start, end, text) in enumerate(new_segments, start=1):
                srt.write(f"{i}\n")
                srt.write(f"{srt_time(start)} --> {srt_time(end)}\n")
                srt.write(text.strip() + "\n\n")
        
        print(f"\n✅ Generated SRT file: {srt_path}")


    # Create a clean .txt version of the SRT file
    if language is None:
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
    else:
        txt_path = os.path.join(output_dir, f"{base_name}_{language}.txt")
    
    try:
        with open(srt_path, "r") as srt_file, open(txt_path, "w") as txt_file:
            for line in srt_file:
                line = line.strip()
                # Skip empty lines, lines with timestamps (containing '-->'), and lines starting with digits (subtitle numbers)
                if line and not line.startswith(tuple('0123456789')) and '-->' not in line:
                    txt_file.write(line + "\n")
        # Remove trailing newline if the last line is empty
        with open(txt_path, "r") as f:
            content = f.read()
        if content.endswith("\n"):
            with open(txt_path, "w") as f:
                f.write(content.rstrip("\n"))
        
        print(f"\n✅ Generated clean TXT file: {txt_path}")

        # Copy txt_path to clipboard
        try:
            process = subprocess.Popen("pbcopy", universal_newlines=True, stdin=subprocess.PIPE)
            process.communicate(txt_path)
            print(f"\nℹ️  Copied TXT path to clipboard: {txt_path}")
        except Exception as e:
            print(f"❌ Error copying to clipboard: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error creating TXT file: {str(e)}")



    # Delete the .tsv and .vtt files created in the same folder
    base_path = os.path.join(output_dir, base_name)
    tsv_path = f"{base_path}.tsv"
    vtt_path = f"{base_path}.vtt"
    
    if os.path.exists(tsv_path):
        try:
            os.remove(tsv_path)
            # print(f"🗑️ Deleted TSV file: {tsv_path}")
        except Exception as e:
            print(f"❌ Error deleting TSV file: {str(e)}")
    
    if os.path.exists(vtt_path):
        try:
            os.remove(vtt_path)
            # print(f"🗑️ Deleted VTT file: {vtt_path}")
        except Exception as e:
            print(f"❌ Error deleting VTT file: {str(e)}")

    return srt_path









if __name__ == "__main__":

    # Start Chrono
    import time
    start_time = time.time()
    import os

    # test_file = "/Users/nic/dl/yt/test/test.mp4"

    # print(f"\n🔊 Generating 🇬🇧 English SRT for: {test_file}\n")

    # generate_srt(test_file, source_lang="EN", output_lang="EN", model_name="large-v2")

    generate_en_srt("/path/to/your/audio.mp3", language="fr")

    # End Chrono
    run_time = round((time.time() - start_time), 3)
    minutes = int(run_time // 60)
    seconds = int(run_time % 60)
    print(f'\n{os.path.basename(__file__)} finished in {minutes}m{seconds}s.\n')