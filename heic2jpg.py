import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

EXTS = (".heic", ".heif")


def convert_one(src, out_dir, quality):
    base = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(out_dir, base + ".jpg")
    n = 1
    while os.path.exists(dst):
        dst = os.path.join(out_dir, f"{base}_{n}.jpg")
        n += 1
    with Image.open(src) as im:
        exif = im.getexif()
        im = ImageOps.exif_transpose(im)
        exif[0x0112] = 1  # ориентацията вече е приложена
        icc = im.info.get("icc_profile")
        if im.mode != "RGB":
            im = im.convert("RGB")
        kwargs = {"quality": quality, "optimize": True, "exif": exif.tobytes()}
        if icc:
            kwargs["icc_profile"] = icc
        im.save(dst, "JPEG", **kwargs)
    return dst


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, n) for n in names if n.lower().endswith(EXTS)]
        elif p.lower().endswith(EXTS):
            files.append(p)
    return files


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HEIC → JPEG")
        self.geometry("520x330")
        self.resizable(False, False)
        self.files = []
        self.out_dir = tk.StringVar(value="")
        self.quality = tk.IntVar(value=92)
        self.busy = False

        pad = {"padx": 12, "pady": 6}
        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Button(top, text="Избери файлове…", command=self.pick_files).pack(side="left")
        ttk.Button(top, text="Избери папка…", command=self.pick_folder).pack(side="left", padx=8)

        self.info = ttk.Label(self, text="Няма избрани файлове")
        self.info.pack(anchor="w", **pad)

        out = ttk.Frame(self)
        out.pack(fill="x", **pad)
        ttk.Label(out, text="Изходна папка:").pack(side="left")
        ttk.Entry(out, textvariable=self.out_dir, width=32).pack(side="left", padx=6)
        ttk.Button(out, text="…", width=3, command=self.pick_out).pack(side="left")
        ttk.Label(self, text="(празно = до оригиналните файлове)", foreground="gray").pack(anchor="w", padx=12)

        q = ttk.Frame(self)
        q.pack(fill="x", **pad)
        ttk.Label(q, text="Качество:").pack(side="left")
        ttk.Scale(q, from_=60, to=100, variable=self.quality, orient="horizontal",
                  command=lambda v: self.quality.set(int(float(v))), length=240).pack(side="left", padx=8)
        ttk.Label(q, textvariable=self.quality, width=4).pack(side="left")

        self.bar = ttk.Progressbar(self, length=490)
        self.bar.pack(**pad)
        self.status = ttk.Label(self, text="")
        self.status.pack(anchor="w", padx=12)

        self.btn = ttk.Button(self, text="Конвертирай", command=self.start)
        self.btn.pack(pady=8)

    def set_files(self, files):
        self.files = files
        self.info.config(text=f"Избрани файлове: {len(files)}" if files else "Няма HEIC файлове")

    def pick_files(self):
        paths = filedialog.askopenfilenames(
            title="HEIC файлове",
            filetypes=[("HEIC/HEIF", "*.heic *.HEIC *.heif *.HEIF"), ("Всички", "*.*")])
        if paths:
            self.set_files(collect(paths))

    def pick_folder(self):
        d = filedialog.askdirectory(title="Папка с HEIC файлове")
        if d:
            self.set_files(collect([d]))

    def pick_out(self):
        d = filedialog.askdirectory(title="Изходна папка")
        if d:
            self.out_dir.set(d)

    def start(self):
        if self.busy:
            return
        if not self.files:
            messagebox.showinfo("HEIC → JPEG", "Първо избери файлове или папка.")
            return
        self.busy = True
        self.btn.state(["disabled"])
        self.bar.config(maximum=len(self.files), value=0)
        threading.Thread(target=self.work, daemon=True).start()

    def work(self):
        ok, errors = 0, []
        for i, f in enumerate(self.files, 1):
            try:
                out = self.out_dir.get().strip() or os.path.dirname(f)
                os.makedirs(out, exist_ok=True)
                convert_one(f, out, self.quality.get())
                ok += 1
            except Exception as e:
                errors.append(f"{os.path.basename(f)}: {e}")
            self.after(0, self.progress, i)
        self.after(0, self.done, ok, errors)

    def progress(self, i):
        self.bar.config(value=i)
        self.status.config(text=f"{i} / {len(self.files)}")

    def done(self, ok, errors):
        self.busy = False
        self.btn.state(["!disabled"])
        msg = f"Готово: {ok} от {len(self.files)} файла."
        if errors:
            msg += "\n\nГрешки:\n" + "\n".join(errors[:8])
        messagebox.showinfo("HEIC → JPEG", msg)


if __name__ == "__main__":
    App().mainloop()
