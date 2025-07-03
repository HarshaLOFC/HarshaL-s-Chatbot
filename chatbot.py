import tkinter as tk
from tkinter import scrolledtext
import re
import threading
import queue
import time
import speech_recognition as sr
import pyttsx3



# -------------------- Static Knowledge Base --------------------
RESPONSES = {
    "hello": "Hey there! I'm Harshal's chatbot. Wanna know something cool about him?",
    "hi": "Hi! Ask me anything about Harshal — he's pretty awesome",
    "what is your name": "I'm just a friendly little bot created to tell you all about Harshal Arjune!",
    "who is harshal": "Harshal Arjune is a third-year BE student in Information Technology from SPPU, working hard to become an AI/ML engineer.",
    "what is harshal's name": "Full name? Harshal Arjune. Simple and solid!",
    "how old is harshal": "He's in his early 20s and totally into AI, tech, and leveling up every day.",
    "where is harshal from": "He’s from India — full of ideas, chai, and tech dreams!",
    "what are harshal's hobbies": "Harshal loves coding cool stuff, diving into AI/ML, playing games, and exploring tech courses online.",
    "what does harshal do": "Right now? He’s building projects, leveling up his skills, and prepping for the job world.",
    "what languages does harshal know": "He codes mainly in Python and knows his way around TensorFlow, PyTorch, and scikit-learn.",
    "what is harshal's goal": "Big goal? To become an AI/ML engineer who builds smart, useful, and fun stuff.",
    "does harshal like ai": "Like it? He’s obsessed! Machine learning, deep learning, you name it.",
    "is harshal open to work": "Absolutely! He’s always up for exciting AI/ML opportunities. Hit him up if you've got something cool.",
    "how can i contact harshal": "You can reach out to him on LinkedIn or drop a mail: harshalarjune13@gmail.com",
    "thank you": "No worries! Ask away if you wanna know more about the legend — Harshal.",
    "bye": "Later, human! Hope you learned a thing or two about Harshal.",
    "default": "Hmm, I didn’t quite get that. Try asking me something else about Harshal!"
}

# -------------------- Chatbot Logic --------------------
def get_response(user_text: str) -> str:
    user_text = user_text.lower()
    for k, v in RESPONSES.items():
        if re.search(k, user_text):
            return v
    return RESPONSES["default"]

# -------------------- TTS Setup --------------------
engine = pyttsx3.init()
engine.setProperty("rate", 160)
voices = engine.getProperty("voices")
female = next((v for v in voices if "female" in v.name.lower()), None)
if female:
    engine.setProperty("voice", female.id)

def speak_async(text: str):
    threading.Thread(target=lambda: (engine.say(text), engine.runAndWait()), daemon=True).start()

# -------------------- Thread‑safe Queue --------------------
q: "queue.Queue[tuple[str,str]]" = queue.Queue()

# -------------------- GUI Functions --------------------
def add_message(speaker: str, msg: str):
    tag = "user_tag" if speaker == "You" else "bot_tag"
    chat.configure(state="normal")
    chat.insert(tk.END, f"{speaker}: ", tag)
    chat.insert(tk.END, f"{msg}\n\n")
    chat.configure(state="disabled")
    chat.see(tk.END)

def send_text(event=None):
    text = entry.get().strip()
    if not text:
        return
    entry.delete(0, tk.END)
    process_user(text)

def process_user(text: str):
    add_message("You", text)
    def _reply():
        q.put(("bot", get_response(text)))
    threading.Timer(0.6, _reply).start()

# -------------------- Voice Input --------------------
def listen_thread():
    recognizer = sr.Recognizer()
    with sr.Microphone() as src:
        try:
            recognizer.adjust_for_ambient_noise(src, duration=0.4)
            audio = recognizer.listen(src, timeout=5)
            q.put(("voice", recognizer.recognize_google(audio)))
        except Exception:
            q.put(("error", "Sorry, couldn't catch that."))
        finally:
            q.put(("listen_done", ""))

def start_listening():
    mic_btn.config(text="🎤…", bg="#ffcccb", state=tk.DISABLED)
    send_btn.config(state=tk.DISABLED)
    threading.Thread(target=listen_thread, daemon=True).start()

# -------------------- Queue Poller --------------------
def poll_queue():
    try:
        while True:
            evt, data = q.get_nowait()
            if evt == "bot":
                add_message("Bot", data)
                speak_async(data)
            elif evt == "voice":
                process_user(data)
            elif evt == "error":
                add_message("Bot", data)
            elif evt == "listen_done":
                mic_btn.config(text="🎤", bg="#90caf9", state=tk.NORMAL)
                send_btn.config(state=tk.NORMAL)
    except queue.Empty:
        pass
    root.after(100, poll_queue)

# -------------------- Build GUI --------------------
root = tk.Tk()
root.title("Harshal Chatbot")
root.configure(bg="#cce7ff")
root.resizable(False, False)

chat = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD, state="disabled",
                                font=("Helvetica", 12), bg="#e3f2fd", fg="#0d47a1",
                                padx=10, pady=10, borderwidth=0, highlightthickness=0)
chat.tag_config("user_tag", foreground="#1565c0", font=("Helvetica", 12, "bold"))
chat.tag_config("bot_tag", foreground="#0d47a1", font=("Helvetica", 12, "bold"))
chat.pack(padx=15, pady=15)

input_frame = tk.Frame(root, bg="#cce7ff")
input_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

entry = tk.Entry(input_frame, font=("Helvetica", 12), bg="#e1f5fe", fg="#01579b", insertbackground="#01579b")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry.focus()

send_btn = tk.Button(input_frame, text="Send", font=("Helvetica", 10, "bold"), bg="#90caf9", fg="#0d47a1",
                     activebackground="#64b5f6", activeforeground="white", command=send_text, padx=10, pady=5)
send_btn.pack(side=tk.LEFT)

mic_btn = tk.Button(input_frame, text="🎤", font=("Helvetica", 10, "bold"), bg="#90caf9", fg="#0d47a1",
                    activebackground="#64b5f6", activeforeground="white", command=start_listening, padx=10, pady=5)
mic_btn.pack(side=tk.LEFT, padx=(10, 0))

root.bind("<Return>", send_text)

# Init
add_message("Bot", "Hey there! I'm Harshal's chatbot. Wanna know something cool about him?")
poll_queue()
root.mainloop()