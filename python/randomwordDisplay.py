from pyscript import when, document, window

current_typing = "" # Stores what you've typed so far
correct_answer = "" # From your TypoGenerator

@when("keydown", "html")
def handle_keypress(event):
    global current_typing
    
    # event.key is the character you pressed
    key = event.key
    
    # 1. Handle Backspace
    if key == "Backspace":
        current_typing = current_typing[:-1]
    
    # 2. Handle standard characters (ignore Shift, Ctrl, etc.)
    elif len(key) == 1:
        # Convert to lowercase as you requested earlier
        current_typing += key.lower()

    # 3. Update the display under the word
    display_element = document.getElementById("LiveTypeDisplay")
    display_element.innerText = current_typing

    # 4. Auto-check if correct
    if current_typing == correct_answer:
        display_element.style.color = "var(--green)"
        print("Match found!")

@when("click", "#btn")
def getWord(event):
    global current_typing, correct_answer
    
    # Reset the typing for the new round
    current_typing = ""
    document.getElementById("LiveTypeDisplay").innerText = ""
    document.getElementById("LiveTypeDisplay").style.color = "var(--med)"
    
    # Get your word from the TypoGenerator class
    original, typo = gen.get_challenge()
    correct_answer = original
    document.getElementById("WordDisplay").innerText = typo