# build_exe.py
import os
import sys
import subprocess

# Nom de ton script à transformer en exe
script_name = "btd_skills_v2.py"

# Optionnel : nom de l'icône (.ico) si tu veux personnaliser l'exe
icon_path = "icon.ico"  # ou None si pas d'icône

# Vérifie que le script existe
if not os.path.isfile(script_name):
    print(f"Error: {script_name} not found in current folder.")
    sys.exit(1)

# Crée la commande PyInstaller
cmd = [
    sys.executable,  # utilise le python actuel
    "-m",
    "PyInstaller",
    "--onefile",     # fichier unique
    "--windowed",    # pas de console
]

if icon_path and os.path.isfile(icon_path):
    cmd += ["--icon", icon_path]

cmd.append(script_name)

# Lance la commande
print("Building executable...")
result = subprocess.run(cmd)

if result.returncode == 0:
    print("Executable built successfully!")
    print("Check the 'dist' folder for your .exe")
else:
    print("Error: Build failed.")
