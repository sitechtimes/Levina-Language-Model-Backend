from users.models import CustomUser
import sys


def run():
    print("\nCreating superuser...")
    student = CustomUser.objects.create_user(
        email="student@example.com", password="student", user_type=0
    )
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="teacher", user_type=1
    )
    admin = CustomUser.objects.create_user(
        email="admin@example.com", password="admin", user_type=2
    )
    superuser = CustomUser.objects.create_superuser(
        email="superuser@example.com", password="superuser", user_type=3
    )
