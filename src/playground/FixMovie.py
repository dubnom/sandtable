#!/usr/bin/python3

import os
import sys
import traceback

from optparse import OptionParser

from Sand import MOVIE_WIDTH, MOVIE_HEIGHT, MOVIE_OUTPUT_PATH, TMP_PATH
import MovieStatus

MOVIE_FORMAT = 'frame%04d.png'
MOVIE_SIZE = '%dx%d' % (MOVIE_WIDTH, MOVIE_HEIGHT)
MOVIE_BIT_RATE = 1800


class Movie:
    FPS = 5


movie = Movie()


def MakeMovie(script, previewMode, ms):
    ms.update(ms.ST_RUNNING, 'Processing "%s" %s' % (script, previewMode))

    #
    #   Assemble all of the images into a movie
    #
    if previewMode:
        outputFile = MOVIE_OUTPUT_PATH + script + '_preview.mp4'
    else:
        outputFile = MOVIE_OUTPUT_PATH + script + '.mp4'

    if previewMode:
        ms.update(ms.ST_RUNNING, 'Using ffmpeg to make the movie')
        os.system('ffmpeg -r %d -b %dk -i %s%s -y %s' % (movie.FPS, MOVIE_BIT_RATE, TMP_PATH, MOVIE_FORMAT, outputFile))
        ms.update(ms.ST_RUNNING, 'Cleaning up ".png" files')
        os.system('rm %s*.png' % (TMP_PATH))
    else:
        # Get the photos from the camera
        ms.update(ms.ST_RUNNING, 'Getting the photos from the camera')
        os.system('gphoto2 -P --filename=%s%%f.jpg' % (TMP_PATH))

        # Rename the photos from 'IMG_####.jpg' to 'frame####.jpg' and convert them to a smaller size
        ms.update(ms.ST_RUNNING, 'Converting the photos to smaller size and renumbering')
        fileNames = os.listdir(TMP_PATH)
        fileNames.sort()
        fileNumber = 0
        for fileName in fileNames:
            if fileName.endswith('.jpg'):
                os.system('convert -size %s %s%s %sframe%04d.jpg' % (MOVIE_SIZE, TMP_PATH, fileName, TMP_PATH, fileNumber))
                os.remove('%s%s' % (TMP_PATH, fileName))
                fileNumber += 1

        # Make the movie
        ms.update(ms.ST_RUNNING, 'Using ffmpeg to make the movie')
        os.system('ffmpeg -r %d -b %dk -i %sframe%%04d.jpg -y %s' % (movie.FPS, MOVIE_BIT_RATE, TMP_PATH, outputFile))
        ms.update(ms.ST_RUNNING, 'Cleaning up the ".jpg" files')
        while fileNumber > 0:
            fileNumber -= 1
            os.remove('%sframe%04d.jpg' % (TMP_PATH, fileNumber))

    return outputFile


def main():
    ms = MovieStatus.MovieStatus()
    try:
        ms.update(ms.ST_RUNNING, 'Starting Up')

        parser = OptionParser("usage: %prog [options]")
        parser.add_option("-p", "--sand",    dest="sand",    help="Draw in sand", default=False, action="store_true")

        (options, args) = parser.parse_args()

        if len(args) != 1:
            print('Expected script name as argument')
            raise ValueError("Script name wasn't passed as an argument")

        movieName = MakeMovie(args[0], not options.sand, ms)
        ms.update(ms.ST_DONE, 'Movie "%s" is finished' % movieName)

    except Exception:
        type, value, trace = sys.exc_info()
        ms.update(ms.ST_ERROR, 'Exited with\n' + ''.join(traceback.format_exception(type, value, trace)))


if __name__ == "__main__":
    main()
