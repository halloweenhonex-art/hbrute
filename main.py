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
                # Нормализуем путь в имя модуля
                clean_name = name.replace("/", ".").replace("\\", ".")
                if clean_name.endswith(".__init__.py"):
                    mod_name = clean_name[:-12]
                else:
                    mod_name = clean_name[:-3]
                
                # Игнорируем пустые имена и внешние файлы
                if mod_name:
                    self.modules[mod_name] = name
        
        # Добавляем родительские пакеты, если их нет
        all_mods = list(self.modules.keys())
        for mod in all_mods:
            parts = mod.split(".")
            for i in range(1, len(parts)):
                parent = ".".join(parts[:i])
                if parent not in self.modules:
                    self.modules[parent] = None # Маркер чистого пакета

    def find_spec(self, fullname, path, target=None):
        if fullname in self.modules:
            spec = importlib.util.spec_from_loader(fullname, self)
            # Если это пакет (есть __init__ или это родитель), помечаем его
            is_pkg = self.modules[fullname] is None or self.modules[fullname].endswith("__init__.py")
            if is_pkg:
                spec.submodule_search_locations = [] 
            return spec
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path = self.modules[module.__name__]
        if path:
            code = self.zip_file.read(path)
            exec(code, module.__dict__)
        else:
            # Для пустых родительских пакетов просто помечаем как пакет
            module.__path__ = []

def start():
    # Список мест для поиска hbrute.data
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "hbrute.data"), # Рядом со скриптом
        os.path.join(sys.prefix, "hbrute.data"), # В корне Python или VENV
        os.path.join(sys.prefix, "local", "hbrute.data"), # Стандарт для некоторых систем
        os.path.join(sys.prefix, "bin", "hbrute.data"), # Для Linux/macOS
        os.path.join(sys.prefix, "Scripts", "hbrute.data"), # Для Windows
        "hbrute.data" # В текущей папке
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
