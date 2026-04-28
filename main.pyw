import pyperclip
from pynput import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import time
import threading
import requests
import queue
import json
import matplotlib.pyplot as plt
import os
import shutil
import math
from PIL import Image, ImageTk

# --- AYARLAR ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "gemini-3-flash-preview" 
TEXT_MODEL_CANDIDATES = [MODEL_ADI]
KISAYOL_METIN = keyboard.Key.f8

# Global Değişkenler
root = None
gui_queue = queue.Queue()
kisayol_basildi = False

# --- PROMPT TASLAĞI ---
ORTAK_PROMPT = (
    "Aşağıdaki metni analiz et ve teknik verileri sayısal olarak çıkar. "
    "Cevabını KESİNLİKLE şu formatta ver:\n\n"
    "---VERI---\n"
    "{\"Ürün 1\": {\"Özellik\": rakam}, \"Ürün 2\": {\"Özellik\": rakam}}\n"
    "---YORUM---\n"
    "Verilere dayanarak acımasız ve net bir karşılaştırma yorumu yaz."
)

ISLEMLER = {
    "📊 Verileri Analiz Et ve Sütun Grafiği ile Karşılaştır": ORTAK_PROMPT,
    "🕸️ Teknik Özellikleri Radar Grafiği ile Görselleştir": ORTAK_PROMPT,
}

def get_available_text_model():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return MODEL_ADI
    except: pass
    return MODEL_ADI

def ollama_cevap_al(prompt):
    try:
        payload = {
            "model": get_available_text_model(),
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "top_p": 0.9},
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except: return None

def strip_code_fence(text):
    if not text: return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:-1] if len(lines) > 2 else lines
        cleaned = "\n".join(lines).strip()
    return cleaned

def secili_metni_kopyala():
    sentinel = f"__AI_ASISTAN__{time.time_ns()}__"
    pyperclip.copy(sentinel)
    for _ in range(4):
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        metin = pyperclip.paste()
        if metin and metin.strip() and metin != sentinel: return metin
    return ""

def grafik_olustur(veri_metni, komut_adi, dosya_adi="temp_graph.png"):
    try:
        veri_metni = strip_code_fence(veri_metni.strip())
        if veri_metni.lower().startswith("json"): veri_metni = veri_metni[4:].strip()
        data = json.loads(veri_metni)
        labels = list(data.keys())
        attributes = []
        for l in labels:
            for a in data[l].keys():
                if a not in attributes: attributes.append(a)
        
        if "Sütun" in komut_adi:
            fig, ax = plt.subplots(figsize=(7, 4))
            x = list(range(len(attributes)))
            width = 0.8 / len(labels)
            for i, label in enumerate(labels):
                vals = [float(data[label].get(a, 0)) for a in attributes]
                ax.bar([p + (i - len(labels)/2 + 0.5) * width for p in x], vals, width, label=label)
            
            ax.set_ylabel('Değerler')
            ax.set_title('Özellik Karşılaştırma Grafiği')
            ax.set_xticks(x)
            # YAZILARIN BİRBİRİNE GİRMESİNİ ENGELLEYEN 45 DERECE EĞİM AYARI
            ax.set_xticklabels(attributes, rotation=45, ha='right', fontsize=9)
            ax.legend()
        
        elif "Radar" in komut_adi:
            angles = [n / float(len(attributes)) * 2 * math.pi for n in range(len(attributes))]
            angles += angles[:1]
            fig, ax = plt.subplots(figsize=(7, 4), subplot_kw=dict(polar=True))
            
            max_vals = {a: max([float(data[l].get(a, 0)) for l in labels]) or 1 for a in attributes}
            for label in labels:
                vals = [float(data[label].get(a, 0)) / max_vals[a] for a in attributes]
                vals += vals[:1]
                ax.plot(angles, vals, linewidth=2, label=label)
                ax.fill(angles, vals, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(attributes)
            ax.set_yticklabels([])
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))

        plt.tight_layout()
        plt.savefig(dosya_adi, dpi=100)
        plt.close()
        return True, data
    except: return False, None

