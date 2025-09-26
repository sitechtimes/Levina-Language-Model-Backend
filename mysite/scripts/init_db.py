from .utils import run_django_command


def run():
    print("\nInitializing database...")
    migration_commands = [
        "makemigrations users",
        "migrate users",
        "makemigrations courses",
        "migrate courses",
        "makemigrations assignments",
        "migrate assignments",
        "makemigrations guidance",
        "migrate guidance",
        "migrate",
    ]

    for command in migration_commands:
        run_django_command(command)

    print("Database initialized.")
