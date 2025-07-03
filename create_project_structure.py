import os

base_path = "ui/gui/theme"
os.makedirs(base_path, exist_ok=True)

files = ["colors.py", "fonts.py", "stylesheet.qss"]
for file in files:
    with open(os.path.join(base_path, file), "w") as f:
        if file.endswith(".py"):
            f.write("# " + file.replace(".py", "").capitalize() + " module\n")
        elif file == "stylesheet.qss":
            f.write("""\
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}
QPushButton {
    background-color: #3a3a3a;
    border: none;
    border-radius: 5px;
    padding: 8px;
}
QPushButton:hover {
    background-color: #505050;
}
""")

print("🎨 'theme' klasörü ve stil dosyaları oluşturuldu.")