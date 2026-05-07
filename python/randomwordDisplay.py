import asyncio
from pyscript import when, document
from phoneticTypo import TypoGenerator 

# Initialize game state
gen = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""
current_timer_task = None
game_active = False

DIFFICULTIES = {"easy": 15, "medium": 8, "hard": 4, "terminator": 2}

async def run_timer(seconds):
    global game_active
    timer_display = document.getElementById("TimerDisplay")
    input_box = document.getElementById("UserTypingBox")
    
    for i in range(seconds, -1, -1):
        if not game_active: break
        timer_display.innerText = f"Time: {i}s"
        if i == 0:
            timer_display.innerText = "TIME'S UP!"
            input_box.style.borderColor = "#ff4757"
            await asyncio.sleep(0.8)
            load_next_challenge()
            return
        await asyncio.sleep(1)

def load_next_challenge():
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

    # Get seconds based on difficulty dropdown
    diff_element = document.getElementById("DifficultySelect")
    diff = diff_element.value if diff_element else "medium"
    seconds = DIFFICULTIES.get(diff, 8)
    
    game_active = True
    if current_timer_task:
        current_timer_task.cancel()
    current_timer_task = asyncio.ensure_future(run_timer(seconds))

@when("click", "#StartBtn")
def start_game(event):
    document.getElementById("StartBtn").style.display = "none"
    document.getElementById("SkipBtn").style.display = "inline-block"
    input_box = document.getElementById("UserTypingBox")
    input_box.disabled = False
    load_next_challenge()

@when("keydown", "#UserTypingBox")
def handle_keypress(event):
    if event.key == "Enter":
        user_input = document.getElementById("UserTypingBox").value.lower().strip()
        if user_input == correct_answer:
            load_next_challenge()

@when("click", "#SkipBtn")
def handle_skip(event):
    load_next_challenge()