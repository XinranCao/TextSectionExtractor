import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import threading
import chardet

# Function to detect the encoding of a given file
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        return chardet.detect(file.read())['encoding']

# Function to extract sections from a file based on user-specified keywords
def extract_sections(file_path, user_keywords):
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as file:
        text = file.read()

    # Find all unique keywords in the text (formatted as "_KEYWORD.")
    all_keywords = set(re.findall(r"_(\w+)\.", text))

    # Prepare a dictionary for the sections to be extracted
    sections = {keyword: '' for keyword in user_keywords}

    # Construct a regex pattern to split the text into parts
    pattern = '(' + '|'.join(re.escape(f"_{keyword}.") for keyword in all_keywords) + ')'
    
    parts = re.split(pattern, text)
    current_keyword = None
    for part in parts:
        if part in [f"_{keyword}." for keyword in all_keywords]:  # Check if the part is a keyword
            current_keyword = part[1:-1]  # Update current_keyword without underscore and period
        else:
            if current_keyword and current_keyword in user_keywords:
                sections[current_keyword] += part.strip() + '\n\n'

    return sections

# Function to compile sections from all files in a folder
def compile_sections(input_folder_path, keywords):
    files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]
    total_files = len(files)
    progress['maximum'] = total_files
    compiled_sections = {keyword: '' for keyword in keywords}

    for index, file in enumerate(files, start=1):
        file_path = os.path.join(input_folder_path, file)
        try:
            sections = extract_sections(file_path, compiled_sections.keys())  # Use formatted keywords
            for key, content in sections.items():
                compiled_sections[key] += content + '\n\n'
            progress['value'] = index
            app.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return

    # Prompt for the output folder after extraction
    output_folder_path = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder_path:
        messagebox.showwarning("Warning", "Output folder not selected. Extraction cancelled.")
        return

    for key, content in compiled_sections.items():
        with open(f'{output_folder_path}/{key}.txt', 'w', encoding='utf-8') as file:
            file.write(content)

    messagebox.showinfo("Information", "Extraction complete. Files saved in the selected output folder.")
    progress['value'] = 0

# Function to add a keyword to the GUI interface
def add_keyword():
    keyword = keyword_entry.get().strip()
    formatted_keyword = f"_{keyword}."
    if keyword and formatted_keyword not in keywords:
        keywords.add(formatted_keyword)  # Add the formatted keyword
        row = tk.Frame(main_frame)
        label = tk.Label(row, text=formatted_keyword)
        delete_button = tk.Button(row, text="Delete", command=lambda: delete_keyword(row, formatted_keyword))
        row.pack(fill='x')
        label.pack(side='left')
        delete_button.pack(side='right')
        keyword_rows[formatted_keyword] = row
    elif keyword:
        messagebox.showinfo("Duplicate Keyword", "This keyword is already added.")
    keyword_entry.delete(0, tk.END)

# Function to delete a specified keyword from the GUI interface
def delete_keyword(row, keyword):
    row.destroy()
    keywords.remove(keyword)

# Function to select a folder through a dialog
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_label.config(text=f"Selected Folder: {folder_path}")
        return folder_path
    return ""

# Function to start the extraction process
def start_extraction():
    input_folder_path = filedialog.askdirectory(title="Select Input Folder")
    if input_folder_path:
        folder_label.config(text=f"Selected Input Folder: {input_folder_path}")
        if keywords:
            threading.Thread(target=lambda: compile_sections(input_folder_path, [k[1:-1] for k in keywords]), daemon=True).start()
        else:
            messagebox.showwarning("Warning", "Please enter at least one keyword.")

# Setting up the Tkinter GUI
app = tk.Tk()
app.title("Section Extractor")

# Set the window size
window_width = 500
window_height = 400
app.geometry(f'{window_width}x{window_height}')

# Get screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calculate position x, y
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)
app.geometry(f'+{int(x)}+{int(y)}')

# Data structures to hold keywords and their corresponding rows in the GUI
keywords = set()
keyword_rows = {}

# Main frame of the GUI
main_frame = tk.Frame(app)
main_frame.pack(padx=10, pady=10)

# Label and Entry for keyword input
keyword_label = tk.Label(main_frame, text="Please enter only the word. It will be formatted automatically.", wraplength=300)
keyword_label.pack(pady=10)
keyword_entry = tk.Entry(main_frame)
keyword_entry.pack(fill='x', expand=True)

# Button to add keywords to the list
add_button = tk.Button(main_frame, text="Add Keyword", command=add_keyword)
add_button.pack()

# Button to select folder and start the extraction process
start_button = tk.Button(app, text="Select Folder and Start Extraction", command=start_extraction)
start_button.pack(pady=10)
folder_label = tk.Label(app, text="No Folder Selected", wraplength=300)
folder_label.pack(pady=10)

# Progress bar to show the progress of the extraction process
progress = ttk.Progressbar(app, orient=tk.HORIZONTAL, length=100, mode='determinate')
progress.pack(pady=10)

# Start the Tkinter event loop
app.mainloop()