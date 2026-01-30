import random
import time
from lru import LRUCache


# Функції без кешу
def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    array[index] = value


# Глобальний кеш
cache = LRUCache(1000)


# Функції з кешем
def range_sum_with_cache(array, left, right):
    key = (left, right)
    result = cache.get(key)

    if result == -1:
        result = sum(array[left : right + 1])
        cache.put(key, result)

    return result


def update_with_cache(array, index, value):
    array[index] = value

    # Інвалідація кешу: видаляємо всі діапазони, що містять index
    keys_to_remove = []
    for key in cache.cache.keys():
        left, right = key
        if left <= index <= right:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        node = cache.cache[key]
        cache.list.remove(node)
        del cache.cache[key]


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def create_report(time_no_cache, time_with_cache, n, q, cache_capacity=1000):
    speedup = time_no_cache / time_with_cache

    report = f"""# Оптимізація доступу до даних за допомогою LRU-кешу

## Параметри тестування

- **Розмір масиву (N):** {n:,}
- **Кількість запитів (Q):** {q:,}
- **Ємність кешу (K):** {cache_capacity}
- **Гарячих діапазонів:** 30
- **Ймовірність гарячого запиту:** 95%
- **Ймовірність Update:** 3%

## Результати виконання

| Режим | Час виконання | Прискорення |
|-------|---------------|-------------|
| Без кешу | {time_no_cache:.2f} с | - |
| З LRU-кешем | {time_with_cache:.2f} с | ×{speedup:.1f} |

## Висновки

**Прискорення:** ×{speedup:.1f}

LRU-кеш показав {"значне" if speedup > 2 else "помірне"} прискорення завдяки багаторазовому використанню "гарячих" діапазонів. 
{"Кеш ефективно зберігає результати популярних запитів, зменшуючи кількість обчислень." if speedup > 2 else "Ефективність кешу обмежена частими оновленнями масиву."}
"""

    with open("task_1/lru_cache_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nЗвіт збережено у файл: lru_cache_report.md")


def main():
    N = 100_000
    Q = 50_000

    array_no_cache = [random.randint(1, 100) for _ in range(N)]
    array_with_cache = array_no_cache.copy()
    queries = make_queries(N, Q)

    # Тест без кешу
    start = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array_no_cache, query[1], query[2])
        else:
            update_no_cache(array_no_cache, query[1], query[2])
    time_no_cache = time.time() - start

    # Тест з кешем
    start = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(array_with_cache, query[1], query[2])
        else:
            update_with_cache(array_with_cache, query[1], query[2])
    time_with_cache = time.time() - start

    # Створення звіту
    create_report(time_no_cache, time_with_cache, N, Q)


if __name__ == "__main__":
    main()
