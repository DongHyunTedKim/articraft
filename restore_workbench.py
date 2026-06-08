import json
import os
import subprocess

# 12 Target workbench records that were unlocked for transfer
target_dirs = [
    "rec_a-1u-rackmount-network-switch-inspired-by-the-ci_20260605_041847_815355_73cad969",
    "rec_a-1u-rackmount-network-switch-inspired-by-the-ci_20260605_041857_644521_73cad969",
    "rec_a-4u-rackmount-8-gpu-server-chassis-in-a-front-a_20260605_013037_558790_666c0444",
    "rec_a-4u-rackmount-8-gpu-server-chassis-in-a-front-a_20260605_020532_722591_50864801",
    "rec_a-4u-rackmount-8-gpu-server-chassis-in-a-front-a_20260605_020538_488600_50864801",
    "rec_a-dell-poweredge-r510-2u-rackmount-server-in-the_20260526_082905_028675_1d9f5a0a",
    "rec_a-dell-poweredge-r510-2u-rackmount-server-in-the_20260526_082916_091873_1d9f5a0a",
    "rec_a-dell-poweredge-r510-2u-rackmount-server-in-the_20260526_083055_623232_1d9f5a0a",
    "rec_a-floor-standing-server-rack-cabinet-a-rectangul_20260526_021814_769769_0f60615f",
    "rec_a-floor-standing-server-rack-cabinet-a-rectangul_20260526_055304_833916_0f60615f",
    "rec_a-floor-standing-server-rack-cabinet-a-rectangul_20260526_064225_081354_0f60615f",
    "rec_a-highly-detailed-4u-rackmount-8gpu-server-chass_20260604_043403_184156_dedc090c",
]

print("Starting restoration of workbench records to local-only status...")

for d in target_dirs:
    record_path = os.path.join("data", "records", d, "record.json")
    if os.path.isfile(record_path):
        try:
            with open(record_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Remove 'dataset' from collections to lock them back under pre-commit hook rules
            if "collections" in data and isinstance(data["collections"], list):
                if "dataset" in data["collections"]:
                    data["collections"] = [c for c in data["collections"] if c != "dataset"]
                    with open(record_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print(f"-> Restored collections in: {record_path}")
        except Exception as e:
            print(f"Error updating {record_path}: {e}")

    # Restore .gitignore file inside the record folder with '*' to ignore contents from git tracking
    gitignore_path = os.path.join("data", "records", d, ".gitignore")
    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# Articraft local workbench record. Do not commit.\n*\n")
        print(f"-> Restored gitignore in: {gitignore_path}")
    except Exception as e:
        print(f"Error updating {gitignore_path}: {e}")

print("\nRestoration complete!")

print("Removing restored records from Git tracking index (keeping local files)...")
for d in target_dirs:
    record_dir = os.path.join("data", "records", d)
    try:
        # Run git rm --cached -r to untrack the record files
        subprocess.run(
            ["git", "rm", "--cached", "-r", record_dir],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"-> Untracked from git: {record_dir}")
    except Exception as e:
        print(f"Failed to untrack {record_dir}: {e}")

print("\nRestoration and untracking complete!")
print("Please run 'git status' to ensure that the record directories are no longer tracked.")
print("You can now safely delete this 'restore_workbench.py' script.")
