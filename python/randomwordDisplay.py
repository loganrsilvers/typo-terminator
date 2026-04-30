from pyscript import when, document, window
from phoneticTypo import TypoGenerator 

# Initialize the generator at the top level
gen = TypoGenerator() 
current_typing = ""
correct_answer = ""

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

        # Auto-check if correct
        if current_typing.strip() == correct_answer.lower().strip():
            display_element.style.color = "var(--green)"
            print("Match found!")

@when("click", "#btn")
def getWord(event=None): # event=None allows us to call this manually
    global current_typing, correct_answer
    
    current_typing = ""
    
    # Update UI elements
    live_display = document.getElementById("LiveTypeDisplay")
    word_display = document.getElementById("WordDisplay")
    
    if live_display and word_display:
        live_display.innerText = ""
        live_display.style.color = "var(--med)"
        
        # Get your word from the TypoGenerator class
        original, typo = gen.get_challenge()
        correct_answer = original.lower()
        word_display.innerText = typo.lower()

# Start the game with a word immediately on load
getWord()