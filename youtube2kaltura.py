"""AUTOMATED YOUTUBE VIDEO DOWNLOAD & UPLOAD TO KALTURA KMS"""

""""
TODO:

"""

from datetime import datetime
import os
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Start Chrono
import time
start_time = time.time()

import ytdownload_videos
import kaltura_video_upload


youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe"


youtube_download_path_with_files = ytdownload_videos.process_youtube_url_to_download(youtube_url)


print(f"\n\n{youtube_download_path_with_files=}")


# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')