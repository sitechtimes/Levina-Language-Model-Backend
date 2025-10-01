from .utils import run_django_command


def run():
    reset = input("Are you sure you want to reset the database? (y/n) ").lower()
    if reset == "y":
        script_commands = [
            "runscript purge_db",
            "runscript init_db",
            "runscript reset_test_data",
        ]

        for command in script_commands:
            run_django_command(command)
