import sys
import json

SIZE = 0.3

for i, line in enumerate(sys.stdin):
    try:
        if "," in line:
            x, y, z, *_ = line.strip().split(",")
        else:
            x, y, z, *_ = line.strip().split()
        
        dic = {
            "name": f"point-{i}",
            "type": "Object/sphere",
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

