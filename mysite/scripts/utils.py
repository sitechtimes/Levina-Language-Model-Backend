import subprocess, random, string, sys, os


def run_django_command(command):
    if sys.platform.startswith("win"):
        python_executable = os.path.join(sys.prefix, "Scripts", "python.exe")
        django_command = f"{python_executable} manage.py {command}"
    else:
        python_executable = os.path.join(sys.prefix, "bin", "python3")
        django_command = f"{python_executable} manage.py {command}"

    try:
        process = subprocess.Popen(
            django_command,
            shell=True,
            stdout=None,
            stderr=None,
            text=True,
        )
        return_code = process.wait()
        if return_code != 0:
            print(f"Process finished with return code: {return_code}")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        if process.poll() is None:
            process.terminate()


def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))
