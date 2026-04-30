import random
import string
import numpy as np
import jellyfish
from pathlib import Path
from pyscript import when, document

# --- Paste your TypoGenerator class here ---
class TypoGenerator:
    def __init__(self, word_bank_file):
        text = Path(word_bank_file).read_text(encoding="utf-8")
        self.words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]

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
                typo = list(word); typo[i], typo[i+1] = typo[i+1], typo[i]; typo = "".join(typo)
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

# --- Game Logic ---

# Initialize the generator
gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""

@when("click", "#btn")
def getWord(event):
    global correct_answer
    
    # Use the class to get a word and its phonetic typo
    original, typo = gen.get_challenge()
    correct_answer = original
    
    # Update the UI
    document.getElementById("WordDisplay").innerText = typo
    document.getElementById("UserTypingBox").value = ""
    print(f"Hint for dev: The answer is {original}")