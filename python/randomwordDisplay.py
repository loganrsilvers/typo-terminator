import asyncio
from pyscript import when, document
from phoneticTypo import TypoGenerator

# ── Game state ──────────────────────────────────────────────
gen            = TypoGenerator("wordbank/600vocabWords.txt")
correct_answer = ""
current_timer  = None
game_active    = False
score          = 0
streak         = 0
best_streak    = 0
lives          = 3
MAX_LIVES      = 3

DIFFICULTIES = {"easy": 15, "medium": 8, "hard": 4, "terminator": 2}

# ── Helpers ─────────────────────────────────────────────────

def update_hud():
    document.getElementById("ScoreDisplay").innerText  = str(score)
    document.getElementById("StreakDisplay").innerText = str(streak)
    document.getElementById("BestDisplay").innerText   = str(best_streak)
    # Always rebuild from scratch — never append to existing text
    hearts = ("❤️" * lives) + ("🖤" * (MAX_LIVES - lives))
    document.getElementById("LivesDisplay").innerText  = hearts

def set_feedback(msg, color="white"):
    el            = document.getElementById("Feedback")
    el.innerText  = msg
    el.style.color = color

def show_game_over():
    global game_active
    game_active = False

    if current_timer:
        current_timer.cancel()

    document.getElementById("GameArea").classList.add("hidden")
    document.getElementById("FinalScore").innerText  = str(score)
    document.getElementById("FinalStreak").innerText = str(best_streak)
    document.getElementById("GameOverScreen").classList.add("visible")

def lose_life(reason=""):
    global lives, streak
    lives  -= 1
    streak  = 0
    update_hud()
    set_feedback(reason, "var(--danger)")
    if lives <= 0:
        show_game_over()

# ── Timer ────────────────────────────────────────────────────

async def run_timer(seconds):
    global game_active
    timer_display = document.getElementById("TimerDisplay")
    bar_fill      = document.getElementById("TimerBarFill")
    input_box     = document.getElementById("UserTypingBox")

    for i in range(seconds, -1, -1):
        if not game_active:
            return
        timer_display.innerText = f"Time: {i}s"

        pct = (i / seconds) * 100
        bar_fill.style.width = f"{pct}%"
        if pct > 60:
            bar_fill.style.background = "var(--accent)"
        elif pct > 30:
            bar_fill.style.background = "var(--warn)"
        else:
            bar_fill.style.background = "var(--danger)"

        if i == 0:
            timer_display.innerText     = "TIME'S UP!"
            input_box.style.borderColor = "var(--danger)"
            lose_life(f"Time's up! Answer was: {correct_answer}")
            if game_active:
                await asyncio.sleep(1.2)
                load_next_challenge()
            return

        await asyncio.sleep(1)

# ── Challenge loader ─────────────────────────────────────────

def load_next_challenge():
    global correct_answer, current_timer

    if not game_active:
        return

    word_display = document.getElementById("WordDisplay")
    input_box    = document.getElementById("UserTypingBox")

    original, typo         = gen.get_challenge()
    correct_answer         = original.lower().strip()
    word_display.innerText = typo

    input_box.value             = ""
    input_box.style.borderColor = "var(--border)"
    input_box.focus()
    set_feedback("")

    diff    = document.getElementById("DifficultySelect").value
    seconds = DIFFICULTIES.get(diff, 8)

    bar_fill                  = document.getElementById("TimerBarFill")
    bar_fill.style.transition = "none"
    bar_fill.style.width      = "100%"
    bar_fill.style.background = "var(--accent)"

    if current_timer:
        current_timer.cancel()
    current_timer = asyncio.ensure_future(run_timer(seconds))

# ── Event handlers ───────────────────────────────────────────

@when("click", "#StartBtn")
def start_game(event):
    global score, streak, best_streak, lives, game_active
    score       = 0
    streak      = 0
    best_streak = 0
    lives       = MAX_LIVES
    game_active = True

    document.getElementById("StartBtn").style.display    = "none"
    document.getElementById("SkipBtn").style.display     = "inline-block"
    document.getElementById("DifficultySelect").disabled = True
    document.getElementById("UserTypingBox").disabled    = False

    update_hud()
    load_next_challenge()


@when("click", "#RestartBtn")
def restart_game(event):
    global game_active
    game_active = False

    document.getElementById("GameOverScreen").classList.remove("visible")
    document.getElementById("GameArea").classList.remove("hidden")
    document.getElementById("StartBtn").style.display    = "block"
    document.getElementById("SkipBtn").style.display     = "none"
    document.getElementById("DifficultySelect").disabled = False
    document.getElementById("UserTypingBox").disabled    = True
    document.getElementById("UserTypingBox").value       = ""
    document.getElementById("WordDisplay").innerText     = "---"
    document.getElementById("TimerDisplay").innerText    = "Time: --"
    document.getElementById("TimerBarFill").style.width  = "100%"
    set_feedback("")


@when("keydown", "#UserTypingBox")
def handle_keypress(event):
    global score, streak, best_streak

    if not game_active or event.key != "Enter":
        return

    user_input = document.getElementById("UserTypingBox").value.lower().strip()

    if user_input == correct_answer:
        score  += 1
        streak += 1
        if streak > best_streak:
            best_streak = streak
        update_hud()
        set_feedback("✓ Correct!", "var(--accent)")
        load_next_challenge()
    else:
        document.getElementById("UserTypingBox").style.borderColor = "var(--danger)"
        set_feedback("✗ Wrong — try again!", "var(--danger)")


@when("click", "#SkipBtn")
def handle_skip(event):
    if not game_active:      # guard: dead after game over
        return
    lose_life(f"Skipped! Answer was: {correct_answer}")
    if game_active:
        load_next_challenge()
