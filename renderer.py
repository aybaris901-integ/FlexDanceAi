import cv2
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2


class GhostRenderer:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        # Задаем стиль для призрака (полупрозрачный, золотой)
        self.ghost_spec = self.mp_drawing.DrawingSpec(
            color=(0, 215, 255),  # Gold
            thickness=2,
            circle_radius=1
        )

    def draw_ghost(self, frame, ghost_landmarks):
        """
        Накладывает скелет призрака на кадр.
        ghost_landmarks: Список словарей [{'x':..., 'y':..., 'z':...}, ...]
        """
        # Создаем пустой список ориентиров в формате MediaPipe
        proto_landmarks = landmark_pb2.NormalizedLandmarkList()
        for lm in ghost_landmarks:
            # Добавляем каждую точку из вашего JSON/списка в объект MediaPipe
            proto_landmarks.landmark.add(x=lm['x'], y=lm['y'], z=lm['z'])

        # Рисуем скелет поверх кадра
        self.mp_drawing.draw_landmarks(
            frame,
            proto_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.ghost_spec,
            connection_drawing_spec=self.ghost_spec
        )
        return frame