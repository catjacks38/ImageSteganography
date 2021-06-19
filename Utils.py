from sys import exit


def raiseErrorAndExit(error):
    print("Sheesh, seems like there was an error while running this program:\n")

    for _ in range(len(error) + 4):
        print("=", end="")

    print(f"\n| {error} |")

    for _ in range(len(error) + 4):
        print("=", end="")

    print("\n\nIf this doesn't help, then you might just need to play more.")

    exit(-1)
