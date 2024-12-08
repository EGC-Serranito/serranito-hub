file_path = 'app/__init__.py'

with open(file_path, 'r') as file:
    lines = file.readlines()

lines = lines[:-1]

lines.append("app = create_app(config_name='filess')\n")

with open(file_path, 'w') as file:
    file.writelines(lines)

print("Última línea reemplazada con éxito.")
