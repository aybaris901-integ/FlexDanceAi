print("--- СТАРТ ЗАПУСКА ---")
import cv2
import mediapipe as mp
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
# Импортируем твою логику (проверь, как называется функция в твоем vision_engine)
from vision_engine import run_game_logic


app = FastAPI()
# Захват камеры
cap = cv2.VideoCapture(0)

# Инициализация MediaPipe (если она нужна здесь, а не внутри run_game_logic)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # ВЫЗОВ ТВОЕЙ ЛОГИКИ
        # Твой движок обрабатывает кадр и возвращает его уже с отрисовкой
        processed_frame = run_game_logic(frame, pose)

        # Кодируем в JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get('/')
def index():
    return {"message": "Сервер FlexDanceAi запущен! Перейди на /video"}


@app.get('/video')
def video_feed():
    # Эта штука создает поток видео для браузера
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # host="0.0.0.0" позволяет зайти с Dell 7480
    print("--- СЕРВЕР ПОЧТИ ГОТОВ ---")
    uvicorn.run(app, host="0.0.0.0", port=8000)