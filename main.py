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
                # Превращаем путь в имя модуля: hbrute/core/banner.py -> hbrute.core.banner
                mod_name = name.replace("/", ".").replace("\\", ".")
                if mod_name.endswith(".__init__.py"):
                    mod_name = mod_name[:-12]
                    is_pkg = True
                else:
                    mod_name = mod_name[:-3]
                    is_pkg = False
                
                self.modules[mod_name] = {"path": name, "is_pkg": is_pkg}

    def find_spec(self, fullname, path, target=None):
        if fullname in self.modules:
            spec = importlib.util.spec_from_loader(fullname, self)
            if self.modules[fullname]["is_pkg"]:
                spec.submodule_search_locations = [fullname]
            return spec
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        mod_info = self.modules[module.__name__]
        code = self.zip_file.read(mod_info["path"])
        if mod_info["is_pkg"]:
            module.__path__ = [module.__name__]
        exec(code, module.__dict__)

def start():
    # Список мест для поиска hbrute.data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "hbrute.data"),
        "hbrute.data"
    ]
    
    data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            data_path = path
            break

    if not data_path:
        print("[!] Ошибка: hbrute.data не найден.")
        print(f"[*] Проверено в: {possible_paths}")
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
