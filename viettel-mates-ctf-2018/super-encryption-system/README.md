# Challenge

```
We have just developed a new encryption system. We believe that it is unbreakable, or not?

Source: https://drive.google.com/file/d/14uHUlGy-WwiYh9F2YbSMCe2aBiDeZ26Q/view?usp=sharing

nc <IP-ADDRESS> <PORT>
```

-----
crypto2.py
```python
from hashlib import sha256
flag = '' # HIDDEN FLAG
g = int(flag[:len(flag)/2].encode('hex'),16)
h = int(flag[len(flag)/2:].encode('hex'),16)
n = 0 # THE MODULUS YOU DONT HAVE TO WORRY ABOUT

def calculate(i):
	p = h ^ i
	r = pow(g, p, n)
	s = hex(r).replace('0x','').replace('L','')
	return s
	
def main():
	while True:
		inp = raw_input("Show me your input: ")
		try:
			inp = int(inp)
		except:
			print 'Wrong input'
			break
		print 'Here you are:', calculate(inp)

if __name__ == '__main__':
	main()
```

# Solution
## Step 1: find `n`
The comment says that `n` is "the modulus you don't have to worry about", but for some reason I didn't buy it, and I started looking at how we can find the value of `n`.

If we find a few numbers divisible by `n`, the chances are their GCD would be equal to `n`. How can we generate a number that is divisible by `n`? Let's assume for a minute that the last two bits of `h` are both zeros. Let's look at three numbers:
```python
v0 = calculate(0)
v1 = calculate(1)
v2 = calculate(2)
```

```python
v0 = pow(g,h) % n
v1 = pow(g,h^1) % n
v2 = pow(g,h^2) % n
```

The last two bits of `h` are zeros so we know that `h^1 == h+1` and `h^2 == h+2`.
```python
v0 = pow(g,h) % n
v1 = pow(g,h+1) % n = pow(g,h)*g % n
v2 = pow(g,h+2) % n = pow(g,h)*g*g % n
```
```python
v1 = (v0*g) % n
v2 = (v0*g*g) % n
```

What if we calculate `(v0*v2 - v1*v1) % n`?
`(v0*v2 - v1*v1) % n = (v0*v0*g*g - v0*g*v0*g) % n = 0`. Bingo! We got a number that is divisible by `n`.

Well... we would get a number divisible by `n` if the last two bits of `h` were zeros. But are we going to be that lucky?

Let's see what we will get if the last two bits of `h` are not zeros. Let's denote an inverse element to `g` modulo `n` as `g_`, i.e. `(g*g_)%n == 1`

| Last two bits of h        | v0            | v1    | v2  |
| ------------------------: | -------------:| -----:| ---:|
| ...01 | v0 | v0 * g_ | v0 * g * g |
| ...10 | v0 | v0 * g | v0 * g_ * g_ |
| ...11 | v0 | v0 * g_ | v0 * g_ * g_ |

If the last two bits of `h` are `11`, `(v0*v2 - v1*v1) % n == 0` still holds.
If the last two bits of `h` are `01` or `10`, we can look at the value of `(v1*v1*v2 - v0*v0*v0) % n`. It's zero!
So we know that either `v0*v2-v1*v1` or `v1*v1*v2-v0*v0*v0` would be divisible by `n`.

Now we can do the same for the following numbers:
```python
v0 = pow(g,h^4) % n
v1 = pow(g,h^4^1) % n
v2 = pow(g,h^4^2) % n
```
The same logic applies for these three numbers so either `v0*v2-v1*v1` or `v1*v1*v2-v0*v0*v0` is divisible by `n`.

Well, for any `X` we can calculate the following numbers:
```python
v0 = pow(g,h^X) % n
v1 = pow(g,h^X^1) % n
v2 = pow(g,h^X^2) % n
```
and then we will know that either `v0*v2-v1*v1` or `v1*v1*v2-v0*v0*v0` is divisible by `n`.

Trying a few different `X`, we soon can find the value of `n`.
`n = 7337488745629403488410174275830423641502142554560856136484326749638755396267050319392266204256751706077766067020335998122952792559058552724477442839630133`

## Step 2: find `g`
Let's look at two values:
```python
v0 = calculate(0)
v1 = calculate(1)
```
If the last bit of `h` is `0`, then `v1 = g * v0` modulo `n`
If the last bit of `h` is `1`, then `v0 = g * v1` modulo `n`
We already know `v0`, `v1`, and `n`, so we can find two possible values of `g` from the above equations. Plus we know that `g` was generated from the flag: `g = int(flag[:len(flag)/2].encode('hex'),16)`

We can find `g = 44996602808662107716423321330522259877001509858135500250548563577`
And the first half of the flag is `matesctf{Y0u_c4n't_f1nd_4ny`

## Step 3: find `h`
We will find `h` bit by bit.
Let's find the last bit.
```
v0 = calculate(0)
v1 = calculate(1)
```
```
v0 = pow(g,h) % n
v1 = pow(g,h^1) % n
```
If the last bit of `h` is `0`, then `h^1 == h+1` and `v1 = v0 * g % n`
If the last bit of `h` is `1`, then `h^1 == h-1` and `v0 = v1 * g % n`
We know all four values `v0`, `v1`, `g`, and `n`, so we can simply find the last bit of `h` by checking both equations and selecting the correct one.

The same logic can be applied to find `i`-th bit of `h`.
```
v0 = calculate(0)
v1 = calculate(1<<i)
```
```
v0 = pow(g,h) % n
v1 = pow(g,h^(1<<i)) % n
```
If the `i`-th bit of `h` is `0`, then `h^(1<<i) == h+(1<<i)` and `v1 = v0 * pow(g,1<<i) % n`
If the `i`-th bit of `h` is `1`, then `h^(1<<i) == h-(1<<i)` and `v0 = v1 * pow(g,1<<i) % n`
Again, we can check both equations and pick the correct one.

`h = 0b01011111011000110110100000110100011011000110110000110100011011100100011100110011010111110110010100110100011100110011000101100101011100100101111101110100011010000011010001101110010111110111010001101000001100010111001101111101`

The second half of the flag is `_ch4ll4nG3_e4s1er_th4n_th1s}`
