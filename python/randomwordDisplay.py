import random
import string
import numpy as np
import jellyfish
from pathlib import Path
from pyscript import when, document

# --- 1. TypoGenerator Class ---
class TypoGenerator:
    def __init__(self, word_bank_file):
        try:
            text = Path(word_bank_file).read_text(encoding="utf-8")
            # Splitting by commas or newlines and stripping whitespace
            self.words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]
        except Exception as e:
            print(f"Load Error: {e}. Using emergency backup words.")
            self.words = ["programming", "columbia", "chicago", "software", "development"]

    def phonetic_code(self, word):
        return {"soundex": jellyfish.soundex(word), "metaphone": jellyfish.metaphone(word), "nysiis": jellyfish.nysiis(word)}

    def phonetic_distance(self, code1, code2):
        dists = [jellyfish.levenshtein_distance(code1[k], code2[k]) for k in code1 if k in code2]
        return np.mean(dists) if dists else 1.0

    def generate_typo(self, word):
        orig_code = self.phonetic_code(word)
        candidates = set()
        for _ in range(50):
            typo = word
            op = random.choice(["swap", "sub"])
            if op == "swap" and len(word) >= 2:
                i = random.randint(0, len(word) - 2)
                typo = list(word); typo[i], typo[i+1] = typo[i+1], typo[i]; typo = "".join(typo)
            elif op == "sub":
                i = random.randint(0, len(word) - 1)
                typo = word[:i] + random.choice(string.ascii_lowercase) + word[i+1:]
            
            if typo != word and len(typo) >= 3:
                if self.phonetic_distance(orig_code, self.phonetic_code(typo)) <= 2:
                    candidates.add(typo)
        return random.choice(list(candidates)) if candidates else word

    def get_challenge(self):
        word = random.choice(self.words)
        return word, self.generate_typo(word)

# --- 2. Initialize Logic ---
gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""

@when("click", "#btn")
def handle_click(event):
    global correct_answer
    
    input_box = document.getElementById("UserTypingBox")
    user_input = input_box.value.lower().strip()

    # Debug logs for the console
    print(f"Comparing: '{user_input}' with '{correct_answer}'")

    if user_input == correct_answer:
        print("Match found!")
        load_new_word()
    else:
        input_box.style.borderColor = "red"
        print(f"Mismatch: Length of input is {len(user_input)}, Answer is {len(correct_answer)}")

def load_new_word():
    global correct_answer
    
    word_display = document.getElementById("WordDisplay")
    input_box = document.getElementById("UserTypingBox")
    
    # Safety check: ensure elements exist before updating
    if word_display and input_box:
        original, typo = gen.get_challenge()
        correct_answer = original.lower().strip() # Double strip for safety
        
        word_display.innerText = typo.lower()
        input_box.value = ""
        input_box.style.borderColor = "white"
        input_box.focus()

# Start the game
load_new_word()