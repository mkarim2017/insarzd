#!/usr/bin/env python3

#Cunren Liang, JPL/Caltech


import os
import sys
import glob
import argparse
import traceback


def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='delete file')
    parser.add_argument('-f', dest='f', type=str, required=True,
            help = 'file to be deleted', nargs='*')

    if len(sys.argv) <= 1:
        print('')
        parser.print_help()
        sys.exit(1)
    else:
        return parser.parse_args()


if __name__ == '__main__':

    try:
        print("delete file")
        inps = cmdLineParse()
        print(inps)
        print(inps.f) 
        #files = sorted(glob.glob(inps.f)) 
        files=sorted(inps.f)
        print(files)
        print(len(files))

        if len(files) == 0:
            print('no file is to be deleted regarding to: {}'.format(inps.f))
        else:
            for file in files:
                os.remove(file)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(str(e))
        traceback.print_exc() 


