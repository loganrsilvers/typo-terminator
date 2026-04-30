from pynput import keyboard

def on_press(key):
    try:
        # 1. Get the character
        char = key.char
        
        # 2. Convert to lowercase if it's not None
        if char is not None:
            lower_char = char.lower()
            print(f'User typed: {lower_char}')
            
    except AttributeError:
        # This handles keys like Shift, Enter, etc.
        print(f'Special key pressed: {key}')

# This starts the "listener" that waits for typing
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()