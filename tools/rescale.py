import sys

SCALE = 10

x_list = []
y_list = []
z_list = []
for i, line in enumerate(sys.stdin):
    if i == 0:
        continue
    try:
        if "," in line:
            x, y, z, *_ = line.strip().split(",")
        else:
            x, y, z, *_ = line.strip().split()
        x_list.append(float(x))
        y_list.append(float(y))
        z_list.append(float(z))
    except Exception as e:
        print(line, e, file=sys.stderr)
        print(line)

x_max = max(x_list)
x_min = min(x_list)

y_max = max(y_list)
y_min = min(y_list)

z_max = max(z_list)
z_min = min(z_list)

for x, y, z in zip(x_list, y_list, z_list):
    x = (x - x_min) / (x_max - x_min)
    y = (y - y_min) / (y_max - y_min)
    z = (z - z_min) / (z_max - z_min)
    print(x * SCALE, y * SCALE, z * SCALE)
