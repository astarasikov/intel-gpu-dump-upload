#!/usr/bin/env python

import os
import sys
import re

def readLines(name):
    try:
        fd = os.open(name, os.O_RDONLY)
        stats = os.fstat(fd)
        data = os.read(fd, stats.st_size)
        os.close(fd)
        lines = data.split('\n')
        return lines
    except IOError, e:
        print 'Error: ', e
        return []

def parseIntelHeader():
    regnames = dict()
    lines = readLines('intel_reg.h')
    regex = re.compile('#define\s+([A-Z0-9_]+)\s+(0x[0-9a-fA-F]+)')
    for line in lines:
        match = regex.match(line)
        if match:
            name = match.group(1)
            sval = match.group(2)
            regnames[name] = sval
    return regnames

def parseRegList():
    regs = []
    lines = readLines('fixregs')
    regex = re.compile('\s+([A-Z0-9_]+):\s+(0x[0-9a-fA-F]+)(.+)')
    for line in lines:
        match = regex.match(line)
        if match:   
            name = match.group(1)
            sval = match.group(2)
            comment = match.group(3)
            regs.append((name, sval, comment))
    return regs

def genScript(header, list, outFile):
    regNames = parseIntelHeader()
    regList = parseRegList()
    out = [ '#!/bin/bash' ]

    for regTuple in regList:
        name, sval, comment = regTuple
        fmtStr = format('oops, register undefined %s' % name)
        if regNames.has_key(name):
            regAddr = regNames[name]
            fmtStr = format('intel_reg_write %s %s #%s' % (regAddr, sval, comment))
        out.append(fmtStr)
    
    outData = str.join('\n', out)

    try:
        fd = os.open(outFile, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        os.write(fd, outData)
        os.fchmod(fd, 755)
        os.fsync(fd)
        os.close(fd)
    except IOError, e:
        print 'Error: ', e

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: %s intel_reg.h reglist output.sh" % sys.argv[0]
    else:
        genScript(*sys.argv[1:])
