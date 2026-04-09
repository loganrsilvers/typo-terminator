from pyscript import when, document

number = 0

@when("click", "#btn")
def increase(event):
    global number
    number += 1
    document.getElementById("count").innerText = str(number)
