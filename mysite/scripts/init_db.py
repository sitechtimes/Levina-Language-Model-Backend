from .utils import run_django_command


def run():
    print("\nInitializing database...")
    migration_commands = [
        "makemigrations users",
        "migrate users",
        "makemigrations assignments",
        "migrate assignments",
        "makemigrations questions",
        "migrate questions",
        "makemigrations courses",
        "migrate courses",
        "migrate",
    ]

    for command in migration_commands:
        run_django_command(command)

    print("Database initialized.")
