from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()
DB_TWITTER = os.getenv("DB_TWITTER")
DB_BTOB = os.getenv("DB_BTOB")
DB_MAILINGEE = os.getenv("DB_MAILINGEE")

import pprint
pp = pprint.PrettyPrinter(indent=4)

####################
# SCRIPT_TITLE

# IMPORTS (script-specific)

import my_utils
from DB.tools import select_all_records, update_record, create_record, delete_record

# GLOBALS

test = 1
verbose = 1

count_row = 0
count_total = 0
count = 0


# FUNCTIONS



# MAIN

from moviepy.editor import VideoFileClip, concatenate_videoclips
import math

def loop_video_to_duration(input_path, output_path, target_duration_hrs=1):
    # Load the video file
    clip = VideoFileClip(input_path)
    
    # Calculate the number of repetitions needed to reach the target duration
    repetitions = math.ceil((target_duration_hrs * 3600) / clip.duration)
    
    # Create a list of the clip repeated the necessary number of times
    clips = [clip] * repetitions
    
    # Concatenate the clips together
    final_clip = concatenate_videoclips(clips)
    
    # Cut the concatenated clip to the target duration
    final_clip = final_clip.subclip(0, target_duration_hrs * 3600)
    
    # Write the result to the output file path
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac') # 250129-0812 not losssless
    # final_clip.write_videofile(output_path, codec='libx264', preset='ultrafast', ffmpeg_params=['-crf', '0'], audio_codec='pcm_s16le') # lossless but 89GB for 1hr

# Example usage
input_path = '/Users/nic/test/test.mp4'
output_path = f"{input_path[:-4]}_LONG.mp4"
loop_video_to_duration(input_path, output_path)







########################################################################################################

if __name__ == '__main__':
    print('\n\n-------------------------------')
    print(f"\ncount_row:\t{count_row:,}")
    print(f"count_total:\t{count_total:,}")
    print(f"count:\t{count:,}")
    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')