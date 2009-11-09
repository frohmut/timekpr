""" Future timekpr application utility """

#!/usr/bin/python

from optparse import OptionParser

def arguments():
    usage = """ %prog [options] arg0 arg1"""
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename",
                      help="read data from FILENAME")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")

    # OPTIONS example: --something or -s for short
    # ARGUMENTS example: something

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")
    if options.verbose:
        print "reading %s... executing %s" % (options.filename, args[0])

if __name__ == "__main__":
    arguments()
