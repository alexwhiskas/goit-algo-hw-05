import chardet

# # detect file encoding
# with open("text_1.txt", "rb") as f:
#     raw_data = f.read(6000)
#     result = chardet.detect(raw_data)
#     print(result)

# exit()

import timeit
import statistics

# --- Алгоритми пошуку --- #
def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return -1
    lps = [0] * m
    j = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
            i += 1
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                lps[i] = 0
                i += 1
    i = j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            return i - j
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1


def rabin_karp_search(text, pattern, q=101):
    d = 256
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return -1
    p = t = 0
    h = 1
    for i in range(m - 1):
        h = (h * d) % q
    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q
    for i in range(n - m + 1):
        if p == t and text[i:i + m] == pattern:
            return i
        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            if t < 0:
                t += q
    return -1


def boyer_moore_search(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return -1
    bad_char = {ch: i for i, ch in enumerate(pattern)}
    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return s
        s += max(1, j - bad_char.get(text[s + j], -1))
    return -1


# --- Безпечне читання файлів --- #
def safe_read(filename):
    for enc in ("utf-8-sig", "cp1251", "utf-8", "iso-8859-1"):
        try:
            with open(filename, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Cannot decode {filename} with common encodings.")


text1 = safe_read("text_1.txt")
text2 = safe_read("text_2.txt")

patterns = {
    "text_1": ("алгоритм", "xyz123"),
    "text_2": ("система", "qwerty999"),
}


# --- Benchmark single run --- #
def benchmark(text, pattern, func):
    return timeit.timeit(lambda: func(text, pattern), number=1)


# --- Run multiple independent tests --- #
def run_tests(repeats=10):
    algorithms = [boyer_moore_search, kmp_search, rabin_karp_search]

    # wins per text, separately for existing and fake patterns
    wins_exist = {name: {f.__name__: 0 for f in algorithms} for name in patterns}
    wins_fake  = {name: {f.__name__: 0 for f in algorithms} for name in patterns}

    for name, (p_exist, p_fake) in patterns.items():
        text = text1 if name == "text_1" else text2
        print(f"\n=== {name} ===")

        for i in range(repeats):
            times_exist = {}
            times_fake = {}

            for func in algorithms:
                t_exist = benchmark(text, p_exist, func)
                t_fake  = benchmark(text, p_fake,  func)
                times_exist[func.__name__] = t_exist
                times_fake[func.__name__]  = t_fake

            best_exist = min(times_exist, key=times_exist.get)
            best_fake  = min(times_fake,  key=times_fake.get)

            wins_exist[name][best_exist] += 1
            wins_fake[name][best_fake]   += 1

            print(f"[{i+1}/{repeats}] найшвидші — {best_exist} (існуючий), {best_fake} (вигаданий)")

    return wins_exist, wins_fake, repeats


# --- Entry point --- #
if __name__ == "__main__":
    wins_exist, wins_fake, repeats = run_tests(repeats=10)

    print("\n=== ПІДСУМКОВА СТАТИСТИКА (по-текстово) ===")
    print(f"🔹 Кількість незалежних прогонів на текст: {repeats}")

    for name in patterns:
        print(f"\n— {name} —")
        print("📈 Перемоги при пошуку ІСНУЮЧОГО підрядка:")
        for algo, wins in wins_exist[name].items():
            print(f"{algo:20s}: {wins} перемог")
        best_exist_text = max(wins_exist[name], key=wins_exist[name].get)

        print("\n📉 Перемоги при пошуку ВИГАДАНОГО підрядка:")
        for algo, wins in wins_fake[name].items():
            print(f"{algo:20s}: {wins} перемог")
        best_fake_text = max(wins_fake[name], key=wins_fake[name].get)

        print("\n=== ВИСНОВОК (для цього тексту) ===")
        print(f"🔹 Найчастіше найшвидшим для існуючих підрядків був: {best_exist_text} ({wins_exist[name][best_exist_text]} з {repeats})")
        print(f"🔹 Найчастіше найшвидшим для вигаданих підрядків був: {best_fake_text} ({wins_fake[name][best_fake_text]} з {repeats})")
