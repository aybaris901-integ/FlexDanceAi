import time
from config import DANCE_TRACK, HOLD_TIME, TARGET_ERROR_MARGIN


class GameLogic:
    def __init__(self):
        self.track_index = 0
        self.total_score = 0
        self.streak = 0
        self.start_time = time.time()
        self.scored_this_round = False

    def update(self, current_angle):
        elapsed_time = time.time() - self.start_time
        target_angle = DANCE_TRACK[self.track_index]

        # Сброс таймера для нового движения
        if elapsed_time > HOLD_TIME:
            self.track_index = (self.track_index + 1) % len(DANCE_TRACK)
            self.start_time = time.time()
            self.scored_this_round = False
            return "NEXT", (255, 255, 255)

        # Проверка попадания в тайминг (2.2 - 2.8 сек)
        if 2.2 < elapsed_time < 2.8 and not self.scored_this_round:
            error = abs(current_angle - target_angle)
            if error < TARGET_ERROR_MARGIN:
                self.total_score += 100 + (self.streak * 10)
                self.streak += 1
                self.scored_this_round = True
                return "PERFECT HIT!", (0, 255, 0)
            else:
                self.streak = 0
                self.scored_this_round = True
                return "MISS!", (0, 0, 255)

        return f"GET READY: {target_angle}", (255, 255, 255)