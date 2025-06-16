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
    selection = file_list.curselection()
    if not selection:
        return
    file_name = file_list.get(selection[0])
    path = os.path.join(FOLDER_PATH, file_name)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, content)
    root.title(f"Redigerar: {file_name}")
    current_file.set(file_name)

def new_file():
    name = simpledialog.askstring("Ny fil", "Ange nytt filnamn (utan .txt):")
    if name:
        file_name = name.strip() + ".txt"
        path = os.path.join(FOLDER_PATH, file_name)
        if os.path.exists(path):
            messagebox.showwarning("Fil finns redan", "En fil med det namnet finns redan.")
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        update_file_list()
        file_list.selection_set(tk.END)
        open_file()

def save_file():
    file_name = current_file.get()
    if not file_name:
        messagebox.showwarning("Ingen fil", "Öppna eller skapa en fil först.")
        return
    path = os.path.join(FOLDER_PATH, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text_box.get("1.0", tk.END).strip())
    messagebox.showinfo("Sparad", f"{file_name} har sparats.")

def open_translate_menu():
    if not current_file.get():
        messagebox.showwarning("Ingen fil", "Öppna eller skapa en fil först.")
        return

    menu = tk.Toplevel(root)
    menu.title("Välj språk för översättning")
    menu.transient(root)
    menu.grab_set()

    # Center the menu on the root window
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
            text_box.insert(tk.END, translated)
            menu.destroy()
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

text_box = tk.Text(frame_right, wrap="word")
text_box.pack(fill=tk.BOTH, expand=True)

# Initiera listan
update_file_list()

root.mainloop()
