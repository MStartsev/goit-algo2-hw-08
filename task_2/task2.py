import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Очищення застарілих запитів з вікна"""
        if user_id not in self.user_windows:
            return

        window = self.user_windows[user_id]
        cutoff_time = current_time - self.window_size

        # Видаляємо всі повідомлення старіші за window_size
        while window and window[0] <= cutoff_time:
            window.popleft()

        # Якщо вікно порожнє, видаляємо користувача
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Перевірка можливості відправлення повідомлення"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Перше повідомлення або вікно очищене
        if user_id not in self.user_windows:
            return True

        # Перевірка ліміту
        return len(self.user_windows[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """Запис нового повідомлення"""
        if not self.can_send_message(user_id):
            return False

        current_time = time.time()

        # Створюємо вікно для нового користувача
        if user_id not in self.user_windows:
            self.user_windows[user_id] = deque()

        self.user_windows[user_id].append(current_time)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        """Розрахунок часу очікування"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо можна відправити - 0
        if (
            user_id not in self.user_windows
            or len(self.user_windows[user_id]) < self.max_requests
        ):
            return 0.0

        # Час до видалення найстарішого повідомлення
        oldest_message = self.user_windows[user_id][0]
        wait_time = (oldest_message + self.window_size) - current_time

        return max(0.0, wait_time)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
