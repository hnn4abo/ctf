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