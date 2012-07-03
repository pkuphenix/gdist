#!/usr/bin/env python
# encoding: utf-8
"""
gdist.py

Created by Li Qian on 2012-07-02.
"""

import sys
import os
import getopt
import hashlib
import shutil

help_message = '''
The help message goes here.
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	##############################################
	# check args and initialize options
	##############################################
	verbose = False
	outdir = "./gdist"
	indir = "./"
	outfile = "./gdist.json"
	
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hi:o:f:v", ["help", "outdir=", "indir=", "file="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--outdir"):
				outdir = value
			if option in ("-i", "--indir"):
				indir = value
			if option in ("-f", "--file"):
				outfile = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2
		
	##############################################
	# Read the input directory and to get a file list
	##############################################
	if not verbose:
		print "Reading directory " + os.path.abspath(indir)
	
	topdown = False
	resultJSON = "{"
	for root, dirs, files in os.walk(indir, topdown):
		if not verbose:
			print "Entering directory " + os.path.join(root)
			
		for name in files:
			# ignore hidden files
			if name[0] == '.':
				continue
			# Analyze file path and name
			if indir[-1] == os.sep:
				omitLen = len(indir)
			else:
				omitLen = len(indir) + 1
			
			srcFullPath = os.path.join(root, name)
			srcRelPath = srcFullPath[omitLen:]
			srcFile = os.path.split(srcFullPath)[1]
			[srcFileMain, srcFileExt] = os.path.splitext(srcFile)
			
			# Compute the md5 digest
			m = hashlib.md5()
			m.update(srcRelPath)
			with open(srcFullPath, "rb") as f:
				bytes = f.read(1024)
				while bytes:
					m.update(bytes)
					bytes = f.read(1024)
			srcDigest = m.hexdigest()
			
			tgtFile = srcFileMain[:32] + "." + srcDigest + srcFileExt[:32]
			if not verbose:
				print("    " + srcRelPath + " >>>> " + tgtFile)
			
			if not os.path.isdir(outdir):
				try:
					os.makedirs(outdir)
				except os.error:
					print "Fail to create target directory: " + outdir
					return 2
					
			# Copy the file to target directory
			try:
				shutil.copy(srcFullPath, os.path.join(outdir, tgtFile))
			except (IOError, os.error), why:
				print "Fail to copy file: " + os.path.join(outdir, tgtFile) + " " + str(why)
				return 2
			
			resultJSON += '\"' + srcRelPath + '\":\"' + tgtFile + '\",'

	##############################################
	# Write the result JSON to output file
	##############################################
	if len(resultJSON) > 1:
		resultJSON = resultJSON[:-1] + '}'
	else:
		resultJSON += "}"
	
	with open(outfile, "w") as f:
		f.write(resultJSON)

if __name__ == "__main__":
	sys.exit(main())
