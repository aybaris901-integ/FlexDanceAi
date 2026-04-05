import cv2
import mediapipe as mp
import numpy as np


# Start mediapipe self = new function
class DanceVision():
    def __init__(self):
        self.perfect_pose = None
        self.mp_pose = mp.solutions.pose
        # very easy mode (0)
        self.pose = self.mp_pose.Pose(model_complexity=0)
        # skeleton vektors and landmarks
        self.mp_drawing = mp.solutions.drawing_utils

    def process(self, frame, save_now=False):
        # opencv color bgr mediapipe color rgb and this block they are s connect
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # save results
        results = self.pose.process(img_rgb)

        if results.pose_landmarks:

            s = [results.pose_landmarks.landmark[11].x, results.pose_landmarks.landmark[11].y]
            e = [results.pose_landmarks.landmark[13].x, results.pose_landmarks.landmark[13].y]
            w = [results.pose_landmarks.landmark[15].x, results.pose_landmarks.landmark[15].y]

            current_angle = self.calculate_angle(s, e, w)

            # Отрисовка стандартного скелета
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Если эталон уже есть — сравниваем
            if self.perfect_pose:
                h, w, _ = frame.shape
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    perf = self.perfect_pose.landmark[i]
                    return frame

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba, bc = a - b, c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
        return int(angle)


# --- ЗАПУСК ---
dv = DanceVision()
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    mirrored_frame = cv2.flip(frame, 1)

    key = cv2.waitKey(1) & 0xFF
    # Передаем кадр в обработку. Если нажата 's', метод обновит эталон.
    frame = dv.process(frame, save_now=(key == ord('s')))

    cv2.imshow("WELCOME", mirrored_frame)
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()

# tomorrow To complete the calculation on cosine and scalar, it is advisable to add 3 d