def sonuc_penceresi_goster(baslik, icerik, resim_yolu=None, ham_veri=None):
    pencere = tk.Toplevel(root)
    pencere.title(baslik)
    pencere.geometry("820x820")
    pencere.configure(bg="#1f1f1f")
    pencere.attributes("-topmost", True)

    canvas = tk.Canvas(pencere, bg="#1f1f1f", highlightthickness=0)
    scrollbar = tk.Scrollbar(pencere, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#1f1f1f")
    
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if resim_yolu and os.path.exists(resim_yolu):
        img = Image.open(resim_yolu)
        img.thumbnail((750, 380), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(scroll_frame, image=photo, bg="#1f1f1f")
        lbl.image = photo
        lbl.pack(pady=10)

    if ham_veri:
        t_frame = tk.Frame(scroll_frame, bg="#1f1f1f")
        t_frame.pack(fill="x", padx=20)
        urunler = list(ham_veri.keys())
        tree = ttk.Treeview(t_frame, columns=["Ö"]+urunler, show="headings", height=3)
        tree.heading("Ö", text="Özellik")
        for u in urunler: tree.heading(u, text=u); tree.column(u, width=100, anchor="center")
        
        attrs = []
        for u in urunler:
            for a in ham_veri[u].keys():
                if a not in attrs: attrs.append(a)
        for a in attrs:
            tree.insert("", "end", values=[a] + [ham_veri[u].get(a, "-") for u in urunler])
        tree.pack(fill="x")

    txt = tk.Text(scroll_frame, wrap="word", bg="#2b2b2b", fg="white", height=8, font=("Segoe UI", 10), padx=10, pady=10)
    txt.pack(fill="x", padx=20, pady=10)
    txt.insert("1.0", icerik)
    txt.config(state="disabled")

    b_frame = tk.Frame(scroll_frame, bg="#1f1f1f")
    b_frame.pack(fill="x", padx=20, pady=10)

    tk.Button(b_frame, text="📋 Yorumu Kopyala", command=lambda: pyperclip.copy(icerik), bg="#3d3d3d", fg="white", relief="flat", padx=10).pack(side="left", padx=5)
    
    if resim_yolu:
        def kaydet():
            y = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if y: shutil.copy(resim_yolu, y); messagebox.showinfo("Başarılı", "Grafik kaydedildi!")
        tk.Button(b_frame, text="💾 GRAFİĞİ KAYDET", command=kaydet, bg="#0f766e", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=15).pack(side="left", padx=5)

    tk.Button(b_frame, text="Kapat", command=pencere.destroy, bg="#3d3d3d", fg="white", relief="flat", padx=10).pack(side="right", padx=5)

def islemi_yap(k, m):
    s = ollama_cevap_al(f"{ISLEMLER[k]}:\n\n'{m}'")
    if s and "---VERI---" in s:
        try:
            parts = s.split("---YORUM---")
            v = parts[0].split("---VERI---")[1].strip()
            y = parts[1].strip()
            ok, ham = grafik_olustur(v, k)
            gui_queue.put((sonuc_penceresi_goster, (k, y, "temp_graph.png" if ok else None, ham)))
        except: pass

def menu_goster():
    m = secili_metni_kopyala()
    if not m.strip(): return
    menu = tk.Menu(root, tearoff=0, bg="#2b2b2b", fg="white")
    for k in ISLEMLER.keys():
        menu.add_command(label=k, command=lambda c=k: threading.Thread(target=islemi_yap, args=(c, m), daemon=True).start())
    px, py = pyautogui.position()
    menu.tk_popup(px, py)

def process_queue():
    while not gui_queue.empty():
        f, a = gui_queue.get(); f(*a)
    root.after(100, process_queue)

if __name__ == "__main__":
    keyboard.Listener(on_press=lambda k: gui_queue.put((menu_goster, ())) if k == KISAYOL_METIN else None).start()
    root = tk.Tk()
    root.withdraw()
    process_queue()
    root.mainloop()