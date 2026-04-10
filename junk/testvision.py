
from agentforge.tools.ImageToTxt import imagetotxt


def lookatimage(path):
    text = imagetotxt(path)
    print(text)


if __name__ == '__main__':
    imagepath = 'img.png'
    lookatimage(imagepath)