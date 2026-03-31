import cv2
import mediapipe as mp

# Start mediapipe self = new function
class DanceVision():
    def __init__(self):
        self.perfect_pose = None
        self.mp_pose = mp.solutions.pose
        # very easy mode (0)
        self.pose = self.mp_pose.Pose(model_complexity=0)
        #skeleton vektors and landmarks
        self.mp_drawing = mp.solutions.drawing_utils

    def process(self, frame, save_now=False):
    #opencv color bgr mediapipe color rgb and this block they are s connect
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #save results
        results = self.pose.process(img_rgb)

        if results.pose_landmarks:
            # Если нажали 'S', сохраняем текущие точки как эталон
            if save_now:
                self.perfect_pose = results.pose_landmarks

            # Отрисовка стандартного скелета
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Если эталон уже есть — сравниваем
            if self.perfect_pose:
                h, w, _ = frame.shape
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    perf = self.perfect_pose.landmark[i]

                    # Считаем расстояние (правильно x-x, y-y)
                    dist = ((landmark.x - perf.x) ** 2 + (landmark.y - perf.y) ** 2) ** 0.5

                    color = (0, 255, 0) if dist < 0.05 else (0, 0, 255)
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (cx, cy), 5, color, -1)
        return frame


# --- ЗАПУСК ---
dv = DanceVision()
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    key = cv2.waitKey(1) & 0xFF
    # Передаем кадр в обработку. Если нажата 's', метод обновит эталон.
    frame = dv.process(frame, save_now=(key == ord('s')))

    cv2.imshow("WELCOME", frame)
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()