#!/usr/bin/env python

import sys
import re

fileName = "output.txt"
outFile = "broken_links.html"
whitelistFile = "link-whitelist.txt"

if len(sys.argv) < 2:
    print ("Enter a file name to parse")
    sys.exit()

outputPath = sys.argv[1]
fileNamePath = outputPath + "/" + fileName
outFilePath = outputPath + "/" +  outFile

with open (whitelistFile) as w:
	whLines = w.readlines()

whitelist = []
for line in whLines:
	link = line.rstrip()
	whitelist.append(link)

with open (fileNamePath) as f:
    lines = f.readlines()

numBrokenLinks = 0
numWhiteListMatches = 0
newLines = ["<!DOCTYPE html><html><head><style>body {font-family: sans-serif;}</style></head><body>"]
whiteListLines = []

for line in lines:
    if "[broken]" in line:
        strings = line.split(" ")
        link = strings[2][:-1]
        link = link.strip()
        if link in whitelist:
            whiteListLines.append("<b>" + strings[0] + "</b>\n<blockquote><a href=\"" + link + "\">[whitelist] " + link + "</a></blockquote>\n")
            numWhiteListMatches += 1
        else:
            newLines.append("<b>" + strings[0] + "</b>\n<blockquote><a href=\"" + link + "\">[broken] " + link + "</a></blockquote>\n")
            numBrokenLinks += 1

newLines.insert(0,"<h1>" + str(numBrokenLinks + numWhiteListMatches) + " broken links found in Sphinx link check</h1>\n")
newLines.insert(1,"<h2>" + str(numBrokenLinks) + " unmatched broken links</h2>\n")
newLines.append("<h2>" + str(numWhiteListMatches) + " links matched whitelist</h2>\n")
for line in whiteListLines:
	newLines.append(line)
newLines.append("</body></html>")

with open (outFilePath, "w") as outF:
    for line in newLines:
        outF.write(line)

print("See ./" + outFilePath + " for a detailed breakdown of broken links.")

if numBrokenLinks != 0:
	sys.exit(-1) 
