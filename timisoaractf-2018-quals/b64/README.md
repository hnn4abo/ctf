We're given a file with a long encrypted text and some python code:

```python
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
```

So, it's basically base64, only we don't know what bits are encoded by what characters. We also see that the original text contains characters in a specific range. Let's see what we can do...

We'll start by breaking the text into chunks of 4 encoded characters, each such chunk encodes 3 ascii characters in the original text.
```
   0     ........ ........ ........     ...     v8A+  
   3     ........ ........ ........     ...     6NYP  
   6     ........ ........ ........     ...     HdYQ  
...

2280     ........ ........ ........     ...     izO2  
2283     ........ ........ ........     ...     NFkT  
2286     ........ ........              ..      a7C=  
```

Above, each line contains the index in the plain text, three 8-bit groups corresponding to three plain-text characters (unknown so far), the ascii representation of those three plain-text characters (unknown), and the 4 corresponding encoding characters (from the given text.encypted file).

This is how this table will look in the end:
```
   0     01010011 01101111 01100011      Soc     v8A+  
   3     01101001 01100001 01101100      ial     6NYP  
   6     00100000 01100001 01101110       an     HdYQ  
...

2280     00110001 00111000 01011101      18]     izO2 
2283     01011011 00110001 00111001      [19     NFkT 
2286     01011101 00001010               ]\      a7C=  
```

Lets start filling those missing bits!!

Lets try to guess some of those bits and see what we get.

We know that in the original plain-text, all chars have 0 as their first bit, this should give us some information:
```
   0     0....... 0....... 0.......      ...     v8A+  
   3     0....... 0....... 0.......      ...     6NYP  
   6     0....... 0....... 0.......      ...     HdYQ  
   9     0....... 0....... 0.......      ...     oU59  
...
```

This will give us some info! From the first line we see that in the 6 bits 'v' encodes the first one is 0. Similarly, for '8' - the third bit is 0, and for 'A' - the fifth bit is zero.
Ok, that's something. We do that for all the chunkschars .

Let's take a look on those bitmaps:

```
'1' ->  ['?', '?', '?', '?', '0', '?']  
'0' ->  ['0', '?', '?', '?', '?', '?']  
'X' ->  ['0', '?', '?', '?', '0', '?']  
'Z' ->  ['?', '?', '?', '?', '?', '?']  
'a' ->  ['0', '?', '0', '?', '?', '?']  
...
```

Mostly still empty, but we have something.


What else do we have? Take a look on the last chunk:

```
2286     0.0.1.0. 0.0.....               ..      a7C=  
```

So, C's last two bits are 0:

```
'C' ->  ['?', '?', '?', '?', '0', '0']
```

Next, we count how many bitmaps have the first bit as 0: 20. How many have the third as 0? 22. What about the fifth bit? 31! Aha!
So at most one of the other symbols have 0 as their 5th bit. Let's set the fifth bit of the other symbols to 1 (we'll correct the one that's wrong later).

The picture clears up a bit:

```
'+' ->  ['?', '?', '0', '?', '1', '?']
'/' ->  ['?', '?', '0', '?', '1', '?']
'1' ->  ['?', '?', '?', '?', '0', '?']
'0' ->  ['0', '?', '?', '?', '1', '?']
...

   0     0...0... 0.1..... 0...0.1.      ...     v8A+  
   3     0...1.0. 0.1...0. 0.....0.      ...     6NYP  
   6     0...0... 0.1...0. 0.....1.      ...     HdYQ  
   9     0...0... 0.1..... 0...0.0.      ...     oU59  
  12     0...0... 0.1..... 0.....1.      ...     j8AQ  
...
```


Next... we spot this chunk:

```
1494     0.0.0... 0.1.0.0. 0.....0.      ...     78rO  
```

Hm... the first ascii looks suspecious, if the first three bits are 000, then ord < 0x20, but that's only possible if ord = 0xa = 0b00001010, but then the fifth bit doesn't match! So the first three bits are 010, that's another known bit '7':
```
'7' -> ['0', '1', '0', '?', '0', '?']
```

A few more similar chunks give us some more bits.


What else can we do? Let's take a look on some frequent chunks:
"HtgC" appears 11 times, "2dO9" appears 10. Hmm... what common 3 letters could they encode, how about "the"?

We try with "HtgC" but hit a dead end. What about "2dO9"?

```
 459     0...1... 0.1.0... 0.....0.      ...     4sXK  
 462     01110100 01101000 01100101      the     2dO9  
 465     0...0.00 01100... 0.....1.      ...     Hdgx  
...
 984     01110100 0110.... 0.....0.      t..     2dqK  
 987     01110100 01101000 01100101      the     2dO9  
 990     0...0.00 0110.... 0.100001      ...     HdTO  
...
1194     0...1... 0.1.0... 0.....0.      ...     4sXK  
1197     01110100 01101000 01100101      the     2dO9  
1200     0...0.00 0110.... 0.100001      ...     Hd1O  
```


Look at the characters right before and right after the "the", we'd expect those to be spaces (0x20 = 0b0010000), and sure enough it looks like they are!
Moreover, we can now update some bits accordingly:

```
'H' -> ['0', '0', '1', '0', '0', '0']
'K' -> ['1', '0', '0', '0', '0', '0']
...
```

