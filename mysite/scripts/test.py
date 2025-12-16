from scripts.check_gpa_csv import run as check_gpa_from_csv
from scripts.update_meets_gpa import run as update_meets_gpa

results = check_gpa_from_csv("../test.csv", 3)
print(results)
results2electricboogaloo = update_meets_gpa(results)
