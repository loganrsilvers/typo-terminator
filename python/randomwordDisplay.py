import asyncio
import random
from pyscript import when, document
from scrambler import WordBank

# ── Initialise word bank ──────────────────────────────────────────────────────
bank = WordBank("wordbank/600vocabWords.txt")

# ── Game state ────────────────────────────────────────────────────────────────
correct_answer  = ""
timer_task      = None
game_active     = False
score           = 0
streak          = 0
best            = 0

DIFFICULTIES = {"easy": 15, "medium": 8, "hard": 4, "terminator": 2}

# ── UI helpers ────────────────────────────────────────────────────────────────
def get_difficulty():
    active = document.querySelector(".diff-btn.active")
    return active.getAttribute("data-diff") if active else "medium"

def get_seconds():
    active = document.querySelector(".diff-btn.active")
    return int(active.getAttribute("data-secs")) if active else 8

def set_feedback(text, css_class):
    fb = document.getElementById("feedback")
    fb.innerText = text
    fb.className = css_class

def update_hud():
    document.getElementById("score-value").innerText  = str(score)
    document.getElementById("streak-value").innerText = str(streak)
    document.getElementById("best-value").innerText   = str(best)

def update_timer_display(remaining, total):
    tv  = document.getElementById("timer-value")
    bar = document.getElementById("timer-bar")
    tv.innerText   = str(remaining)
    pct            = (remaining / total) * 100
    bar.style.width = f"{pct}%"

    if remaining <= 2:
        tv.className  = "danger"
        bar.className = "danger"
    elif remaining <= total * 0.4:
        tv.className  = "warn"
        bar.className = "warn"
    else:
        tv.className  = ""
        bar.className = ""

def flash_word(css_class):
    wd = document.getElementById("word-display")
    wd.classList.remove("flash-correct", "flash-wrong")
    _ = wd.offsetWidth   # force reflow so the animation restarts cleanly
    wd.classList.add(css_class)

# ── Timer coroutine ───────────────────────────────────────────────────────────
async def run_timer(seconds):
    global game_active, streak

    for i in range(seconds, -1, -1):
        if not game_active:
            return
        update_timer_display(i, seconds)
        if i == 0:
            game_active = False
            streak = 0
            update_hud()
            set_feedback(f"TIME'S UP!", "show-timeout")
            flash_word("flash-wrong")

            document.getElementById("input-box").disabled = True

            # Briefly reveal the correct answer before moving on
            rev = document.getElementById("reveal")
            rev.innerHTML = f"The word was: <span>{correct_answer}</span>"
            await asyncio.sleep(2)
            rev.innerHTML = ""
            load_next_challenge(restart_timer=True)
            return
        await asyncio.sleep(1)

# ── Core game flow ────────────────────────────────────────────────────────────
def load_next_challenge(restart_timer=True):
    global correct_answer, timer_task, game_active

    game_active = False
    if timer_task:
        timer_task.cancel()

    word, scrambled = bank.get_challenge()
    correct_answer  = word

    document.getElementById("word-display").innerText = scrambled.upper()

    ib = document.getElementById("input-box")
    ib.value    = ""
    ib.disabled = False
    ib.className = ""
    ib.focus()

    set_feedback("", "")
    document.getElementById("reveal").innerHTML = ""
    update_hud()

    if restart_timer:
        secs = get_seconds()
        update_timer_display(secs, secs)
        game_active = True
        timer_task  = asyncio.ensure_future(run_timer(secs))

# ── Event handlers ────────────────────────────────────────────────────────────
@when("click", "#start-btn")
def start_game(event):
    global score, streak, best
    score = streak = 0
    update_hud()

    document.getElementById("start-btn").style.display = "none"
    document.getElementById("skip-btn").style.display  = "inline-block"

    # Lock difficulty buttons once game starts
    for btn in document.querySelectorAll(".diff-btn"):
        btn.setAttribute("disabled", "true")

    load_next_challenge(restart_timer=True)

@when("keydown", "#input-box")
def handle_keypress(event):
    global score, streak, best

    if event.key != "Enter":
        return

    user_input = document.getElementById("input-box").value.lower().strip()

    if user_input == correct_answer:
        score  += 1
        streak += 1
        if score > best:
            best = score
        update_hud()
        set_feedback("CORRECT!", "show-correct")
        flash_word("flash-correct")
        load_next_challenge(restart_timer=True)
    else:
        # Wrong answer: flash and let them try again, don't advance
        set_feedback("WRONG — try again", "show-wrong")
        ib = document.getElementById("input-box")
        ib.classList.remove("wrong")
        _ = ib.offsetWidth   # force reflow
        ib.classList.add("wrong")
        flash_word("flash-wrong")

@when("click", "#skip-btn")
def handle_skip(event):
    global streak
    streak = 0
    update_hud()
    set_feedback("SKIPPED", "show-timeout")
    load_next_challenge(restart_timer=True)
