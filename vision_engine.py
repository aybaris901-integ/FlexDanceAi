"""
Vision Engine v1.0
Core module for skeletal tracking and movement analysis using MediaPipe & OpenCV.
Developed for FlexIn / Dance AI.
"""

from renderer import GhostRenderer
import json
import numpy as np
import cv2
import mediapipe as mp
import cv2
import mediapipe as mp
import time

# load ghost first level
ghost_ui = GhostRenderer()

try:
    with open('dance_cor.json', 'r') as f:
        ghost_data = json.load(f)
    print("Данные призрака загружены успешно!")
except FileNotFoundError:
    ghost_data = {}
    print("Файл dance_cor.json не найден. Призрак будет скрыт.")
except Exception as e:
    ghost_data = {}
    print(f"Ошибка при загрузке JSON: {e}")


class DanceVision:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(model_complexity=0)
        self.mp_drawing = mp.solutions.drawing_utils
        # Переменные состояния игры
        self.dance_track = [90, 160, 45, 180, 30]
        self.track_index = 0
        self.total_score = 0
        self.streak = 0
        self.start_time = time.time()
        self.HOLD_TIME = 3.0
        self.scored_this_round = False

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba, bc = a - b, c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
        return int(angle)

#
vision = DanceVision()
#  Manually create a ghost if the JSON is empty
if not ghost_data:
    print("ВНИМАНИЕ: Создаю тестового призрака (две точки), чтобы проверить рендерер!")
    # We create one pose (index 0) where the arm just hangs
    test_pose = []
    for i in range(33): # MediaPipe нужно ровно 33 точки
        test_pose.append({'x': 0.5, 'y': 0.5 + (i * 0.01), 'z': 0})
    ghost_data["0"] = test_pose
def run_game_logic(frame):
    global ghost_data
    print(f"DEBUG: Шаг {vision.track_index} | В базе есть: {list(ghost_data.keys())}")
    h, w, _ = frame.shape
    frame = cv2.flip(frame, 1) # Отзеркаливаем видео

    # 1. DRAWING A GHOST (Golden Silhouette)
    # Search for a pose in JSON by the current step index
    current_step_name = str(vision.track_index)
    if current_step_name in ghost_data:
        # drawing ghost first
        frame = ghost_ui.draw_ghost(frame, ghost_data[current_step_name])

    #Drawing your skeleton
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = vision.pose.process(rgb_frame)
    elapsed_time = time.time() - vision.start_time

    # Position change timer
    if elapsed_time > vision.HOLD_TIME:
        vision.track_index = (vision.track_index + 1) % len(vision.dance_track)
        vision.start_time = time.time()
        vision.scored_this_round = False

    target_angle = vision.dance_track[vision.track_index]
    status = f"GET READY: {target_angle}"
    msg_color = (255, 255, 255)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        # Checking the right elbow
        if lm[14].visibility > 0.5:
            shoulder = [lm[12].x, lm[12].y]
            elbow = [lm[14].x, lm[14].y]
            wrist = [lm[16].x, lm[16].y]

            current_angle = vision.calculate_angle(shoulder, elbow, wrist)
            error = abs(current_angle - target_angle)

            # Logic HIT / MISS
            if 2.2 < elapsed_time < 2.8 and not vision.scored_this_round:
                if error < 25:
                    vision.total_score += 100 + (vision.streak * 10)
                    vision.streak += 1
                    vision.scored_this_round = True
                    status = "PERFECT HIT!"
                    msg_color = (0, 255, 0)
                else:
                    vision.streak = 0
                    vision.scored_this_round = True
                    status = "MISS!"
                    msg_color = (0, 0, 255)
            elif vision.scored_this_round:
                status = "WAIT FOR NEXT..."
                msg_color = (0, 255, 255)

        # Draw your current skeleton over the ghost
        vision.mp_drawing.draw_landmarks(frame, results.pose_landmarks, vision.mp_pose.POSE_CONNECTIONS)

    # 3. interface
    cv2.rectangle(frame, (0, 0), (w, 100), (20, 20, 20), -1)
    cv2.putText(frame, status, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, msg_color, 3)
    cv2.putText(frame, f"SCORE: {vision.total_score} | STREAK: {vision.streak}", (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    # progress bar
    bar_color = (0, 255, 255) if elapsed_time < 2.2 else (0, 255, 0)
    progress_w = int((elapsed_time / vision.HOLD_TIME) * w)
    cv2.line(frame, (0, 95), (progress_w, 95), bar_color, 10)

    return frame

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("Load the game, press 'q' to exit..")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = run_game_logic(frame)

        cv2.imshow('Dance AI', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()