import os
import shutil


def run():
    print("\nStarting cleanup...")
    root_dir = os.getcwd()
    venv_dir = os.getenv("VIRTUAL_ENV")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            print(f"Deleting {pycache_path}...")
            shutil.rmtree(pycache_path)
        if venv_dir and dirpath.startswith(venv_dir):
            continue
        if "migrations" in dirnames:
            migrations_path = os.path.join(dirpath, "migrations")
            if os.path.exists(migrations_path):
                print(f"Deleting {migrations_path}...")
                shutil.rmtree(migrations_path)
        if "db.sqlite3" in filenames:
            db_path = os.path.join(dirpath, "db.sqlite3")
            print(f"Deleting {db_path}...")
            os.remove(db_path)

    print("Cleanup completed.")
