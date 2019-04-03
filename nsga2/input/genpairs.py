from random import random

def main(num):
    for x in range(num):
        for y in range(num):
            if (x >= y): continue
            else:
                print("{}-{}: {}".format(x, y, round(random(),2)))


if __name__ == "__main__":
    # execute only if run as a script
    main(10)
