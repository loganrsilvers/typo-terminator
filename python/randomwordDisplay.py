import random
import os
from pyscript import when, document

file_path = "wordbank/600vocabWords.txt"
word_list = []

# 1. Load the list once when the script starts
if os.path.exists(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        # Split by commas and clean up whitespace
        word_list = [w.strip() for w in content.split(',') if w.strip()]
else:
    print(f"Error: {file_path} not found.")

@when("click", "#btn")
def getWord(event):
    if word_list:
        # 2. Pick a NEW random word inside the function
        new_word = random.choice(word_list)
        # 3. Display the word (make sure your HTML ID is "count")
        document.getElementById("WordDisplay").innerText = new_word
    else:
        document.getElementById("WordDisplay").innerText = "List Empty"
