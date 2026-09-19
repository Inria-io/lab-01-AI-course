"""Task 2 -- locate the Kazakh premium: same length, different letters."""

import tiktoken
from texts import KK_SHARED_LETTERS, KK_SPECIAL_LETTERS

texts = {
    "shared_letters": KK_SHARED_LETTERS["kk"],
    "special_letters": KK_SPECIAL_LETTERS["kk"],
}

print("TASK 2 -- Kazakh premium (shared vs special letters)")
print("-" * 60)

for name, text in texts.items():
    chars = len(text)
    nbytes = len(text.encode("utf-8"))
    print(f"\n{name}: \"{text}\"")
    print(f"  chars={chars}  bytes={nbytes}  bytes/char={nbytes/chars:.2f}")
    for enc_name in ("o200k_base", "cl100k_base"):
        enc = tiktoken.get_encoding(enc_name)
        n_tokens = len(enc.encode(text))
        print(f"  {enc_name}: {n_tokens} tokens")