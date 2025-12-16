import csv

def run(file_path,cutoff):
    results = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            student = row["Student Name"]
            gpa = float(row["Cumulative Average"])
            results[student] = {"has_matching_gpa": gpa >= cutoff}
    return results

            