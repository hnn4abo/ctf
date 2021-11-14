# Challenge, the easy version.

`What can I say, I just like squares.`

-----
nonsquarefreedom_easy.py
```
#!/usr/bin/env python3
#
# Polymero
#

# Imports
from Crypto.Util.number import getPrime
import os

# Local imports
with open('flag.txt','rb') as f:
    FLAG = f.read()
    f.close()

# Key gen
P = getPrime(512//8)
Q = getPrime(256)
R = getPrime(256)
N = P**8 * Q * R
E = 0x10001

def pad_easy(m):
    m <<= (512//8)
    m += (-(m % (P**2)) % P)
    return m

# Pad FLAG
M = pad_easy(int.from_bytes(FLAG,'big'))
print('M < N    :',M < N)
print('M < P**8 :',M < (P**8))
print('M < Q*R  :',M < (Q*R))

# Encrypt FLAG
C = pow(M,E,N)
print('\nn =',N)
print('e =',E)
print('c =',C)

# Hint
F = P**7 * (P-1) * (Q-1) * (R-1)
D = inverse(E,F)
print('\nD(C) =',pow(C,D,N))

#----------------------------------------------------
#                       Output
#----------------------------------------------------
# M < N    : True
# M < P**8 : True
# M < Q*R  : True
#
# n = 68410735253478047532669195609897926895002715632943461448660159313126496660033080937734557748701577020593482441014012783126085444004682764336220752851098517881202476417639649807333810261708210761333918442034275018088771547499619393557995773550772279857842207065696251926349053195423917250334982174308578108707
# e = 65537
# c = 4776006201999857533937746330553026200220638488579394063956998522022062232921285860886801454955588545654394710104334517021340109545003304904641820637316671869512340501549190724859489875329025743780939742424765825407663239591228764211985406490810832049380427145964590612241379808722737688823830921988891019862
#
# D(C) = 58324527381741086207181449678831242444903897671571344216578285287377618832939516678686212825798172668450906644065483369735063383237979049248667084304630968896854046853486000780081390375682767386163384705607552367796490630893227401487357088304270489873369870382871693215188248166759293149916320915248800905458
#
```

# Solution
This is RSA with the following important details:
- `N = P**8 * Q * R`
- `M` is divisible by P, thus **not** co-prime with `N`
- `E` and `D` are usual RSA parameters: `E = 65537` and `E*D ≡ 1 (mod φ(N))`
- `C = M**E (mod N)` is known
- `D(C) = (M**E)**D (mod N)` is known as well

The `pad_easy` takes the flag as input, adds `512//8` zero bits to the end, and then rounds up to the nearest integer divisible by P. If we can find `M`, we can easily find the flag by dropping the last `512//8` bits.

From Euler's theorem we know that if `x` is co-prime with `N`, then `(x**E)**D ≡ x (mod φ(N))`
In this challenge we know `(M**E)**D (mod N)`, but `M` is not co-prime with `N`, thus finding `M` is going to be a bit more complicated... But it's still possible!

Let's denote `M = P*X` and try to find `P` and `X`.

## Step 1. Find `P`.
Main idea: if we have two numbers divisible by `P` (or by `P**k` for some `k`), we can find GCD of the two numbers, and it would probably be `P` (or `P**k`).
One obvious number is `N`, it is divisible by `P**8`.
Another number is `M**E (mod N)` (which is known). `M**E` is divisible by `P**8` (because it is divisible by `P**65537`), `N` is divisible by `P**8` as well; thus `M**E (mod N)` must be divisible by `P**8` too.
So we find `GCD(N, C)`, and it is `P**8`.

## Step 2. Find `X`.
Here we will need the known `D(C)` value.
`D(C) ≡ (M**E)**D ≡ M**(E*D) ≡ (P*X)**(E*D) ≡ P**(E*D) * X**(E*D) (mod N)`
Let's get rid of `mod(N)` first:
`P**(E*D) * X**(E*D) = A*N + D(C)` for some `A`. It's time to replace `N` with `P**8 * Q * R`:
`P**(E*D) * X**(E*D) = A*P**8*Q*R + D(C)`. Divide both parts by `P**8`:
`P**(E*D-8) * X**(E*D) = A*Q*R + D(C)/P**8`
We are almost there. It's time to look at this formula modulo `Q*R`:
`P**(E*D-8) * X**(E*D) ≡ D(C)/P**8 (mod Q*R)`
If we could find `P**(E*D-8) (mod Q*R)`, we then can find `X**(E*D) (mod Q*R)` from the previous formula. And it's easy to show that `X = X**(E*D) (mod Q*R)`, thus we found `X`!
### Find `P**(E*D-8) (mod Q*R)`
It's simply `P**(-7) (mod Q*R)`. And here is why.
We know that `E*D ≡ 1 (mod φ(N))`, i.e. `E*D ≡ 1 (mod P**7*(P-1)*(Q-1)*(R-1))`. So for some `B`:
`E*D = B*P**7*(P-1)*(Q-1)*(R-1) + 1`
`E*D-8 = B*P**7*(P-1)*(Q-1)*(R-1) - 7`
`P**(E*D-8) = P**((Q-1)*(R-1)*...) * P**(-7)`
Euler's theorem tells us that `P**((Q-1)*(R-1)) ≡ 1 (mod Q*R)` (because `P` is co-prime with `Q*R`), and it means that `P**(E*D-8) ≡ P**(-7) (mod Q*R)`
### Proof `X ≡ X**(E*D) (mod Q*R)`
Well, it is Euler's theorem again. `X` now is co-prime with `Q*R` (well, most likely!), thus `X**(E*D) = X**(1 + (Q-1)*(R-1)*...) ≡ X (mod Q*R)`

