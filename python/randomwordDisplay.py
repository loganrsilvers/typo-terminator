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
        except Exception:
            # Emergency backup words if the file fails to load
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
            op = random.choice(["swap", "sub", "del", "ins"])
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

# --- 2. Logic ---
gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""

@when("keydown", "#UserTypingBox")
def handle_input_key(event):
    global correct_answer
    
    # Check if the user pressed the Enter key
    if event.key == "Enter":
        user_input = event.target.value.lower().strip()
        
        # If it's correct, move to the next word
        if user_input == correct_answer:
            print("Correct! Moving to next word...")
            getWord()  # This clears the box and gets a new word
        else:
            # Optional: Visual shake or red border if they hit enter but it's wrong
            event.target.style.borderColor = "#FF5252" 

@when("input", "#UserTypingBox")
def live_check(event):
    global correct_answer
    user_input = event.target.value.lower().strip()
    feedback = document.getElementById("Feedback")
    
    # Give them a green "success" hint as they type
    if user_input == correct_answer:
        event.target.style.borderColor = "#4CAF50"
        feedback.innerText = "Press Enter to continue!"
        feedback.style.color = "#4CAF50"
    else:
        event.target.style.borderColor = "var(--med)"
        feedback.innerText = ""

# The getWord function stays the same as before
@when("click", "#btn")
def getWord(event=None):
    global correct_answer
    
    word_display = document.getElementById("WordDisplay")
    input_box = document.getElementById("UserTypingBox")
    feedback = document.getElementById("Feedback")
    
    # Get new word from the class
    original, typo = gen.get_challenge()
    correct_answer = original.lower()
    
    # Reset UI
    word_display.innerText = typo.lower()
    input_box.value = ""
    input_box.style.borderColor = "var(--med)"
    feedback.innerText = ""
    input_box.focus() # Put the cursor back in the box automatically
# Initialize
getWord()