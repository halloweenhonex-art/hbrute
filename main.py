import os
import sys
import io
import zipfile
import importlib.abc
import importlib.util
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib

# Тот же ключ, что и в билдере
SECRET_KEY = b"hbrute_god_mode_secret_key_2026"
KEY = hashlib.sha256(SECRET_KEY).digest()

def decrypt_data(data):
    iv = data[:16]
    encrypted = data[16:]
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(decrypted_padded) + unpadder.finalize()

class MemoryLoader(importlib.abc.MetaPathFinder):
    def __init__(self, zip_data):
        self.zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
        self.modules = {}
        for name in self.zip_file.namelist():
            if name.endswith(".py"):
                mod_name = name.replace(".py", "").replace("/", ".").replace("\\", ".")
                # Убираем лишние префиксы если они есть
                self.modules[mod_name] = name

    def find_spec(self, fullname, path, target=None):
        if fullname in self.modules:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path = self.modules[module.__name__]
        code = self.zip_file.read(path)
        exec(code, module.__dict__)

def start():
    # Определяем путь к hbrute.data рядом с исполняемым файлом
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "hbrute.data")
    
    if not os.path.exists(data_path):
        # Если рядом нет, пробуем в текущей папке
        data_path = "hbrute.data"
        if not os.path.exists(data_path):
            print("[!] Ошибка: hbrute.data не найден.")
            return

    try:
        with open(data_path, "rb") as f:
            encrypted_blob = f.read()
        
        # Расшифровка в памяти
        decrypted_zip = decrypt_data(encrypted_blob)
        
        # Регистрация загрузчика из памяти
        sys.meta_path.append(MemoryLoader(decrypted_zip))
        
        # Запуск главного модуля
        import hbrute.main
        hbrute.main.interactive_shell()
        
    except Exception as e:
        print(f"[!] Критическая ошибка загрузки: {e}")

if __name__ == "__main__":
    start()
