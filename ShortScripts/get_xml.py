#!/usr/bin/env python

import argparse
import uiautomator

def main(args):
     print(args['xml_file'])
     uiautomator.device.dump(args['xml_file'])

if __name__ == "__main__":
     # https://stackoverflow.com/questions/7427101/simple-argparse-example-wanted-1-argument-3-results
     parser = argparse.ArgumentParser()
     parser.add_argument('-x','--xml_file', help='XML File', required=True)

     args = vars(parser.parse_args())
     main(args)