import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz
import os
import argparse
import sys
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

# @Author: AccaEmme
# @Created on: 10th of November 2025
# @Last Update: 11th of November 2025
# @GitHub: https://github.com/AccaEmme/PDF-Toolkit

# Esempi:
# Aggiungi password
# python pdf_toolkit.py addpw input.pdf output.pdf miaPassword123
#
# Rimuovi password
# python pdf_toolkit.py removepw protetto.pdf sbloccato.pdf miaPassword123
#
# Cracca password (usa dizionario)
# python pdf_toolkit.py crackpw protetto.pdf sbloccato.pdf passwords.txt

# ------------------ Funzioni PDF ------------------

def compress_pdf(input_path, output_path, dpi=50): # 72. dpi basso = meno qualità, più compressione
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=int(dpi))
            img_path = f"temp_page_{i}.png"
            pix.save(img_path)
            img_pdf = fitz.open()
            rect = fitz.Rect(0, 0, pix.width, pix.height)
            page_img = img_pdf.new_page(width=rect.width, height=rect.height)
            page_img.insert_image(rect, filename=img_path)
            new_doc.insert_pdf(img_pdf)
            os.remove(img_path)
        new_doc.save(output_path)
        print(f"[✓] PDF compresso salvato in: {output_path}")
    except Exception as e:
        print(f"[!] Errore nella compressione: {e}")

def merge_pdfs(file_list, output_path):
    try:
        merger = PdfMerger()
        for f in file_list:
            merger.append(f)
        merger.write(output_path)
        merger.close()
        print(f"[✓] PDF uniti in: {output_path}")
    except Exception as e:
        print(f"[!] Errore nell'accorpamento: {e}")

def split_pdf(input_path):
    try:
        reader = PdfReader(input_path)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = f"{input_path[:-4]}_page_{i+1}.pdf"
            with open(output_path, "wb") as f:
                writer.write(f)
        print("[✓] PDF diviso in pagine singole.")
    except Exception as e:
        print(f"[!] Errore nello split: {e}")

def add_password(input_path, output_path, password):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"[✓] Password aggiunta: {output_path}")
    except Exception as e:
        print(f"[!] Errore: {e}")

def remove_password(input_path, output_path, password):
    try:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"[✓] Password rimossa: {output_path}")
    except Exception as e:
        print(f"[!] Errore: {e}")

def crack_password(input_path, output_path, wordlist):
    try:
        reader = PdfReader(input_path)
        if not reader.is_encrypted:
            print("[!] Il file non è protetto da password.")
            return "non_protetto"

        with open(wordlist, "r") as f:
            for line in f:
                pwd = line.strip()
                try:
                    reader.decrypt(pwd)
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    with open(output_path, "wb") as out:
                        writer.write(out)
                    print(f"[✓] Password trovata: {pwd}")
                    return pwd
                except:
                    continue

        print("[!] Nessuna password trovata nel dizionario.")
        return None

    except Exception as e:
        print(f"[!] Errore: {e}")
        return None


# ------------------ GUI ------------------

