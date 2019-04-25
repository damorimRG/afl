from os import listdir

def main():
    outdirname="output/libjpeg-turbo/"
    for filename in listdir(outdirname):
        print(filename)


if __name__ == '__main__':
    main()
