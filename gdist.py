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
import json

help_message = '''
gdist.py [ -h ] [ -v ] [ -i indir ] [ -o outdir ] [ -f file ] [ -r reference ]

-h (--help) This help message
-v Verbose mode
-i (--indir) Assign the input directory (default ./)
-o (--outdir) Assign the output directory (optional)
-f (--file) Assign the output file for mapping JSON (default ./gdist.json)
-r (--reference) Assign the reference mapping JSON for incremental update. Only files with digests different from the reference JSON are copied.
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	##############################################
	# check args and initialize options
	##############################################
	verbose = False
	outdir = ""
	indir = "./"
	outfile = "./gdist.json"
	reffile = ""
	
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hi:o:f:r:v", ["help", "outdir=", "indir=", "file=", "reference="])
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
			if option in ("-r", "--reference"):
				reffile = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use -h (--help)"
		return 2
	
	if not os.path.isdir(indir):
		print >> sys.stderr, "Input directory " + indir + " doesn't exist"
		return 2
	
	# check output directory not a subdirectory of input directory (to avoid dead loop)
	if outdir:
		absInDir = os.path.abspath(indir)
		absOutDir = os.path.abspath(outdir)
		if (absOutDir[:len(absInDir)] == absInDir):
			print >> sys.stderr, "Input directory must not contain output directory (to avoid dead loop)"
			return 2
		
	##############################################
	# Read the reference JSON
	##############################################
	refMap = {}
	if os.path.isfile(reffile):
		with open(reffile, "r") as f:
			try:
				refMap = json.load(f)
			except ValueError, err:
				print >> sys.stderr, "Fail reading reference JSON file " + reffile + ": " + str(err)
				return 2
	
	##############################################
	# Read the input directory and to get a file list
	##############################################
	if verbose:
		print "Reading directory " + os.path.abspath(indir)
	
	topdown = False
	count = 0
	resultJSON = "{"
	for root, dirs, files in os.walk(indir, topdown):
		if verbose:
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
			
			# Check whether this file is already in reference JSON
			if (refMap):
				if (refMap[srcRelPath] == tgtFile):
					if verbose:
						print("    " + tgtFile + " is in reference JSON")
					continue
					
			# Ready to copy
			if verbose:
				print("    " + srcRelPath + " >>>> " + tgtFile)
			
			count += 1
			
			# Copy when outdir is not empty
			if outdir:
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
			
			# Append to the output JSON
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

	report = ""
	if outdir:
		report += "Succeeded copying " + str(count) + " files from " + indir + " to " + outdir
	else:
		report += "Succeeded reading " + str(count) + " files in " + indir
	if reffile:
		report += " based on referecing JSON " + reffile
	report += ", generating JSON output at " + outfile
	print(report)

if __name__ == "__main__":
	sys.exit(main())
