import cv2
import numpy as np

def frame_score(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)
    return sharpness * (0.5 + brightness / 255)  # weighted combo

def extract_best_thumbnail(video_path, fractions=[0.25, 0.5, 0.75]):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    best_score = -1
    best_frame = None

    for f in fractions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total_frames * f))
        success, frame = cap.read()
        if success:
            score = frame_score(frame)
            if score > best_score:
                best_score = score
                best_frame = frame

    cap.release()
    if best_frame is not None:
        output_path = video_path.rsplit(".", 1)[0] + ".jpg"
        cv2.imwrite(output_path, best_frame)
        print(f"\n✅ Thumbnail saved to: {output_path}\n")

if __name__ == "__main__":

    extract_best_thumbnail("/Users/nic/dl/yt/test/test.mp4")