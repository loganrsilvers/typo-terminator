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
        except:
            self.words = ["programming", "backend", "database", "chicago", "interface", "teamwork"]

    def generate_typo(self, word):
        typo = list(word)
        if len(typo) >= 2:
            i = random.randint(0, len(typo) - 2)
            typo[i], typo[i+1] = typo[i+1], typo[i]
        return "".join(typo)

    def get_challenge(self):
        word = random.choice(self.words)
        return word, self.generate_typo(word)

gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""
current_timer_task = None
game_active = False

DIFFICULTIES = {"easy": 15, "medium": 8, "hard": 4, "terminator": 2}

async def run_timer(seconds):
    global game_active
    display = document.getElementById("TimerDisplay")
    for i in range(seconds, -1, -1):
        if not game_active: return
        display.innerText = f"Time: {i}s"
        if i == 0:
            document.getElementById("UserTypingBox").style.borderColor = "red"
            await asyncio.sleep(0.5)
            load_new_word()
            return
        await asyncio.sleep(1)

def load_new_word():
    global correct_answer, current_timer_task, game_active
    game_active = False 
    
    word_display = document.getElementById("WordDisplay")
    input_box = document.getElementById("UserTypingBox")
    
    original, typo = gen.get_challenge()
    correct_answer = original.lower().strip()
    word_display.innerText = typo
    
    input_box.value = ""
    input_box.style.borderColor = "white"
    input_box.focus()

    diff = document.getElementById("DifficultySelect").value
    seconds = DIFFICULTIES.get(diff, 8)
    game_active = True
    
    if current_timer_task: current_timer_task.cancel()
    current_timer_task = asyncio.ensure_future(run_timer(seconds))

@when("click", "#StartBtn")
def start_game(event):
    input_box = document.getElementById("UserTypingBox")
    input_box.disabled = False
    input_box.placeholder = "Type here..."
    
    document.getElementById("StartBtn").style.display = "none"
    document.getElementById("SkipBtn").style.display = "block"
    
    load_new_word()

@when("keydown", "#UserTypingBox")
def handle_keypress(event):

    if event.key == "Enter":
        user_input = document.getElementById("UserTypingBox").value.lower().strip()
        if user_input == correct_answer:
            load_new_word()

@when("click", "#SkipBtn")
def skip(event):
    load_new_word()