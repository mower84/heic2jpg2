# HEIC → JPEG (portable)

Приложение без инсталация: избираш HEIC файлове или папка, получаваш JPEG
(запазва EXIF, цветови профил и правилната ориентация).

## Как да получиш .exe и .app (без да инсталираш нищо локално)
1. Създай безплатно хранилище в GitHub и качи тези файлове (с папката `.github`).
2. Раздел **Actions → Build → Run workflow** (или просто push в `main`).
3. След 3–5 мин. в края на изпълнението, в **Artifacts**, ще има:
   - `HEIC2JPG-windows` → `HEIC2JPG.exe`
   - `HEIC2JPG-mac-apple-silicon` → `HEIC2JPG.app` (M1/M2/M3/M4)
   - `HEIC2JPG-mac-intel` → `HEIC2JPG.app` (Intel Mac)

## Първо стартиране
- **Mac:** приложението не е подписано. Десен клик → Open → Open, или в Terminal:
  `xattr -cr HEIC2JPG.app`
- **Windows:** SmartScreen може да предупреди → More info → Run anyway.

## Ръчна компилация (на съответната система)
    pip install -r requirements.txt
    pyinstaller --onefile --windowed --name HEIC2JPG --collect-all pillow_heif heic2jpg.py
(на Mac махни `--onefile`, за да получиш `.app`)
