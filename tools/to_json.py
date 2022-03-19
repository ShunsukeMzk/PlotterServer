import sys
import json

SIZE = 0.3

last_index = 0
for i, line in enumerate(sys.stdin):
    last_index = i
    try:
        if "," in line:
            x, y, z, *_ = line.strip().split(",")
        else:
            x, y, z, *_ = line.strip().split()
        
        dic = {
            "path": f"point/{i}",
            "type": "Object/Sphere",
            "position": {
                "x": float(x),
                "y": float(y),
                "z": float(z),
            },
            "scale": {
                "x": SIZE,
                "y": SIZE,
                "z": SIZE,
            },
            "color": {
                "r": float(x) / 10,
                "g": float(y) / 10,
                "b": float(z) / 10,
                "a": 1,
            }
        }
        print(json.dumps(dic))

    except Exception as e:
        print(line, e, file=sys.stderr)
        print(line)

for i in range(last_index + 1):
    if i == 0:
        continue

    dic = {
        "path": f"point/{i-1}_{i}",
        "type": "Object/Line",
    }
    print(json.dumps(dic))