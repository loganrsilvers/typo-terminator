import random
from pathlib import Path


class WordBank:
    def __init__(self, word_bank_file):
        try:
            text = Path(word_bank_file).read_text(encoding="utf-8")
            all_words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]
            # Filter out words shorter than 4 letters — they often can't be meaningfully scrambled
            self.words = [w for w in all_words if len(w) >= 4]
        except Exception as e:
            print(f"Error loading wordbank: {e}")
            self.words = ["programming", "backend", "database", "interface", "columbia", "chicago", "wrestling", "software"]

    def scramble(self, word):
        """
        Shuffle the letters of a word without adding or removing any.
        Guarantees the scrambled result differs from the original.
        Falls back gracefully if the word cannot be scrambled (e.g. 'aaaa').
        """
        letters = list(word)
        for _ in range(200):
            random.shuffle(letters)
            candidate = "".join(letters)
            if candidate != word:
                return candidate
        return "".join(letters)  # fallback: return as-is if all shuffles match original

    def get_challenge(self):
        """Return (original_word, scrambled_word) from the word bank."""
        word = random.choice(self.words)
        scrambled = self.scramble(word)
        return word, scrambled
