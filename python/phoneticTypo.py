python
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
            print(f"Error loading wordbank: {e}")
            self.words = ["programming", "backend", "database", "interface", "columbia", "chicago", "wrestling", "software"]

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
            
            if op == "swap" and len(word) >= 2:
                i = random.randint(0, len(word) - 2)
                t = list(word)
                t[i], t[i+1] = t[i+1], t[i]
                typo = "".join(t)
            elif op == "sub" and len(word) >= 1:
                i = random.randint(0, len(word) - 1)
                typo = word[:i] + random.choice(string.ascii_lowercase) + word[i+1:]
            elif op == "del" and len(word) >= 2:
                i = random.randint(0, len(word) - 1)
                typo = word[:i] + word[i+1:]
            elif op == "ins":
                i = random.randint(0, len(word))
                typo = word[:i] + random.choice(string.ascii_lowercase) + word[i:]
            
            if typo != word and len(typo) >= 3:
                dist = self.phonetic_distance(orig_code, self.phonetic_code(typo))
                if dist <= max_dist:
                    candidates.add(typo)
        
        return random.choice(list(candidates)) if candidates else word

    def get_challenge(self):
        word = random.choice(self.words)
        typo = self.generate_typo(word)
        return word, typo
