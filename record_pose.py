import cv2
import mediapipe as mp
import json
import os

cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose.Pose(model_complexity=0)
recorded_poses = {}
count = 0

print("=== ЗАПУСК РЕКОРДЕРА FLEXIN ===")
print("ИНСТРУКЦИЯ: 1. Переключи язык на ENG. 2. Нажми 'S' для записи. 3. Нажми 'Q' для выхода.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    results = mp_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.pose_landmarks:
        # Рисуем обычный скелет, чтобы ты видел, что нейронка тебя узнала
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

    cv2.putText(frame, f"Steps recorded: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('RECORD MODE', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        if results.pose_landmarks:
            # Вытягиваем координаты
            points = [{'x': l.x, 'y': l.y, 'z': l.z} for l in results.pose_landmarks.landmark]
            recorded_poses[str(count)] = points
            print(f">>> ПОЗА {count} ЗАПИСАНА В ПАМЯТЬ!")
            count += 1
        else:
            print("!!! ОШИБКА: MediaPipe не видит тебя в кадре. Встань подальше!")

    elif key == ord('q'):
        print("=== СОХРАНЕНИЕ И ВЫХОД ===")
        break

# Записываем в файл
with open('dance_cor.json', 'w') as f:
    json.dump(recorded_poses, f, indent=4)  # indent сделает JSON красивым и читаемым

print(f"УСПЕХ! Файл dance_cor.json создан. Записано поз: {len(recorded_poses)}")
cap.release()
cv2.destroyAllWindows()