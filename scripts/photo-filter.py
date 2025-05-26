#!/usr/bin/env python

# Scroll source folder and copy rated pictures to destination directory
# e.g. ./photo-filter.py -s /photosrc -d /photodest

import os
import sys
import optparse
import pyexiv2 as pe
import time
import stat
import shutil

class NoFile(Exception):

    def __init__(self, msg):
        self.msg = msg

def custom_listdir(path):
    """
    Returns the content of a directory by showing directories first
    and then files by ordering the names alphabetically
    """
    dirs = sorted([d for d in os.listdir(path) \
        if os.path.isdir(path + os.path.sep + d)])
    dirs.extend(sorted([f for f in os.listdir(path) \
        if os.path.isfile(path + os.path.sep + f)]))

    return dirs

def filterPhoto(srcfile, dstfile):
    # print "> Photo is: '%s / %s'" % (os.path.dirname(srcfile), os.path.basename(srcfile) )
    directorySrc = os.path.dirname(srcfile)
    directoryDst = os.path.dirname(dstfile)
    
    metadata = pe.ImageMetadata(srcfile)
    metadata.read()
    try:
      rating = metadata['Exif.Image.Rating']
      if rating and rating.value > 0:
        # print "> Photo is: '%s/%s' = %d" % (directorySrc, os.path.basename(srcfile), rating.value )
        print "> Photo is: '%s/%s' = %d" % (directoryDst, os.path.basename(dstfile), rating.value )
        if not os.path.exists(directoryDst):
          os.makedirs(directoryDst)
        shutil.copy(srcfile, directoryDst)
        
    except KeyError, err:
      # nothing
      pass

def iterateRecursively(srcfolder, dstfolder):
    try:
        #test whether the folder passed exists, and the path is good
        if not os.path.exists(srcfolder):
            raise NoFile("Folder '%s' does not exist" % srcfolder)
        if not os.path.isdir(srcfolder):
            raise NoFile("'%s' is not a folder" % srcfolder)
        print ">>> Folder: '%s'" % srcfolder

        listing = custom_listdir(srcfolder) # os.listdir(srcfolder)

        # process the files
        for infile in listing:
            if not os.path.isdir(os.path.join(srcfolder, infile)):

                froot, ext = os.path.splitext(infile) #get the extension
                if ext.lower() == '.jpg':
                    try:
                        filterPhoto(os.path.join(srcfolder, infile), os.path.join(dstfolder, infile))
                    except BaseException as error:
                        print('An exception occurred: {}'.format(error))
                else:
                    pass
		    # print '>  ', infile, ' <--- UNPROCESSED'

        # recurse the folders
        for infile in listing:
            if os.path.isdir(os.path.join(srcfolder, infile)):
                #iterateRecursively(os.path.join(srcfolder, infile), os.path.join(dstfolder, infile))
                iterateRecursively(os.path.join(srcfolder, infile), dstfolder)

    except NoFile, err:
        print err.msg


if __name__ == '__main__':
    parser=optparse.OptionParser()
    parser.add_option('-s', '--source', dest='source',
                type="string",
                default="/home/clement/Images/tmp",
                help="Directory used to iterate recursively the pictures.")
    parser.add_option('-d', '--destination', dest='destination',
                type="string",
                default="/home/clement/Images/tmp2",
                help="Directory used to copy the rated pictures only.")
    (options, args) = parser.parse_args()

    try:
        iterateRecursively(options.source, options.destination)
    except:
        exc_info = sys.exc_info()
        print "unhandled exception: %s %s %s" \
            % (exc_info[0], exc_info[1], exc_info[2])

