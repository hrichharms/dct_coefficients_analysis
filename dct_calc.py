from os.path import isdir
from os import mkdir
from sys import argv
from cv2 import VideoCapture, dct
from json import dump


VIDEO_FORMATS = "mov", "mp4", "avi", "mkv"
TEMP_DIR = "temp"


# python3 dct_calc.py <input filename> <output_filename> <mode> *<args>


if __name__ == "__main__":

    # ensure that temporary directory exists
    if not isdir(TEMP_DIR): mkdir(TEMP_DIR)    