Some letters start to appear in the text:

```
 228     01110100 0110.... 0.....0.      t..     2d1T  
 231     00100000 01100001 01..0.1.       a.     HdYs  
 234     01110100 01100101 0...0.1.      te.     2drW  
 237     00100000 01100001 0.100000       a.     HdkK  
 240     0...00.. 0.1..... 0.....0.      ...     jsAL  
 243     0...00.. 0.1.1000 01100101      ..e     j8O9  
 246     0...01.. 0.1..... 0.....0.      ...     oU5w  
 249     01110101 0.1..... 0.....0.      u..     2NDP  
```


We do some more guesswork. For example, this is a common pattern:

```
1290     00100000 01101001 01....1.       i.     Hd9Q  
1293     00100000 0.1.0... 0.....00       ..     HtgC  
...
1245     00100000 01101001 01....1.       i.     Hd9Q  
1248     00100000 0101.... 0.....1.       ..     HYDZ  
```

A common two letter word starting with i? "is" or "in", let's try each.
In some cases we only have one or two missing bits, we guess based on common sense.

More words emerge:
```

2160     0...1.01 0.1.0... 0.100000      ...     4aiK  
2163     0...00.. 0.1..... 0.101110      ...     j8AQ  
2166     01110100 01101001 01101110      tin     2d9Q  
2169     01110101 0.1.0... 0.....0.      u..     2NvP  
```

This looks like "continue" between two spaces.

```
1566     01110100 01101000 01..0.1.      th.     2dOF  
1569     0...1... 0.1..... 01000101      ..E     3e5Y  
```

A space before a Capital E? Probably!


```
1821     01010011 01101001 01101110      Sin     v89Q  
1824     01100011 01100101 00100000      ce      j8vK  
1827     01110100 01101000 01100001      tha     2dOO  
1830     01110100 0.1..... 01....0.      t..     2U5w  
```

A space after "that".

A few more of those, and we start getting more and more plain text:

```
  84     01100101 0010.... 0.100000      e..     ohwK  
  87     01100101 01110011 01....0.      es.     oauw  
  90     01100101 01100011 01....1.      ec.     oNux  
  93     01100001 0110.... 0.100000      a..     jN1P  
  96     0...1.01 00100000 01....0.      . .     Sh5G  
```

That looks like "especially"!

Eventually we see something that looks like real text:

```text
So.ia` and econom.c malaise had .een presen..i. .o.ia`ist .omania...r quite some
 time, espec.al`. .u.... the au..e..t. .ear. o. the ...... T.e auste..t..mea..re
..were .es.g.ed .. pa.t .. .eauses.u to repa. ...eign debts.X6] .hortl. a.ter a.
..tched pu.`i....eec. .. .eauses.u .. Buc.a.e.....omania.. .ap.ta` c.t.. t.a..wa
s .roa.cast to mil`ion. o. Roma..an..o. ..ate te`ev..io., ..nk-a.....`e mem.e.s 
o. t.e mil.tar. switched, alm..t una..mou.l.. ...m su.po.t... the d...ator to .a
ck... the pr..e..... .opulatio..[7] ..ot.. st..et vio`e..e a...murder in se..ral
 ..ma..a. cities over the cou.se o. r..ghl. a.week `e..the .omanian st..ngma. to
 .lee t.e .ap.ta` c.t..o. .. De.em.er with .i..wi.e, Deput. Prime ....ster .`e.a
 .eauses.u. Evading .aptu.e .. ha...l..depa.ti.g v.a .el.copter e....tivel. po.
```


Now we can google it, and find the original: https://en.wikipedia.org/wiki/Romanian_Revolution.
Complete the bitmaps and we can get the complete plaintext, and here's the flag:

```
... Ceausescus along with its communist past, and the tumultuous departure from it.[9][10] timctf{c6167039f2c2029e9e2c79d163c6af99} The National Salvation Front quickly took power after Ceausescu was toppled, promising free and fair elections
```

The flag: timctf{c6167039f2c2029e9e2c79d163c6af99}


If you want to check yourself, here's the complete mapping to standard base64:

```python

from base64 import b64decode

m = {'0': 'O', '2': 'd', '4': 'b', '6': 'a', '8': '2', 'D': 'J', 'F': 'z', 'H': 'I', 'L': '0', 'N': 'W', 'P': 's', 'R': 'n', 'T': '5', 'X': 'c', 'Z': 'v', 'd': 'G', 'f': '4', 'h': 'S', 'j': 'Y', 'l': '3', 'n': 't', 'r': 'V', 't': 'H', 'v': 'U', 'x': 'p', 'z': 'T', '+': 'j', '/': 'D', '1': 'x', '3': 'L', '5': 'B', '7': 'Q', '9': 'l', '=': '=', 'A': '9', 'C': 'o', 'G': 'k', 'I': '1', 'K': 'g', 'M': 'A', 'O': 'h', 'Q': 'u', 'S': 'e', 'U': 'C', 'W': 'y', 'Y': 'F', 'a': 'X', 'e': 'i', 'g': 'R', 'i': 'M', 'k': 'E', 'o': 'Z', 'q': '8', 's': 'm', 'u': 'N', 'w': 'w', 'y': 'K'}

b64decode(''.join([m[c] for c in open("text.encrypted").read().strip()]))

```




