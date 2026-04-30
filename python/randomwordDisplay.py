import random
import string
import numpy as np
import jellyfish
from pathlib import Path
from pyscript import when, document

# --- 1. TypoGenerator Class ---
class TypoGenerator:
    def __init__(self, word_bank_file):
        # Using Path to read the fetched file
        text = Path(word_bank_file).read_text(encoding="utf-8")
        # Clean up the word bank (split by commas or newlines)
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

# --- 2. Game Variables ---
# Ensure this path matches your [[fetch]] in HTML
gen = TypoGenerator("wordbank/600vocabWords.txt")
current_typing = ""
correct_answer = ""

# --- 3. Event Handlers ---

@when("keydown", "html")
def handle_keypress(event):
    global current_typing, correct_answer
    
    key = event.key
    
    if key == "Backspace":
        current_typing = current_typing[:-1]
    elif len(key) == 1:
        current_typing += key.lower()

    display_element = document.getElementById("LiveTypeDisplay")
    if display_element:
        display_element.innerText = current_typing

        # Check if typed correctly
        if current_typing.strip() == correct_answer.lower().strip():
            display_element.style.color = "var(--green)"
            print("Match found!")

@when("click", "#btn")
def getWord(event=None):
    global current_typing, correct_answer
    
    current_typing = ""
    
    live_display = document.getElementById("LiveTypeDisplay")
    word_display = document.getElementById("WordDisplay")
    
    if live_display and word_display:
        live_display.innerText = ""
        live_display.style.color = "var(--med)"
        
        # Get new word
        original, typo = gen.get_challenge()
        correct_answer = original.lower()
        word_display.innerText = typo.lower()
        print(f"New word loaded. Answer is: {correct_answer}")

# --- 4. Initialize Game ---
getWord()