import cv2
import time
import config as cfg
from vision import DanceVision


def main():
    # Инициализация
    vision = DanceVision()
    cap = cv2.VideoCapture(0)

    # Состояние игры
    track_index = 0
    total_score = 0
    streak = 0
    start_time = time.time()
    scored_this_round = False
    status = "READY?"
    msg_color = cfg.COLOR_READY

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        results = vision.process_frame(frame)
        elapsed_time = time.time() - start_time

        # 1. Логика таймера (смена кадра)
        if elapsed_time > cfg.HOLD_TIME:
            track_index = (track_index + 1) % len(cfg.DANCE_TRACK)
            start_time = time.time()
            scored_this_round = False

        target_angle = cfg.DANCE_TRACK[track_index]

        # 2. Обработка движений
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Проверяем видимость правого локтя (id 14)
            if lm[14].visibility > 0.5:
                # Координаты суставов
                shoulder = [lm[12].x, lm[12].y]
                elbow = [lm[14].x, lm[14].y]
                wrist = [lm[16].x, lm[16].y]

                current_angle = vision.calculate_angle(shoulder, elbow, wrist)
                error = abs(current_angle - target_angle)

                # 3. Логика HIT / MISS (проверка попадания в окно)
                if cfg.HIT_WINDOW_START < elapsed_time < cfg.HIT_WINDOW_END and not scored_this_round:
                    if error < cfg.ANGLE_THRESHOLD:
                        total_score += 100 + (streak * 10)
                        streak += 1
                        status = "PERFECT HIT!"
                        msg_color = cfg.COLOR_PERFECT
                    else:
                        streak = 0
                        status = "MISS!"
                        msg_color = cfg.COLOR_MISS
                    scored_this_round = True

                # Статусы вне окна попадания
                elif not scored_this_round:
                    status = f"GET READY: {target_angle}"
                    msg_color = cfg.COLOR_READY
                elif elapsed_time >= cfg.HIT_WINDOW_END:
                    status = "WAIT FOR NEXT..."
                    msg_color = cfg.COLOR_WAIT

                # 4. Отрисовка скелета
                vision.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, vision.mp_pose.POSE_CONNECTIONS
                )

        # 5. Интерфейс (UI)
        # Плашка сверху
        cv2.rectangle(frame, (0, 0), (w, 100), cfg.COLOR_UI_BG, -1)
        cv2.putText(frame, status, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, msg_color, 3)
        cv2.putText(frame, f"SCORE: {total_score} | STREAK: {streak}", (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Прогресс-бар (внизу плашки)
        bar_color = cfg.COLOR_WAIT if elapsed_time < cfg.HIT_WINDOW_START else cfg.COLOR_PERFECT
        progress_w = int((elapsed_time / cfg.HOLD_TIME) * w)
        cv2.line(frame, (0, 95), (progress_w, 95), bar_color, 10)

        cv2.imshow('Dance AI - Modular Edition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()