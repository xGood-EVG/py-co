from calendar import month
import sys

if __name__ == '__main__':
    year, mon = int(sys.argv[1]), int(sys.argv[2])
    data = month(year, mon).splitlines()
    print(f".. table:: {data[0].lstrip()}\n")
    data = "\n".join([data[0], "=" * len(data[1]), data[1], "=" * len(data[1]), *data[2:], "=" * len(data[1])]).splitlines()
    for ind in range(len(data[1])):
        if data[2][ind] == " ":
            data[1] = data[1][:ind] + ' ' + data[1][ind+1:]
            data[3] = data[3][:ind] + ' ' + data[3][ind+1:]
            data[-1] = data[-1][:ind] + ' ' + data[-1][ind+1:]
    print("\n".join(data[1:]))
