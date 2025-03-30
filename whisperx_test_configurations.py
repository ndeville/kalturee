# Start Chrono
import time
import cv2

import os
import subprocess


# input_path = "/Users/nic/dl/yt/pharma-demo/Mayo Clinic Q&A podcast： A vaccine milestone.mp4"
input_path = "/Users/nic/dl/yt/test/test.mp4"


# FUNCTIONS

def get_video_duration(video_path):
    """Get the duration of a video file in seconds."""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        cap.release()
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0
    


duration = get_video_duration(input_path)
duration_minutes = int(duration // 60)
duration_seconds = int(duration % 60)
print(f"\n\n=============== ℹ️  processing {duration_minutes}m {duration_seconds}s video.\n")


output_dir = os.path.dirname(input_path)

start_time = time.time()

# WhisperX Configuration
MODEL = "turbo"
MODEL_CACHE_ONLY = "False"
MODEL_DIR = None
DEVICE = "cpu"  # Changed from "cuda" to "cpu". Only "cpu" is available on my Mac Studio.
DEVICE_INDEX = "0"
ALIGN_MODEL = "WAV2VEC2_ASR_LARGE_LV60K_960H"
BATCH_SIZE = "16"
COMPUTE_TYPE = "int8"
MAX_LINE_WIDTH = "40"
MAX_LINE_COUNT = "1"
LANGUAGE = "en"
TASK = "transcribe"
VERBOSE = "True"
INTERPOLATE_METHOD = "nearest"
NO_ALIGN = "False"
RETURN_CHAR_ALIGNMENTS = "False"
VAD_METHOD = "silero" # or "silero" / # pyannote provides robust, precise segmentation for challenging audio (at higher computational cost) while silero is lighter and faster but may be less accurate in complex scenarios.
VAD_ONSET = "0.500"
VAD_OFFSET = "0.363"
CHUNK_SIZE = "30"
DIARIZE = "False"
MIN_SPEAKERS = None
MAX_SPEAKERS = None
TEMPERATURE = "0"
BEST_OF = "5"
BEAM_SIZE = "5"
PATIENCE = "1.0"
LENGTH_PENALTY = "1.0"
SUPPRESS_TOKENS = "-1"
SUPPRESS_NUMERALS = "False"
INITIAL_PROMPT = None
CONDITION_ON_PREVIOUS_TEXT = "False"
FP16 = "True"
TEMPERATURE_INCREMENT_ON_FALLBACK = "0.2"
COMPRESSION_RATIO_THRESHOLD = "2.4"
LOGPROB_THRESHOLD = "-1.0"
NO_SPEECH_THRESHOLD = "0.6"
HIGHLIGHT_WORDS = "False"
SEGMENT_RESOLUTION = "sentence"
THREADS = "8"
HF_TOKEN = None
PRINT_PROGRESS = "True"
OUTPUT_FORMAT = "all"

cmd = [
    "whisperx",
    input_path,
    "--model", MODEL,
    "--model_cache_only", MODEL_CACHE_ONLY,
    "--device", DEVICE,
    "--device_index", DEVICE_INDEX,
    "--align_model", ALIGN_MODEL,
    "--batch_size", BATCH_SIZE,
    "--compute_type", COMPUTE_TYPE,
    "--max_line_width", MAX_LINE_WIDTH,
    "--max_line_count", MAX_LINE_COUNT,
    "--language", LANGUAGE,
    "--task", TASK,
    "--verbose", VERBOSE,
    "--interpolate_method", INTERPOLATE_METHOD,
    "--vad_method", VAD_METHOD,
    "--vad_onset", VAD_ONSET,
    "--vad_offset", VAD_OFFSET,
    "--chunk_size", CHUNK_SIZE,
    "--temperature", TEMPERATURE,
    "--best_of", BEST_OF,
    "--beam_size", BEAM_SIZE,
    "--patience", PATIENCE,
    "--length_penalty", LENGTH_PENALTY,
    "--suppress_tokens", SUPPRESS_TOKENS,
    "--temperature_increment_on_fallback", TEMPERATURE_INCREMENT_ON_FALLBACK,
    "--compression_ratio_threshold", COMPRESSION_RATIO_THRESHOLD,
    "--logprob_threshold", LOGPROB_THRESHOLD,
    "--no_speech_threshold", NO_SPEECH_THRESHOLD,
    "--segment_resolution", SEGMENT_RESOLUTION,
    "--threads", THREADS,
    "--print_progress", PRINT_PROGRESS,
    "--output_dir", output_dir,
    "--output_format", OUTPUT_FORMAT,
    
    # # 250328-2326 MORE TESTST TO TRY
    # "--vad_filter", "True",      # Voice activity detection to better segment speech
    # "--min_speech_duration_ms", "250",  # Minimum speech segment duration
    # "--max_speech_duration_s", "5",     # Maximum speech segment duration

    # TEST ALSO:
    # "--length_penalty", "1.2", # TEST OUTPUT LENGTH
]

subprocess.run(cmd, check=True)



# End Chrono
run_time = round((time.time() - start_time), 3)
run_time_minutes = int(run_time // 60)
run_time_seconds = int(run_time % 60)
conversion_ratio = round(duration / run_time, 2)
print(f'\n{duration_minutes}m{duration_seconds}s converted in {run_time_minutes}m{run_time_seconds}s (ratio: {conversion_ratio}x).\n')

# Print configuration summary
print(f"{conversion_ratio}x ({duration_minutes}m{duration_seconds}s converted in {run_time_minutes}m{run_time_seconds}s) with model: {MODEL}, align_model: {ALIGN_MODEL}, batch_size: {BATCH_SIZE} threads: {THREADS} compute_type: {COMPUTE_TYPE} language: {LANGUAGE}\n")
# print(f"{conversion_ratio}x ({duration_minutes}m {duration_seconds}s converted in {run_time_minutes}m {run_time_seconds}s) with model: {MODEL}, align_model: {ALIGN_MODEL}, batch_size: {BATCH_SIZE} threads: {THREADS} compute_type: {COMPUTE_TYPE}")
