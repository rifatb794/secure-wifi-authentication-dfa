import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import random

try:
    import winsound
except ImportError:
    winsound = None


# ================= DFA States =================
START = "START"
L1_Q1 = "L1_Q1"
L2_Q1 = "L2_Q1"
L2_Q2 = "L2_Q2"
L3_Q1 = "L3_Q1"
L3_Q2 = "L3_Q2"
L3_Q3 = "L3_Q3"
L4_Q1 = "L4_Q1"
ACCEPT = "ACCEPT"
LOCKED = "LOCKED"


# ================= Global Variables =================
current_state = START
attempt = 1
entered_password = ""
wrong_attempts = 0
correct_inputs = 0
time_left = 60
timer_running = True
start_time = time.time()
last_summary = ""

session_id = f"DFA-{time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"


# ================= Theme Colors =================
BG_MAIN = "#050816"
BG_HEADER = "#07111f"
BG_CARD = "#0b1220"
BG_CARD_2 = "#101827"
BORDER = "#38bdf8"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
CYAN = "#22d3ee"
BLUE = "#0ea5e9"
GREEN = "#22c55e"
YELLOW = "#facc15"
RED = "#ef4444"
BUTTON_DARK = "#334155"


# ================= Utility Functions =================
def play_sound(sound_type):
    if winsound:
        if sound_type == "success":
            winsound.Beep(950, 120)
        elif sound_type == "error":
            winsound.Beep(450, 180)
        elif sound_type == "lock":
            winsound.Beep(250, 400)


def add_hover(button, normal_color, hover_color):
    button.bind("<Enter>", lambda e: button.config(bg=hover_color))
    button.bind("<Leave>", lambda e: button.config(bg=normal_color))


def add_log(message):
    current_time = time.strftime("%H:%M:%S")
    log_box.config(state="normal")
    log_box.insert(tk.END, f"[{current_time}] {message}\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")


def add_transition_row(previous_state, user_input, next_state, status):
    table.insert("", "end", values=(previous_state, user_input, next_state, status))


def update_risk_meter():
    if wrong_attempts == 0:
        risk_label.config(text="Risk Level: LOW", fg=GREEN)
        threat_value.config(text="NORMAL", fg=GREEN)
    elif wrong_attempts == 1:
        risk_label.config(text="Risk Level: MEDIUM", fg=YELLOW)
        threat_value.config(text="SUSPICIOUS", fg=YELLOW)
    else:
        risk_label.config(text="Risk Level: HIGH", fg=RED)
        threat_value.config(text="HIGH RISK", fg=RED)

    unauthorized_value.config(text=str(wrong_attempts))


