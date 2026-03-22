def rms(data):
    return (sum(x**2 for x in data) / len(data)) ** 0.5
