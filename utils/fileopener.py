import os
import subprocess
directory = r"C:/Users/benja/Downloads/Kossel XL-20231115T144643Z-001"
viewer_program = r"C:/Program Files/Prusa3D/PrusaSlicer/prusa-slicer.exe"

for root, dirs, files in os.walk(directory):
    print("root", root)
    for file in files:
        if file.endswith(".stl"):
            print("file", file)
            file_path = os.path.join(root, file)
            subprocess.run([viewer_program, file_path])
