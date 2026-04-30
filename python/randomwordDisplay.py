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

# --- 2. NEW: GameTester Class ---
class GameTester:
    def __init__(self, generator):
        self.gen = generator

    def run_all_tests(self):
        print("--- STARTING SYSTEM TEST ---")
        self.test_word_loading()
        self.test_typo_generation()
        print("--- SYSTEM TEST COMPLETE ---")

    def test_word_loading(self):
        if len(self.gen.words) > 0:
            print(f"✅ SUCCESS: Word bank loaded with {len(self.gen.words)} words.")
        else:
            print("❌ FAIL: Word bank is empty.")

    def test_typo_generation(self):
        orig, typo = self.gen.get_challenge()
        if orig != typo:
            print(f"✅ SUCCESS: Generated challenge '{typo}' from '{orig}'.")
        else:
            print("❌ FAIL: Generator returned the original word (no typo).")

# --- 3. Logic & Event Handlers ---
gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""

@when("click", "#btn")
def handle_click(event):
    global correct_answer
    input_box = document.getElementById("UserTypingBox")
    user_input = input_box.value.lower().strip()

    if user_input == correct_answer:
        load_new_word()
    else:
        input_box.style.borderColor = "red"
        print(f"Mismatch! Answer is: {correct_answer}")

def load_new_word():
    global correct_answer
    word_display = document.getElementById("WordDisplay")
    input_box = document.getElementById("UserTypingBox")
    
    if word_display and input_box:
        original, typo = gen.get_challenge()
        correct_answer = original.lower().strip()
        word_display.innerText = typo.lower()
        input_box.value = ""
        input_box.style.borderColor = "white"
        input_box.focus()

# --- 4. Execution ---
# Run the tests first to check the "engine"
tester = GameTester(gen)
tester.run_all_tests()

# Start the game
load_new_word()