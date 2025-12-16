from .utils import run_django_command
run_django_command("")
from users.models import CustomUser


def run(gpa_dict):
    for full_name, data in gpa_dict.items():
        try:
            last,first = [s.strip() for s in full_name.split(",")]
            print(f"this is last {last} and first {first}")
            user = CustomUser.objects.get(first_name=first, last_name=last)
            user.meets_gpa_req = data["has_matching_gpa"]
            user.save()
        except CustomUser.DoesNotExist:
            print(f"User not found: {full_name}")
