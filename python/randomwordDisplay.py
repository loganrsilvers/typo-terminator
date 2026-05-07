import random
import string
import numpy as np
import jellyfish
import asyncio
from pathlib import Path
from pyscript import when, document

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


gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""
current_timer_task = None
game_active = False 

DIFFICULTIES = {
    "easy": 15,
    "medium": 8,
    "hard": 4,
    "terminator": 2
}


async def run_timer(seconds):
    global game_active
    timer_display = document.getElementById("TimerDisplay")
    input_box = document.getElementById("UserTypingBox")
    
    for i in range(seconds, -1, -1):
        if not game_active:
            break 
        
        timer_display.innerText = f"Time: {i}s"
        
        if i == 0:
            timer_display.innerText = "TIME'S UP!"
            input_box.style.borderColor = "red"
            await asyncio.sleep(1) 
            if game_active: 
                load_new_word()
            return
            
        await asyncio.sleep(1)


def check_answer():
    global correct_answer
    input_box = document.getElementById("UserTypingBox")
    user_input = input_box.value.lower().strip()


    if user_input == correct_answer:
        load_new_word()


@when("input", "#UserTypingBox")
def handle_input(event):
    check_answer()

@when("click", "#btn")
def handle_click(event):
    load_new_word()

@when("change", "#DifficultySelect")
def handle_difficulty_change(event):
    load_new_word()

def load_new_word():
    global correct_answer, current_timer_task, game_active
    

    game_active = False 
    
    word_display = document.getElementById("WordDisplay")
    input_box = document.getElementById("UserTypingBox")
    diff_select = document.getElementById("DifficultySelect")
    
    if word_display and input_box:
        original, typo = gen.get_challenge()
        correct_answer = original.lower().strip()
        word_display.innerText = typo.lower()
        
        input_box.value = ""
        input_box.style.borderColor = "white"
        input_box.focus()


        diff = diff_select.value if diff_select else "medium"
        seconds = DIFFICULTIES.get(diff, 8)
        
        game_active = True
        
        if current_timer_task:
            current_timer_task.cancel()
        
 
        current_timer_task = asyncio.ensure_future(run_timer(seconds))


load_new_word()