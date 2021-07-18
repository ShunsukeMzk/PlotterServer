import time

with open("data/lorenzdata_short.rescale.csv") as f:
    for line in f:
        try:
            x, y, z = line.strip().split()
            x, y, z = map(float, (x, y, z))
        except Exception:
            pass
        else:
            print(flush=True)
            print(x, y, z, flush=True)
            print(y + 1, x, z, flush=True)
            time.sleep(0.1)

