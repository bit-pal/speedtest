#!/usr/bin/env python3
import argparse
import sys
import time
import urllib.request

DEFAULT_URL = "https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg"
CHUNK_SIZE = 64 * 1024
USER_AGENT = "speedtest-script/1.0"


def download(url: str, timeout: float) -> tuple[int, float]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"},
    )
    start = time.perf_counter()
    size = 0
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            size += len(chunk)
    return size, time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания по URL.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="адрес тяжёлого файла (картинки)")
    parser.add_argument("-n", "--requests", type=int, default=10, help="число запросов (по умолчанию 10)")
    parser.add_argument("-t", "--timeout", type=float, default=60, help="таймаут запроса, сек (по умолчанию 60)")
    args = parser.parse_args()

    if args.requests < 1:
        parser.error("число запросов должно быть >= 1")

    print(f"URL: {args.url}")
    print(f"Запросов: {args.requests}\n")

    sizes, durations = [], []
    for i in range(1, args.requests + 1):
        try:
            size, duration = download(args.url, args.timeout)
        except Exception as exc:  # сеть, HTTP-ошибки, таймауты
            print(f"[{i:>2}/{args.requests}] ошибка: {exc}")
            continue
        sizes.append(size)
        durations.append(duration)
        speed = size / duration / 1_000_000 if duration else 0
        print(f"[{i:>2}/{args.requests}] {size / 1_000_000:8.2f} МБ за {duration:6.3f} с  ->  {speed:7.2f} МБ/с")

    if not sizes:
        print("\nНи один запрос не завершился успешно.")
        return 1

    total_bytes = sum(sizes)
    total_time = sum(durations)
    avg_time = total_time / len(durations)
    speed_mb_s = total_bytes / total_time / 1_000_000

    print("\n" + "=" * 50)
    print(f"Успешных запросов:     {len(sizes)} из {args.requests}")
    print(f"Среднее время запроса: {avg_time:.3f} с")
    print(f"Скачано всего:         {total_bytes / 1_000_000:.2f} МБ ({total_bytes} байт)")
    print(f"Скорость:              {speed_mb_s:.2f} МБ/с ({speed_mb_s * 8:.2f} Мбит/с)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
