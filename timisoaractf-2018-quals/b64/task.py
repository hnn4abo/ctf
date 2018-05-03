#!/usr/bin/python
import sys, random, base64, string
# original table
b64tab ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
z = list(b64tab)
# STRONG security no doubt!
random.shuffle(z)
b64new =  ''.join(z)
f = open(sys.argv[1], "r").read()
for idx, c in enumerate(f):
	assert (ord(c) >= 0x20 and ord(c) < 0x80) or (ord(c) == 0xa)
f = base64.b64encode(f)
f = f.translate(string.maketrans(b64tab, b64new))
open(sys.argv[1] + ".encrypted", "w").write(f + "\n")