def export_report():
    global last_summary

    if not last_summary:
        messagebox.showwarning("No Report", "No authentication report available yet.")
        return

    os.makedirs("reports", exist_ok=True)
    file_path = os.path.join("reports", f"authentication_report_{session_id}.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(last_summary)

    messagebox.showinfo("Report Exported", f"Report saved successfully:\n{file_path}")


# ================= Character Validation =================
def is_digit(c):
    return c.isdigit()


def is_uppercase(c):
    return c.isupper()


def is_lowercase(c):
    return c.islower()


def is_special(c):
    return not c.isalnum()


# ================= DFA Information =================
def get_info():
    if current_state == START:
        return "Layer 1", "Special Character", "1st Character", "Relevant: Any special character"
    elif current_state == L1_Q1:
        return "Layer 2", "Uppercase Letter", "2nd Character", "Relevant: A-Z"
    elif current_state == L2_Q1:
        return "Layer 2", "Uppercase Letter", "3rd Character", "Relevant: A-Z"
    elif current_state == L2_Q2:
        return "Layer 3", "Lowercase Letter", "4th Character", "Relevant: a-z"
    elif current_state == L3_Q1:
        return "Layer 3", "Lowercase Letter", "5th Character", "Relevant: a-z"
    elif current_state == L3_Q2:
        return "Layer 3", "Lowercase Letter", "6th Character", "Relevant: a-z"
    elif current_state == L3_Q3:
        return "Layer 4", "Digit", "7th Character", "Relevant: 0-9"
    elif current_state == L4_Q1:
        return "Layer 4", "Digit", "8th Character", "Relevant: 0-9"

    return "-", "-", "-", "-"


# ================= Background and Layout =================
def draw_background():
    bg_canvas.delete("all")

    width = root.winfo_width()
    height = root.winfo_height()

    if width < 100:
        width = 1250
    if height < 100:
        height = 850

    for i in range(0, height, 4):
        shade = 8 + int(i / height * 16)
        color = f"#{shade:02x}{shade + 4:02x}{shade + 18:02x}"
        bg_canvas.create_rectangle(0, i, width, i + 4, outline="", fill=color)

    bg_canvas.create_oval(-220, -150, 300, 340, fill="#082f49", outline="")
    bg_canvas.create_oval(width - 360, 70, width + 200, 650, fill="#172554", outline="")
    bg_canvas.create_oval(300, height - 290, 900, height + 170, fill="#042f2e", outline="")


def resize_layout(event=None):
    draw_background()

    width = root.winfo_width()
    height = root.winfo_height()

    header.place(x=0, y=0, width=width, height=95)

    body_width = 1195
    body_y = 112
    footer_height = 52

    body_height = height - body_y - footer_height - 15
    if body_height < 650:
        body_height = 650

    body_x = max((width - body_width) // 2, 20)

    body.place(
        x=body_x,
        y=body_y,
        width=body_width,
        height=body_height
    )

    footer_frame.place(
        x=0,
        y=height - footer_height,
        width=width,
        height=footer_height
    )


# ================= DFA Diagram =================
def draw_dfa_diagram():
    dfa_canvas.delete("all")

    states = [START, L1_Q1, L2_Q1, L2_Q2, L3_Q1, L3_Q2, L3_Q3, L4_Q1, ACCEPT]
    x_start = 35
    y = 48
    gap = 82
    radius = 22

    for i in range(len(states) - 1):
        x1 = x_start + i * gap + radius
        x2 = x_start + (i + 1) * gap - radius
        dfa_canvas.create_line(x1, y, x2, y, fill="#475569", width=2, arrow=tk.LAST)

    for i, state in enumerate(states):
        x = x_start + i * gap

        if state == current_state:
            fill_color = GREEN
            outline_color = TEXT_PRIMARY
        elif current_state == LOCKED:
            fill_color = RED if state == START else BG_CARD_2
            outline_color = RED if state == START else "#475569"
        else:
            fill_color = BG_CARD_2
            outline_color = BORDER

        dfa_canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=fill_color,
            outline=outline_color,
            width=2
        )

        dfa_canvas.create_text(x, y, text=str(i), fill="white", font=("Segoe UI", 9, "bold"))
        dfa_canvas.create_text(x, y + 38, text=state, fill="#cbd5e1", font=("Segoe UI", 7, "bold"))

    if current_state == LOCKED:
        dfa_canvas.create_text(
            205,
            118,
            text="LOCKED / REJECTED",
            fill=RED,
            font=("Segoe UI", 12, "bold")
        )


# ================= GUI Update =================
def update_gui():
    layer, char_type, position, relevant = get_info()

    layer_value.config(text=layer)
    type_value.config(text=char_type)
    position_value.config(text=position)
    relevant_value.config(text=relevant)
    attempt_value.config(text=f"Attempt: {attempt} / 2")
    state_value.config(text=f"Current State: {current_state}")
    password_value.config(text=entered_password)
    progress["value"] = len(entered_password) * 12.5

    session_value.config(text=session_id)
    update_risk_meter()
    draw_dfa_diagram()


def generate_summary():
    total_time = int(time.time() - start_time)
    result = "ACCESS GRANTED" if current_state == ACCEPT else "REJECTED / LOCKED"

    return f"""DFA-Based Secure WiFi Authentication - Summary Report
====================================================

Session ID: {session_id}
Final Status: {result}
Correct Inputs: {correct_inputs}
Wrong Attempts: {wrong_attempts}
Authentication Progress: {len(entered_password)} / 8
Time Taken: {total_time} seconds
Final DFA State: {current_state}
Risk Level: {risk_label.cget("text")}
System Status: {'SECURE' if current_state == ACCEPT else 'LOCKED'}

Generated Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""


def show_summary():
    global last_summary
    last_summary = generate_summary()
    messagebox.showinfo("Authentication Summary", last_summary)


# ================= Timer =================
def update_timer():
    global time_left, current_state, timer_running

    if timer_running:
        timer_label.config(text=f"Session Timer: {time_left}s")
        timer_label.config(fg=RED if time_left <= 10 else YELLOW)

        if time_left <= 0 and current_state not in [ACCEPT, LOCKED]:
            current_state = LOCKED
            timer_running = False
            status_value.config(text="Session timeout. Authentication locked.", fg=RED)
            add_log("Session timeout. System moved to LOCKED state.")
            add_transition_row("ACTIVE", "TIMEOUT", LOCKED, "LOCKED")
            play_sound("lock")
            show_result()
            return

        time_left -= 1
        root.after(1000, update_timer)


# ================= Authentication Logic =================
def handle_valid(previous_state, user_input, next_state, message):
    global current_state, attempt, entered_password, correct_inputs

    current_state = next_state
    attempt = 1
    entered_password += "*"
    correct_inputs += 1

    status_value.config(text=message, fg=GREEN)
    add_log(f"Correct input accepted. Transition: {previous_state} → {next_state}")
    add_transition_row(previous_state, "*", next_state, "VALID")
    play_sound("success")


def handle_second_chance(previous_state, user_input, message):
    global attempt, wrong_attempts

    attempt = 2
    wrong_attempts += 1

    status_value.config(text=message, fg=YELLOW)
    add_log("Wrong but relevant input entered. Second chance activated.")
    add_transition_row(previous_state, "*", previous_state, "SECOND CHANCE")
    play_sound("error")


def handle_locked(previous_state, user_input):
    global current_state, wrong_attempts

    current_state = LOCKED
    wrong_attempts += 1
    add_transition_row(previous_state, "*", current_state, "LOCKED")


def submit_char():
    global current_state

    c = char_entry.get()
    char_entry.delete(0, tk.END)

    if current_state in [ACCEPT, LOCKED]:
        return

    previous_state = current_state

    if len(c) != 1:
        handle_locked(previous_state, "Invalid Length")
        status_value.config(text="Invalid input! Enter only one character.", fg=RED)
        add_log("Invalid input length detected. System locked.")
        play_sound("lock")
        show_result()
        return

    if current_state == START:
        if c == "@":
            handle_valid(previous_state, c, L1_Q1, "Correct! Special character accepted.")
        elif is_special(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong special character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L1_Q1:
        if c == "A":
            handle_valid(previous_state, c, L2_Q1, "Correct! Uppercase character accepted.")
        elif is_uppercase(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong uppercase character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L2_Q1:
        if c == "D":
            handle_valid(previous_state, c, L2_Q2, "Correct! Uppercase character accepted.")
        elif is_uppercase(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong uppercase character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L2_Q2:
        if c == "m":
            handle_valid(previous_state, c, L3_Q1, "Correct! Lowercase character accepted.")
        elif is_lowercase(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong lowercase character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L3_Q1:
        if c == "i":
            handle_valid(previous_state, c, L3_Q2, "Correct! Lowercase character accepted.")
        elif is_lowercase(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong lowercase character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L3_Q2:
        if c == "n":
            handle_valid(previous_state, c, L3_Q3, "Correct! Lowercase character accepted.")
        elif is_lowercase(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong lowercase character but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L3_Q3:
        if c == "1":
            handle_valid(previous_state, c, L4_Q1, "Correct! Digit accepted.")
        elif is_digit(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong digit but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    elif current_state == L4_Q1:
        if c == "2":
            handle_valid(previous_state, c, ACCEPT, "Authentication sequence completed successfully.")
        elif is_digit(c) and attempt == 1:
            handle_second_chance(previous_state, c, "Wrong digit but relevant. Second chance activated.")
        else:
            handle_locked(previous_state, c)

    if current_state == LOCKED:
        add_log("Authentication failed. System moved to LOCKED state.")
        play_sound("lock")
        show_result()
    elif current_state == ACCEPT:
        add_log("Authentication successful. ACCESS GRANTED.")
        show_result()
    else:
        update_gui()


def show_result():
    global timer_running

    timer_running = False
    update_gui()

    char_entry.config(state="disabled")
    submit_btn.config(state="disabled")

    if current_state == ACCEPT:
        final_status.config(text="ACCESS GRANTED", fg=GREEN)
        system_value.config(text="SECURE", fg=GREEN)
        messagebox.showinfo("Success", "Authentication successful. Secure access granted!")
    else:
        final_status.config(text="REJECTED / LOCKED", fg=RED)
        system_value.config(text="LOCKED", fg=RED)
        status_value.config(text="Protocol violated or maximum attempts exceeded.", fg=RED)
        messagebox.showerror("Locked", "Authentication failed. Access terminated!")

    show_summary()
    export_btn.config(state="normal")


def reset_system():
    global current_state, attempt, entered_password, wrong_attempts, correct_inputs
    global time_left, timer_running, start_time, session_id, last_summary

    current_state = START
    attempt = 1
    entered_password = ""
    wrong_attempts = 0
    correct_inputs = 0
    time_left = 60
    timer_running = True
    start_time = time.time()
    session_id = f"DFA-{time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    last_summary = ""

    char_entry.config(state="normal")
    submit_btn.config(state="normal")
    export_btn.config(state="disabled")
    char_entry.delete(0, tk.END)

    final_status.config(text="WAITING", fg=CYAN)
    status_value.config(text="Enter authentication character one by one.", fg=TEXT_PRIMARY)
    progress["value"] = 0

    system_value.config(text="ACTIVE", fg=GREEN)
    encryption_value.config(text="ENABLED", fg=CYAN)
    threat_value.config(text="NORMAL", fg=GREEN)
    unauthorized_value.config(text="0")

    log_box.config(state="normal")
    log_box.delete("1.0", tk.END)
    log_box.config(state="disabled")

    for item in table.get_children():
        table.delete(item)

    add_log("System reset. Authentication session started.")
    update_gui()
    update_timer()


# ================= Main Window =================
root = tk.Tk()
root.title("DFA-Based Secure WiFi Authentication System")
root.geometry("1250x850")
root.minsize(1250, 850)
root.resizable(True, True)

bg_canvas = tk.Canvas(root, highlightthickness=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)


# ================= Tkinter Styles =================
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TProgressbar",
    thickness=22,
    troughcolor="#1e293b",
    background=GREEN,
    bordercolor="#1e293b",
    lightcolor=GREEN,
    darkcolor=GREEN
)

style.configure(
    "Treeview",
    background="#020617",
    foreground="#e5e7eb",
    fieldbackground="#020617",
    rowheight=24,
    font=("Segoe UI", 8)
)

style.configure(
    "Treeview.Heading",
    background="#1e293b",
    foreground="#38bdf8",
    font=("Segoe UI", 8, "bold")
)


# ================= Header =================
header = tk.Frame(root, bg=BG_HEADER)

title = tk.Label(
    header,
    text="DFA-Based Secure WiFi Authentication",
    font=("Segoe UI", 26, "bold"),
    bg=BG_HEADER,
    fg=TEXT_PRIMARY
)
title.pack(pady=(16, 3))

subtitle = tk.Label(
    header,
    text="Cybersecurity Authentication System with Live State Monitoring",
    font=("Segoe UI", 12),
    bg=BG_HEADER,
    fg=TEXT_SECONDARY
)
subtitle.pack()


# ================= Body =================
body = tk.Frame(root, bg=BG_MAIN)


# ================= Left Card =================
left_card = tk.Frame(body, bg=BG_CARD, width=320, height=530, highlightbackground="#1e40af", highlightthickness=2)
left_card.grid(row=0, column=0, padx=10)
left_card.grid_propagate(False)

tk.Label(
    left_card,
    text="Authentication Panel",
    font=("Segoe UI", 17, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(18, 8))

timer_label = tk.Label(left_card, text="Session Timer: 60s", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=YELLOW)
timer_label.pack(pady=3)

session_value = tk.Label(left_card, text=session_id, font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=CYAN)
session_value.pack(pady=2)

risk_label = tk.Label(left_card, text="Risk Level: LOW", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=GREEN)
risk_label.pack(pady=4)

tk.Label(
    left_card,
    text="Enter one character at a time",
    font=("Segoe UI", 10),
    bg=BG_CARD,
    fg=TEXT_SECONDARY
).pack()

char_entry = tk.Entry(
    left_card,
    font=("Segoe UI", 30, "bold"),
    justify="center",
    width=6,
    show="*",
    bg=BG_CARD_2,
    fg=CYAN,
    insertbackground=CYAN,
    relief="flat",
    highlightthickness=3,
    highlightbackground=BLUE,
    highlightcolor=GREEN
)
char_entry.pack(pady=14, ipady=9)

submit_btn = tk.Button(
    left_card,
    text="SUBMIT CHARACTER",
    font=("Segoe UI", 10, "bold"),
    bg=BLUE,
    fg="white",
    activebackground="#0284c7",
    activeforeground="white",
    relief="flat",
    width=23,
    height=2,
    cursor="hand2",
    command=submit_char
)
submit_btn.pack(pady=6)
add_hover(submit_btn, BLUE, "#0284c7")

reset_btn = tk.Button(
    left_card,
    text="RESET SYSTEM",
    font=("Segoe UI", 10, "bold"),
    bg=BUTTON_DARK,
    fg="white",
    activebackground="#475569",
    activeforeground="white",
    relief="flat",
    width=23,
    height=1,
    cursor="hand2",
    command=reset_system
)
reset_btn.pack(pady=5)
add_hover(reset_btn, BUTTON_DARK, "#475569")

export_btn = tk.Button(
    left_card,
    text="EXPORT REPORT",
    font=("Segoe UI", 10, "bold"),
    bg="#16a34a",
    fg="white",
    activebackground="#15803d",
    activeforeground="white",
    relief="flat",
    width=23,
    height=1,
    cursor="hand2",
    command=export_report,
    state="disabled"
)
export_btn.pack(pady=5)
add_hover(export_btn, "#16a34a", "#15803d")

tk.Label(
    left_card,
    text="Authentication Progress",
    font=("Segoe UI", 10, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(17, 6))

progress = ttk.Progressbar(left_card, orient="horizontal", length=250, mode="determinate")
progress.pack()

password_value = tk.Label(left_card, text="", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=CYAN)
password_value.pack(pady=10)

tk.Label(
    left_card,
    text="Security Monitoring",
    font=("Segoe UI", 13, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(12, 5))


def mini_status_row(label, value, color):
    frame = tk.Frame(left_card, bg=BG_CARD)
    frame.pack(fill="x", padx=30, pady=2)

    tk.Label(
        frame,
        text=label,
        font=("Segoe UI", 9, "bold"),
        bg=BG_CARD,
        fg=TEXT_SECONDARY,
        width=16,
        anchor="w"
    ).pack(side="left")

    val = tk.Label(
        frame,
        text=value,
        font=("Segoe UI", 9, "bold"),
        bg=BG_CARD,
        fg=color,
        anchor="w"
    )
    val.pack(side="left")
    return val


system_value = mini_status_row("System:", "ACTIVE", GREEN)
encryption_value = mini_status_row("Encryption:", "ENABLED", CYAN)
threat_value = mini_status_row("Threat:", "NORMAL", GREEN)
unauthorized_value = mini_status_row("Wrong Attempts:", "0", YELLOW)


# ================= Middle Card =================
middle_card = tk.Frame(body, bg=BG_CARD, width=360, height=530, highlightbackground=BORDER, highlightthickness=2)
middle_card.grid(row=0, column=1, padx=10)
middle_card.grid_propagate(False)

tk.Label(
    middle_card,
    text="DFA Live Details",
    font=("Segoe UI", 17, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(18, 12))


def detail_row(label):
    frame = tk.Frame(middle_card, bg=BG_CARD)
    frame.pack(fill="x", padx=25, pady=5)

    tk.Label(
        frame,
        text=label,
        font=("Segoe UI", 10, "bold"),
        bg=BG_CARD,
        fg=TEXT_SECONDARY,
        width=12,
        anchor="w"
    ).pack(side="left")

    value = tk.Label(
        frame,
        text="",
        font=("Segoe UI", 10, "bold"),
        bg=BG_CARD,
        fg=TEXT_PRIMARY,
        anchor="w"
    )
    value.pack(side="left")
    return value


layer_value = detail_row("Layer:")
type_value = detail_row("Type:")
position_value = detail_row("Position:")
relevant_value = detail_row("Relevant:")
attempt_value = detail_row("Attempt:")
state_value = detail_row("State:")

tk.Label(
    middle_card,
    text="Current Status",
    font=("Segoe UI", 11, "bold"),
    bg=BG_CARD,
    fg=TEXT_SECONDARY
).pack(pady=(18, 5))

final_status = tk.Label(
    middle_card,
    text="WAITING",
    font=("Segoe UI", 25, "bold"),
    bg=BG_CARD,
    fg=CYAN
)
final_status.pack()

status_value = tk.Label(
    middle_card,
    text="Enter authentication character one by one.",
    font=("Segoe UI", 10),
    bg=BG_CARD,
    fg=TEXT_PRIMARY,
    wraplength=315,
    justify="center"
)
status_value.pack(pady=8)

tk.Label(
    middle_card,
    text="Live Transition Table",
    font=("Segoe UI", 13, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(15, 5))

table = ttk.Treeview(middle_card, columns=("Current", "Input", "Next", "Status"), show="headings", height=8)
table.heading("Current", text="Current")
table.heading("Input", text="Input")
table.heading("Next", text="Next")
table.heading("Status", text="Status")

table.column("Current", width=78, anchor="center")
table.column("Input", width=55, anchor="center")
table.column("Next", width=78, anchor="center")
table.column("Status", width=95, anchor="center")
table.pack(pady=5)


# ================= Right Card =================
right_card = tk.Frame(body, bg=BG_CARD, width=470, height=530, highlightbackground="#2563eb", highlightthickness=2)
right_card.grid(row=0, column=2, padx=10)
right_card.grid_propagate(False)

tk.Label(
    right_card,
    text="Live DFA Diagram",
    font=("Segoe UI", 17, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(15, 5))

dfa_canvas = tk.Canvas(right_card, width=410, height=130, bg=BG_CARD, highlightthickness=0)
dfa_canvas.pack(pady=5)

tk.Label(
    right_card,
    text="Authentication Logs",
    font=("Segoe UI", 14, "bold"),
    bg=BG_CARD,
    fg=TEXT_PRIMARY
).pack(pady=(8, 5))

log_box = tk.Text(
    right_card,
    height=17,
    width=56,
    bg="#020617",
    fg="#e5e7eb",
    insertbackground="white",
    font=("Consolas", 9),
    relief="flat",
    state="disabled"
)
log_box.pack(pady=5)


# ================= Footer =================
footer_frame = tk.Frame(root, bg=BG_HEADER)

footer = tk.Label(
    footer_frame,
    text="DFA Security Protocol Active   |   Multi-Layer Authentication   |   Real-Time Monitoring   |   Access Control Simulation",
    font=("Segoe UI", 10, "bold"),
    bg=BG_HEADER,
    fg=TEXT_SECONDARY
)
footer.pack(pady=15)


# ================= Program Start =================
char_entry.bind("<Return>", lambda event: submit_char())
root.bind("<Configure>", resize_layout)

add_log("System started. Waiting for authentication input.")
update_gui()
update_timer()
resize_layout()

root.mainloop()