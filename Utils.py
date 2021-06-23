from sys import exit

LSBEncode = 1

start = 38
end = 1

def raiseErrorAndExit(error):
    print("Sheesh, seems like there was an error while running this program:\n")

    for _ in range(len(error) + 4):
        print("=", end="")

    print(f"\n| {error} |")

    for _ in range(len(error) + 4):
        print("=", end="")

    print("\n\nIf this doesn't help, then you might just need to play more.")

    exit(-1)


def genHeaderData(method, option, fileExtension):
    global start
    global end

    header = [start, method, option]

    for char in fileExtension:
        header.append(ord(char))

    header.append(end)

    return header


def getHeaderData(data):
    global start
    global end

    fileExtension = ""

    if data[0] != start:
        return -1

    for byte in data[3:]:
        if byte == end:
            break

        fileExtension += chr(byte)

    return data[1], data[2], fileExtension
