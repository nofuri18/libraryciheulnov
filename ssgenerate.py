import os

folder = "./screenshots"
files = sorted(os.listdir(folder))

print("| " + " | ".join([f.split(".")[0] for f in files]) + " |")
print("|" + "|".join(["-"*10]*len(files)) + "|")
print("| " + " | ".join([f'<img src="{folder}/{f}" width="200">' for f in files]) + " |")
