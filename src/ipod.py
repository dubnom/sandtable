#!/usr/bin/python

import os

def main():
    MOVIE_OUTPUT_PATH = 'video/'
    fileNames = os.listdir( MOVIE_OUTPUT_PATH )
    fileNames.sort()
    for fileName in fileNames:
        if fileName.endswith( '.mp4' ):
            print('Converting "%s" to ipod format' % fileName)
            os.system( 'ffmpeg -i %s%s -f mp4 -vcodec mpeg4 -b 700k -r 5 -s 320x214 -padtop 12 -padbottom 14 -ab 128kb -acodec mp3 -ar 48000 -y %s%s_ipod.mp4' % (MOVIE_OUTPUT_PATH, fileName, MOVIE_OUTPUT_PATH, fileName[:-4]))

#ffmpeg -i "/home/fxfitz/multimedia/videos/psych/Psych.S01E15.DSR.XviD-ORENJi.avi" -f mp4 -vcodec mpeg4 -b 700k -aspect 4:3 -r 23.98 -s 320x240 -acodec aac -ar 48000 -comment "Encoded by Vive" "/home/fxfitz/test.mp4"
main()