So the formula for `X` is rather simple.
From `P**(E*D-8) * X**(E*D) ≡ D(C)/P**8 (mod Q*R)` and `P**(E*D-8) ≡ P**(-7) (mod Q*R)`, we see that `X**(E*D) ≡ D(C)/P**8 * P**7 (mod Q*R)`.
`X = D(C)/P**8 * P**7 (mod Q*R)`
`X = D(C)/P (mod Q*R)`
(Actually we only found `X (mod Q*R)` and there might be multiple solutions for `X`. We will pick `0 < X < Q*R` and will hope it is the right one.)

Let's write a script and see if it actually works.
```
from Crypto.Util.number import long_to_bytes

# copied from the 'MathyOracle' challenge
def GCD(N,k):
    while min(N,k)>0:
        if k>N: N,k = k,N
        N%=k
    return max(N,k)

N = 68410735253478047532669195609897926895002715632943461448660159313126496660033080937734557748701577020593482441014012783126085444004682764336220752851098517881202476417639649807333810261708210761333918442034275018088771547499619393557995773550772279857842207065696251926349053195423917250334982174308578108707
E = 65537
C = 4776006201999857533937746330553026200220638488579394063956998522022062232921285860886801454955588545654394710104334517021340109545003304904641820637316671869512340501549190724859489875329025743780939742424765825407663239591228764211985406490810832049380427145964590612241379808722737688823830921988891019862

# D(C)
DC = 58324527381741086207181449678831242444903897671571344216578285287377618832939516678686212825798172668450906644065483369735063383237979049248667084304630968896854046853486000780081390375682767386163384705607552367796490630893227401487357088304270489873369870382871693215188248166759293149916320915248800905458

P8 = GCD(N, C)
# Found from P8
P = 17649002407863577841
assert P8 == P**8
assert DC % (P**8) == 0

# Q*R
QR = N // P8
assert N == P**8 * QR

X = (DC // P) % QR
M = P * X
print (long_to_bytes(M>>(512//8)))
```

Output is `flag{y34_th1s_1s_n0t_h0w_mult1pr1m3_RS4_w0rks_buddy}`

# Challenge, the hard version.
The only difference in the hard version is the padding method (and, of course, the generated random primes `P`, `Q`, `R`;
```
def pad_hard(m):
    m <<= (512//2)
    m += int.from_bytes(os.urandom(256//8),'big')
    m += (-(m % (P**2)) % (P**2))
    m += (-(m % (P**3)) % (P**3))
    return m
```
The `pad_hard` takes the flag as input, adds `512//2` random bits to the end, and then rounds up to the nearest(?) integer divisible by `P**3`.
Can we apply the same method again? The method may not work because the different padding method might mess up with some assumptions that were valid in the easy version, but let's give it a try.
There are just a few differences from the easy version:
- `M = P**3 * X`
- `D(C) ≡ (M**E)**D ≡ M**(E*D) ≡ (P**3*X)**(E*D) ≡ P**(3*E*D) * X**(E*D) (mod N)`
- `P**(3*E*D-8) ≡ P**(3*(1+(Q-1)*(R-1)*...)-8) ≡ P**(-5) (mod Q*R)`
And the final formula for `X`:
`X = D(C)/P**3 (mod Q*R)`

Let's see if it works.

```
from Crypto.Util.number import long_to_bytes

# copied from the 'MathyOracle' challenge
def GCD(N,k):
    while min(N,k)>0:
        if k>N: N,k = k,N
        N%=k
    return max(N,k)

N = 51214772223826458947343903953001487476278631390021520449180482250318402223871910467589821176474724615270573620128351792442696435406924016685353662124634928276565604574767844305337546301974967758679072483930469188209450741154719808928273796360060047042981437882233649203901005093617276209822357002895662878141
E = 65537
C = 41328763458934302623886982279989290133391941143474825043156612786022747186181626092904440906629512249693098336428292454473471954816980834113337123971593864752166968333372184013915759408279871722264574280860701217968784830530130601590818131935509927605432477384634437968100579272192406391181345133757405127746

# D(C)
DC = 36121865463995782277296293158498110427613111962414238045946490101935688033022876541418793886469647898078579120189419552431787379541843120009675223060979171856818401470674058515557901674369835328155371791544935440499813846484080003978652786490718806523938327240659684439275298596339460595405316567186468069580

P8 = GCD(N, C)
# Found from P8
P = 16799713761391840501
assert P8 == P**8
assert DC % (P**8) == 0

# Q*R
QR = N // P8
assert N == P**8 * QR

X = (DC // P**3) % QR
M = P**3 * X
print (long_to_bytes(M>>(512//2)))
```

Output is `flag{1_th1nk_1_m1ght_b3_squ4r3_fr33_1nt0l3r4nt}`