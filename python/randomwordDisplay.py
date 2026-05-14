import asyncio
from pyscript import when, document
from phoneticTypo import TypoGenerator

# ── Initialise ────────────────────────────────────────────────────────────────
gen = TypoGenerator("wordbank/600vocabWords.txt")

# ── Game state ────────────────────────────────────────────────────────────────
correct_answer = ""
current_timer  = None
game_active    = False
score          = 0
streak         = 0
best_streak    = 0
lives          = 3
MAX_LIVES      = 3

DIFFICULTIES = {"easy": 15, "medium": 8, "hard": 4, "terminator": 2}

# ── UI helpers ────────────────────────────────────────────────────────────────
def update_hud():
    document.getElementById("ScoreDisplay").innerText  = str(score)
    document.getElementById("StreakDisplay").innerText = str(streak)
    document.getElementById("BestDisplay").innerText   = str(best_streak)
    hearts = ("❤️" * lives) + ("🖤" * (MAX_LIVES - lives))
    document.getElementById("LivesDisplay").innerText  = hearts

def set_feedback(msg, color="white"):
    el             = document.getElementById("Feedback")
    el.innerText   = msg
    el.style.color = color

def show_game_over():
    global game_active
    game_active = False
    if current_timer:
        current_timer.cancel()
    document.getElementById("GameArea").classList.add("hidden")
    document.getElementById("GameOverScreen").classList.add("visible")
    document.getElementById("FinalScore").innerText  = str(score)
    document.getElementById("FinalStreak").innerText = str(best_streak)

def lose_life(reason=""):
    global lives, streak
    lives  -= 1
    streak  = 0
    update_hud()
    set_feedback(reason, "var(--danger)")
    if lives <= 0:
        show_game_over()

# ── Loading screen ────────────────────────────────────────────────────────────
def on_progress(word, typo, api_call, max_calls, approved, batch_size):
    """
    Called on every single API attempt.
    Bar fills based on api_calls / max_calls so it moves with every word checked.
    Label shows which word is being tested right now.
    """
    pct = int((api_call / max_calls) * 100)
    document.getElementById("LoadingBar").style.width     = f"{pct}%"
    document.getElementById("LoadingApproved").innerText  = str(approved)
    document.getElementById("LoadingTotal").innerText     = str(batch_size)
    document.getElementById("LoadingCurrentWord").innerText = f'checking "{word}" → "{typo}"'

async def run_warm_up():
    await gen.warm_up(on_progress=on_progress)
    document.getElementById("LoadingScreen").classList.add("hidden")
    document.getElementById("StartBtn").disabled = False

asyncio.ensure_future(run_warm_up())

# ── Timer ─────────────────────────────────────────────────────────────────────
async def run_timer(seconds):
    global game_active

    for i in range(seconds, -1, -1):
        if not game_active:
            return

        document.getElementById("TimerDisplay").innerText = f"Time: {i}s"
        pct      = (i / seconds) * 100
        bar_fill = document.getElementById("TimerBarFill")
        bar_fill.style.width = f"{pct}%"

        if pct > 60:
            bar_fill.style.background = "var(--accent)"
        elif pct > 30:
            bar_fill.style.background = "var(--warn)"
        else:
            bar_fill.style.background = "var(--danger)"

        if i == 0:
            document.getElementById("TimerDisplay").innerText          = "TIME'S UP!"
            document.getElementById("UserTypingBox").style.borderColor = "var(--danger)"
            lose_life(f"Time's up!  Answer: {correct_answer}")
            if game_active:
                await asyncio.sleep(1.5)
                load_next_challenge()
            return

        await asyncio.sleep(1)

# ── Challenge loader ──────────────────────────────────────────────────────────
def load_next_challenge():
    global correct_answer, current_timer, game_active

    if not game_active:
        return

    if current_timer:
        current_timer.cancel()
        current_timer = None

    original, typo = gen.get_challenge()
    correct_answer = original.lower().strip()

    document.getElementById("WordDisplay").innerText             = typo.upper()
    document.getElementById("UserTypingBox").value               = ""
    document.getElementById("UserTypingBox").style.borderColor   = "var(--border)"
    document.getElementById("UserTypingBox").classList.remove("flash-wrong", "flash-right")
    document.getElementById("UserTypingBox").focus()
    set_feedback("")

    diff    = document.getElementById("DifficultySelect").value
    seconds = DIFFICULTIES.get(diff, 8)

    bar_fill                  = document.getElementById("TimerBarFill")
    bar_fill.style.transition = "none"
    bar_fill.style.width      = "100%"
    bar_fill.style.background = "var(--accent)"

    current_timer = asyncio.ensure_future(run_timer(seconds))

# ── Event handlers ────────────────────────────────────────────────────────────
@when("click", "#StartBtn")
def start_game(event):
    global score, streak, best_streak, lives, game_active

    if document.getElementById("StartBtn").disabled:
        return

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
    if current_timer:
        current_timer.cancel()

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
    update_hud()


@when("keydown", "#UserTypingBox")
def handle_keypress(event):
    global score, streak, best_streak

    if not game_active or event.key != "Enter":
        return

    user_input = document.getElementById("UserTypingBox").value.lower().strip()
    ib         = document.getElementById("UserTypingBox")

    if user_input == correct_answer:
        score  += 1
        streak += 1
        if streak > best_streak:
            best_streak = streak
        update_hud()
        set_feedback("✓ Correct!", "var(--accent)")
        ib.classList.remove("flash-wrong")
        ib.classList.add("flash-right")
        load_next_challenge()
    else:
        ib.classList.remove("flash-right")
        ib.classList.add("flash-wrong")
        set_feedback("✗ Wrong — try again!", "var(--danger)")


@when("click", "#SkipBtn")
def handle_skip(event):
    if not game_active:
        return
    lose_life(f"Skipped!  Answer: {correct_answer}")
    if game_active:
        load_next_challenge()