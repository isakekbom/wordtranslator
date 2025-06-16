import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import os
import translation

FOLDER_PATH = "./textfiler"  # Alla textfiler sparas här

# Skapa mapp om den inte finns
os.makedirs(FOLDER_PATH, exist_ok=True)

# ----- Funktioner -----

def update_file_list():
    file_list.delete(0, tk.END)
    files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".txt")]
    for f in files:
        file_list.insert(tk.END, f)

def open_file(event=None):
    global source_language, edit_mode, edit_target_language
    selection = file_list.curselection()
    if not selection:
        return
    file_name = file_list.get(selection[0])
    path = os.path.join(FOLDER_PATH, file_name)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if lines and lines[0].startswith("# language:"):
        source_language = lines[0].strip().split(":", 1)[1].strip()
        content = "".join(lines[1:])
    else:
        source_language = "Unknown"
        content = "".join(lines)
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, content)
    root.title(f"Redigerar: {file_name} ({source_language})")
    current_file.set(file_name)
    # Reset edit mode
    edit_mode = False
    edit_target_language = None
    edit_mode_label.config(text="")

def new_file():
    name = simpledialog.askstring("Ny fil", "Ange nytt filnamn (utan .txt):")
    if name:
        file_name = name.strip() + ".txt"
        path = os.path.join(FOLDER_PATH, file_name)
        if os.path.exists(path):
            messagebox.showwarning("Fil finns redan", "En fil med det namnet finns redan.")
            return

        # Dropdown for source language selection
        lang_win = tk.Toplevel(root)
        lang_win.title("Välj källspråk")
        lang_win.transient(root)
        lang_win.grab_set()
        tk.Label(lang_win, text="Välj källspråk:").pack(pady=5)
        language_var = tk.StringVar()
        languages = ["English", "Swedish", "Spanish", "French", "German"]
        language_dropdown = ttk.Combobox(lang_win, textvariable=language_var, values=languages, state="readonly")
        language_dropdown.pack(pady=5)
        language_dropdown.set(languages[0])

        def create_file():
            lang = language_var.get()
            if not lang or lang not in languages:
                messagebox.showwarning("Fel", "Du måste välja ett giltigt språk.")
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# language: {lang}\n")
            lang_win.destroy()
            update_file_list()
            file_list.selection_set(tk.END)
            open_file()

        button_frame = tk.Frame(lang_win)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", width=8, command=create_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Avbryt", width=8, command=lang_win.destroy).pack(side=tk.LEFT, padx=5)

def save_file():
    global edit_mode, edit_target_language, source_language
    file_name = current_file.get()
    if not file_name:
        messagebox.showwarning("Ingen fil", "Öppna eller skapa en fil först.")
        return
    path = os.path.join(FOLDER_PATH, file_name)

    # Read the first line (language) if it exists
    language_line = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].startswith("# language:"):
            language_line = lines[0]
        else:
            language_line = f"# language: {source_language}\n"

    # Get the text to save (excluding the language line)
    text_to_save = text_box.get("1.0", tk.END).strip()
    if edit_mode and edit_target_language and source_language and edit_target_language != source_language:
        try:
            # Translate back to source language before saving
            text_to_save = translation.translate_text(text_to_save, source_language)
            messagebox.showinfo("Sparad", f"Texten har översatts tillbaka till {source_language} och sparats.")
        except Exception as e:
            messagebox.showerror("Fel vid översättning tillbaka", str(e))
            return
        # Reset edit mode after saving
        edit_mode = False
        edit_target_language = None
        edit_mode_label.config(text="")

    # Always write the language line first, then the content
    with open(path, "w", encoding="utf-8") as f:
        f.write(language_line)
        if text_to_save:
            f.write(text_to_save if text_to_save.startswith("\n") else "\n" + text_to_save)
    messagebox.showinfo("Sparad", f"{file_name} har sparats.")

        # Refresh file selection and reload content
    files = list(file_list.get(0, tk.END))
    if file_name in files:
        idx = files.index(file_name)
        file_list.selection_clear(0, tk.END)
        file_list.selection_set(idx)
        file_list.activate(idx)
    open_file()

def open_translate_menu():
    global edit_mode, edit_target_language
    if not current_file.get():
        messagebox.showwarning("Ingen fil", "Öppna eller skapa en fil först.")
        return

    menu = tk.Toplevel(root)
    menu.title("Välj språk för översättning")
    menu.transient(root)
    menu.grab_set()

    menu.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (200 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (150 // 2)
    menu.geometry(f"200x150+{x}+{y}")

    tk.Label(menu, text="Välj språk:").pack(pady=5)
    language_var = tk.StringVar()
    languages = ["English", "Swedish", "Spanish", "French", "German"]
    language_dropdown = ttk.Combobox(menu, textvariable=language_var, values=languages, state="readonly")
    language_dropdown.pack(pady=5)
    language_dropdown.set("English")

    def do_translate():
        global edit_mode, edit_target_language
        target_language = language_var.get()
        if not target_language:
            messagebox.showwarning("Språk saknas", "Välj ett språk.")
            return
        original_text = text_box.get("1.0", tk.END).strip()
        if not original_text:
            messagebox.showwarning("Ingen text", "Det finns ingen text att översätta.")
            return
        try:
            translated = translation.translate_text(original_text, target_language)
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, translated if translated is not None else "")
            menu.destroy()
            # Set edit mode and show indicator
            edit_mode = True
            edit_target_language = target_language
            edit_mode_label.config(text=f"Redigerar i {target_language} (översätts tillbaka vid spara)")
        except Exception as e:
            messagebox.showerror("Fel vid översättning", str(e))

    button_frame = tk.Frame(menu)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="OK", width=8, command=do_translate).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Avbryt", width=8, command=menu.destroy).pack(side=tk.LEFT, padx=5)

# ----- GUI Setup -----

root = tk.Tk()
root.title("Textfilhanterare")

current_file = tk.StringVar()

edit_mode = False
edit_target_language = None
source_language = None


# Vänstersida: Filval
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Label(frame_left, text="Textfiler:").pack()
file_list = tk.Listbox(frame_left, height=20, width=30)
file_list.pack()
file_list.bind("<<ListboxSelect>>", open_file)

tk.Button(frame_left, text="Skapa ny fil", command=new_file).pack(pady=5)
tk.Button(frame_left, text="Spara ändringar", command=save_file).pack()
tk.Button(frame_left, text="Redigera i annat språk", command=open_translate_menu).pack(pady=5)

# Högersida: Textredigerare
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

edit_mode_label = tk.Label(frame_right, text="", fg="red")
edit_mode_label.pack(anchor="ne")

text_box = tk.Text(frame_right, wrap="word")
text_box.pack(fill=tk.BOTH, expand=True)

# Initiera listan
update_file_list()

root.mainloop()
