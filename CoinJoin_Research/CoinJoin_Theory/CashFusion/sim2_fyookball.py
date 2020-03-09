# Source: https://gist.github.com/fyookball/0b79a56b484063ac25d1ccaf22894dbb

from scipy.special import comb, factorial
import numpy as np
from itertools import combinations

Nplayers = 3  # don't change this.
Ninputsperplayer = 6   # don't go above 6 because it will take FOREVER to enumerate
typicalamount = 100   # relative to the 'resolution' of 1, how big are typical input amounts?


playerinputs = np.random.exponential(typicalamount, size=(Nplayers, Ninputsperplayer)).astype(int)
playerinputs = np.sort(playerinputs, axis=1)

playersums = np.sum(playerinputs, axis=1)
print(playerinputs)
print("player sums:", playersums)


# What does the final transaction look like:
inputs = np.sort(playerinputs.flatten())
outputs = np.sort(np.sum(playerinputs, axis=1))

print("Transaction inputs: ", inputs)
print("Transaction outputs:", outputs)


candidates = []
def add_candidate(sub, subsub):
    fulllist = list(inputs)
    sub = list(sub)
    subsub = list(subsub)
    for x in sub:
        fulllist.remove(x)
    for x in subsub:
        sub.remove(x)
    c = np.array([fulllist,sub, subsub])
    candidates.append(c)

# Now try to decompose from inputs & outputs
amtotal = np.sum(outputs)
sumhist = np.zeros((amtotal,amtotal))
for sub in combinations(inputs, len(inputs) - Ninputsperplayer):
    subamount = np.sum(sub)
    for subsub in combinations(sub, len(sub) - Ninputsperplayer):
        subsubamount = np.sum(subsub)
        sum0 = amtotal-subamount
        sum1 =  subamount-subsubamount
        # sum2 = subsubamount
        if sum0 == playersums[0] and sum1 == playersums[1]:
            add_candidate(sub,subsub)
        sumhist[sum1, sum0] += 1

print(sumhist[playersums[0], playersums[1]], "ways exist at actual configuration")

print("list of all candidate decompositions with sum %s"%(playersums))
for c in candidates:
    match = np.all(c == playerinputs)
    print(c, "<--- Correct!" if match else "")
