import random
import string
import numpy as np
import jellyfish
from pathlib import Path

class TypoGenerator:
    def __init__(self, word_bank_file):
        try:
            text = Path(word_bank_file).read_text(encoding="utf-8")
            self.words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]
        except Exception as e:
            self.words = ["programming", "backend", "interface", "database"]

    def phonetic_code(self, word):
        return {
            "soundex": jellyfish.soundex(word),
            "metaphone": jellyfish.metaphone(word),
            "nysiis": jellyfish.nysiis(word)
        }

    def phonetic_distance(self, code1, code2):
        dists = []
        for key in code1:
            if key in code2:
                dists.append(jellyfish.levenshtein_distance(code1[key], code2[key]))
        return np.mean(dists) if dists else 1.0

    def generate_typo(self, word, max_dist=2):
        orig_code = self.phonetic_code(word)
        candidates = set()
        for _ in range(50):
            typo = word
            op = random.choice(["swap", "sub", "del", "ins"])
            # ... (your existing swap/sub/del/ins logic here)
            if typo != word and len(typo) >= 3:
                dist = self.phonetic_distance(orig_code, self.phonetic_code(typo))
                if dist <= max_dist:
                    candidates.add(typo)
        return random.choice(list(candidates)) if candidates else word

    def get_challenge(self):
        word = random.choice(self.words)
        typo = self.generate_typo(word)
        return word, typo