
def gene():
    yield from range(10)
    yield from sorted(range(10), reverse=True)


for j in gene():
    print(j)