def launch_gui():
    root = tk.Tk()
    root.title("PDF Toolkit")
    root.geometry("1100x400")
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Home
    home_frame = ttk.Frame(notebook)
    notebook.add(home_frame, text="🏠 Home")
    tk.Label(home_frame, text="Benvenuto nel PDF Toolkit!", font=("Arial", 14)).pack(pady=10)
    tk.Label(home_frame, text="Funzionalità:\n- Compressione\n- Accorpamento\n- Split\n- CLI support", justify="left").pack(pady=10)

     # Scheda Compressore PDF
    compress_frame = ttk.Frame(notebook)
    notebook.add(compress_frame, text="📉 Compressore PDF")

    tk.Label(compress_frame, text="Seleziona il file PDF da comprimere:").pack(pady=5)
    selected_file_var = tk.StringVar()
    tk.Entry(compress_frame, textvariable=selected_file_var, width=50).pack(pady=5)

    def select_pdf_file():
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            selected_file_var.set(path)

    tk.Button(compress_frame, text="📂 Seleziona PDF", command=select_pdf_file).pack(pady=5)

    tk.Label(compress_frame, text="DPI (qualità):").pack(pady=5)
    dpi_var = tk.IntVar(value=50)

    dpi_label = tk.Label(compress_frame, text="", font=("Arial", 10), fg="blue")
    dpi_label.pack(pady=5)

    def update_dpi_label(value):
        dpi = int(value)
        if dpi < 30:
            text = "⚠️ DPI troppo basso: qualità illeggibile"
        elif dpi <= 50:
            text = "50 DPI → ottimo compromesso per file leggibili e leggeri"
        elif dpi <= 72:
            text = "72 DPI → qualità standard per schermo"
        elif dpi <= 150:
            text = "150 DPI → buona qualità per stampa leggera"
        else:
            text = "⚠️ DPI elevato: file più pesante, qualità alta"
        dpi_label.config(text=f"Range pratico consigliato: 30–150 DPI\n{text}")

    dpi_spin = tk.Spinbox(compress_frame, from_=30, to=300, increment=10, textvariable=dpi_var, width=10, command=lambda: update_dpi_label(dpi_var.get()))
    dpi_spin.pack(pady=5)

    tk.Scale(compress_frame, from_=30, to=300, orient="horizontal", variable=dpi_var, command=update_dpi_label).pack(pady=5)

    update_dpi_label(dpi_var.get())

    def gui_compress():
        input_path = selected_file_var.get()
        if not input_path:
            messagebox.showwarning("Attenzione", "Seleziona prima un file PDF.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            compress_pdf(input_path, output_path, dpi_var.get())
            messagebox.showinfo("Successo", f"PDF compresso salvato in:\n{output_path}")

    tk.Button(compress_frame, text="💾 Comprimi e salva", command=gui_compress).pack(pady=20)

    # Accorpa
    merge_frame = ttk.Frame(notebook)
    notebook.add(merge_frame, text="📎 Accorpa PDF")
    def gui_merge():
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        merge_pdfs(files, output_path)
        messagebox.showinfo("Successo", f"PDF uniti in:\n{output_path}")
    tk.Label(merge_frame, text="Unisci più PDF in uno solo").pack(pady=10)
    tk.Button(merge_frame, text="Seleziona PDF da unire", command=gui_merge).pack(pady=20)

    # Splitta
    split_frame = ttk.Frame(notebook)
    notebook.add(split_frame, text="✂️ Splitta PDF")
    def gui_split():
        input_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        split_pdf(input_path)
        messagebox.showinfo("Successo", "PDF diviso in pagine singole.")
    tk.Label(split_frame, text="Dividi un PDF in pagine singole").pack(pady=10)
    tk.Button(split_frame, text="Seleziona PDF da dividere", command=gui_split).pack(pady=20)

    # Scheda Aggiungi Password
    addpw_frame = ttk.Frame(notebook)
    notebook.add(addpw_frame, text="🔐 Aggiungi Password")
    tk.Label(addpw_frame, text="Proteggi un PDF con password").pack(pady=10)
    pw_var = tk.StringVar()
    tk.Entry(addpw_frame, textvariable=pw_var, show="*").pack(pady=5)
    def gui_addpw():
        input_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        add_password(input_path, output_path, pw_var.get())
        messagebox.showinfo("Successo", f"Password aggiunta a:\n{output_path}")
    tk.Button(addpw_frame, text="Seleziona PDF e proteggi", command=gui_addpw).pack(pady=10)

    # Scheda Rimuovi Password
    removepw_frame = ttk.Frame(notebook)
    notebook.add(removepw_frame, text="🔓 Rimuovi Password")
    tk.Label(removepw_frame, text="Rimuovi la password da un PDF").pack(pady=10)
    removepw_var = tk.StringVar()
    tk.Entry(removepw_frame, textvariable=removepw_var, show="*").pack(pady=5)
    def gui_removepw():
        input_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        remove_password(input_path, output_path, removepw_var.get())
        messagebox.showinfo("Successo", f"Password rimossa da:\n{output_path}")
    tk.Button(removepw_frame, text="Seleziona PDF e rimuovi", command=gui_removepw).pack(pady=10)

    # Scheda Cracca Password
    crackpw_frame = ttk.Frame(notebook)
    notebook.add(crackpw_frame, text="⚠️ Cracca Password")
    tk.Label(crackpw_frame, text="Recupera PDF protetto usando dizionario").pack(pady=10)
    def gui_crackpw():
        input_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        wordlist_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        result = crack_password(input_path, output_path, wordlist_path)

        if result == "non_protetto":
            messagebox.showinfo("Info", "Il file non è protetto da password.")
        elif result:
            messagebox.showinfo("Successo", f"Password trovata: {result}\nPDF sbloccato salvato in:\n{output_path}")
        else:
            messagebox.showwarning("Fallito", "Nessuna password trovata nel dizionario.")

    tk.Button(crackpw_frame, text="Seleziona PDF e dizionario", command=gui_crackpw).pack(pady=10)

    # About
    about_frame = ttk.Frame(notebook)
    notebook.add(about_frame, text="ℹ️ About Me")
    tk.Label(about_frame, text="PDF Toolkit v1.0", font=("Arial", 12)).pack(pady=10)
    tk.Label(about_frame, text="Creato da AccaEmme\n in data 10 novembre 2025 con last update 11 novembre 2025. Sviluppato in Python e librerie Tkinter e PyMuPDF\nCompatibile con Windows e Linux", justify="center").pack(pady=10)
    tk.Label(about_frame, text="Utilizzabile sia con GUI sia da command line:", justify="center").pack(pady=10)
    tk.Label(about_frame, text="python pdf_toolkit.py compress input.pdf output.pdf --dpi 40", justify="center").pack(pady=10)
    tk.Label(about_frame, text="python pdf_toolkit.py merge file1.pdf file2.pdf file3.pdf output.pdf", justify="center").pack(pady=10)
    tk.Label(about_frame, text="python pdf_toolkit.py split input.pdf", justify="center").pack(pady=10)

    root.mainloop()

# ------------------ CLI ------------------

def parse_cli():
    parser = argparse.ArgumentParser(description="PDF Toolkit - GUI + CLI")
    subparsers = parser.add_subparsers(dest="command")

    compress = subparsers.add_parser("compress", help="Comprime un PDF")
    compress.add_argument("input", help="Percorso del PDF da comprimere")
    compress.add_argument("output", help="Percorso del PDF compresso")
    compress.add_argument("--dpi", type=int, default=50, help="Risoluzione DPI (default: 50)")

    merge = subparsers.add_parser("merge", help="Unisce più PDF")
    merge.add_argument("files", nargs="+", help="Lista di PDF da unire")
    merge.add_argument("output", help="Percorso del PDF finale")

    split = subparsers.add_parser("split", help="Divide un PDF in pagine singole")
    split.add_argument("input", help="Percorso del PDF da dividere")

    # Aggiungi password
    addpw = subparsers.add_parser("addpw", help="Aggiunge una password a un PDF")
    addpw.add_argument("input", help="PDF da proteggere")
    addpw.add_argument("output", help="PDF protetto")
    addpw.add_argument("password", help="Password da impostare")

    # Rimuovi password
    removepw = subparsers.add_parser("removepw", help="Rimuove la password da un PDF")
    removepw.add_argument("input", help="PDF protetto")
    removepw.add_argument("output", help="PDF senza protezione")
    removepw.add_argument("password", help="Password attuale")

    # Cracca password
    crackpw = subparsers.add_parser("crackpw", help="Tenta di craccare la password di un PDF usando un dizionario")
    crackpw.add_argument("input", help="PDF protetto")
    crackpw.add_argument("output", help="PDF sbloccato")
    crackpw.add_argument("wordlist", help="File di testo con lista di password")


    args = parser.parse_args()
    if args.command == "compress":
        compress_pdf(args.input, args.output, args.dpi)
    elif args.command == "merge":
        merge_pdfs(args.files, args.output)
    elif args.command == "split":
        split_pdf(args.input)
    elif args.command == "addpw":
        add_password(args.input, args.output, args.password)
    elif args.command == "removepw":
        remove_password(args.input, args.output, args.password)
    elif args.command == "crackpw":
        result = crack_password(args.input, args.output, args.wordlist)
        if result == "non_protetto":
            print("[!] Il file non è protetto da password.")
        elif result:
            print(f"[✓] Password corretta: {result}")
        else:
            print("[✘] Nessuna password trovata nel dizionario.")

    else:
        launch_gui()

# ------------------ Avvio ------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_cli()
    else:
        launch_gui()
