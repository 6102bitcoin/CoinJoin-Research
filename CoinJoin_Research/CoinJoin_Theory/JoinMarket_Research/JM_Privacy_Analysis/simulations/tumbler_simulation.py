from itertools import combinations, chain, product
from hashlib import sha256
from binascii import hexlify
import random
import copy
fnt = 190000

def nfc(closure):
    '''unique names for closures
    for easier reading
    '''
    return 'C'+ hexlify(sha256(''.join(str(closure))).digest())[:3].upper()

class simTx(object):
    def __init__(self, ins, cjouts, chouts):
        self.ins = [item for sublist in ins for item in sublist]
        self.cjouts = cjouts
        self.chouts = chouts
        self.outs = self.cjouts + self.chouts
        self.validate()
        self.linkages = []
        self.sudoku()
    
    def validate(self):
        total_in = sum([_[1] for _ in self.ins])
        total_out = sum([_[1] for _ in self.outs])
        if total_out > total_in:
            self.printout()
            raise Exception("invalid transaction.")
        x = [_[1] for _ in self.cjouts]
        if not x.count(x[0])==len(x):
            raise Exception("not all coinjoin outputs equal sized.")
    
    def printout(self):
        print "SIMULATED TRANSACTION: "
        total_in = sum([_[1] for _ in self.ins])
        total_out = sum([_[1] for _ in self.outs])        
        print 'got totalin: '+str(total_in)
        print 'got totalout: '+str(total_out)
        print 'with these inputs: '
        print self.ins
        print 'and these cjouts: '
        print self.cjouts
        print 'and these chouts: '
        print self.chouts        
        print 'got these linkages'
        for l in self.linkages:
            print 'change out: '+str(l[0])+' is linked to input: '+str(l[1])

    def sudoku(self):
        '''Creates a set of deduced linkages between
        inputs and change outputs for the given transaction. Based on the 
        tolerance parameter fnt (in satoshis) deduces the linkages with a simple
        'coinjoin sudoku' approach.
        Each element in the generated list `iss`(which is of size 2^len(self.ins))
        has format (sum, (index, index, ..)) which is variable length, and the
        indices are the index into self.ins.
        The equation to find a linkage is:
        change output - coinjoin output ~= sum(subset of inputs)
        '''
        x = [_[1] for _ in self.ins]
        if len(self.ins) > 20:
            #combinatorial blowup; give up
            raise Exception("panic: too many combinations to sudoku")
        
        #"input indices list"
        iil = range(len(self.ins))
        
        #list of all possible combinations of indices
        input_combos = list(
            chain.from_iterable(combinations(iil,r) for r in range(len(iil)+1)))
        
        #for each element of input_combos, calculate the total input amount
        #from summing each input at that index and create a tuple as described.
        iss = []
        for ic in input_combos:
            amt = sum([self.ins[_][1] for _ in ic])
            iss.append((amt, ic))

        for cho in self.chouts:
            if cho==(0,0):
                print 'calculate input combo for zero change;'
                #raw_input()
                for isum in iss:
                    if abs(self.cjouts[0][1] -isum[0])< fnt:
                        for j in range(len(isum[1])-1): #won't happen if only 1 
                            #link each input to each other, let closure algo
                            #collapse them later
                            self.linkages.append((self.ins[isum[1][j]],
                                                  self.ins[isum[1][j+1]]))
                continue
            none_found = True
            for isum in iss:
                if abs(self.cjouts[0][1] + cho[1] - isum[0]) < fnt:
                    #all entries in isum[1] are linked to this change output
                    for j in isum[1]:
                        self.linkages.append((cho, self.ins[j]))
                        none_found = False
            if none_found:
                print 'no linkage found for this change: '+str(cho)
                raw_input()

def find_closures(linkages):
    '''Generates a set of lists of
    utxo type objects (here just (id, amt)), which are
    connected via the given linkages.
    The linkages are of the form (utxo1,utxo2).
    '''
    new_closures = []
    closures = [[_[0],_[1]] for _ in  linkages]
    for c in closures:
        updates = []
        for i,c2 in enumerate(new_closures):
            if not set(c2).isdisjoint(set(c)):
                updates.append((i, list(set(c2).union(set(c)))))
        if len(updates)==0:
            new_closures.append(c)
        else:
            new_closures = [i for j,i in enumerate(
                new_closures) if j not in [_[0] for _ in updates]]
            new_closures.append(list(set.union(*[set(_[1]) for _ in updates])))
        
    return new_closures

def utxo(amt=-1, mult = 1, txid = None, tindex = -1):
    amt = int(1000000000*random.random()) if amt==-1 else amt
    amt = mult * amt
    if amt==0:
        return (0,0)
    if not txid:
        txid = hexlify(sha256(str(amt)).digest())[:6]
    if tindex==-1:
        tindex = int(20*random.random())
    txidn = txid + ':'+str(tindex)
    return (txidn, amt)

def create_tx(wallet_ins, cjamt, txfee, cjfee, payer):
    '''wallet_ins is of form [(utxo1, utxo2,..),(utxo1, utxo2,..)..]
    n = len(wallet_ins)
    create n out utxos of amt cjamt
    for each wallet in, create a chout of correct size:
    for non-payer index, chout = sum(ins)- cjout + cfee/(n-1)
    for payer index, chout = sum(ins) - cjout - cjfee - txfee
    return simTx object
    '''
    n = len(wallet_ins)
    cjouts = []
    chouts = []
    txid = hexlify(sha256(str(cjamt)).digest())[:6]
    for i in range(n):
        cjouts.append(utxo(amt=cjamt, txid=txid, tindex=i))
        if i != payer:
            chout_amt = sum([_[1] for _ in wallet_ins[i]]) - cjamt + cjfee/(n-1)
        else:
            chout_amt = sum([_[1] for _ in wallet_ins[i]]) - cjamt - cjfee - txfee
        chouts.append(utxo(amt=chout_amt, txid=txid, tindex=i+n))
    return simTx(wallet_ins, cjouts, chouts)

if __name__ == '__main__':
    #create a set of wallets W_ij
    #with j running 0 to n_mixdepths-1
    #in each mixdepth create utxos 0..n_utxos-1
    #then follow tumbler algo for W_0:
    #means, starting from W_00, do ntx txs
    #with the third a sweep to W_01, then repeat
    #up to W_0_n-mixdepths-1
    cjfee = 150000
    txfee = 30000
    num_wallets = 10
    n_mixdepths = 5
    nc = 2 # no of counterparties, so 3 total
    ntx = 3 #no of transactions per mixdepth, including final sweep
    n_utxos = 4
    nutx = 2 #no of utxos to use in each tx (static for now)
    wallets = []
    #defines wallets initial state
    for w in range(num_wallets):
        wallets.append([])
        for m in range(n_mixdepths):
            wallets[w].append([])
            #to make 'not enough liquidity found' errors rare, give more coins
            #to ygens (wallets 1,2,3,4)
            mult = 1 if w==0 else 6
            for u in range(n_utxos):
                wallets[w][m].append(utxo(mult=mult)) #default random txids
                
    #keep a copy (effectively to store both spent and unspent txos)
    original_wallets = copy.deepcopy(wallets)
    txs = []
    for i in range(n_mixdepths):
        for j in range(ntx):
            wallet_ins = []
            #j=2 is last, is sweep
            if j==2:
                wallet_ins.append(wallets[0][i])
            else:
                wallet_ins.append(wallets[0][i][:nutx])
            total_amt = sum([_[1] for _ in wallet_ins[0]])
            if j != 2:
                total_amt = int( 0.8 * total_amt)
            #delete consumed utxos for non-sweep so not reused
            wallets[0][i] = wallets[0][i][nutx:]
            #pick random counterparty wallets
            counterparty_indices = range(1,num_wallets)
            random.shuffle(counterparty_indices)
            for c in counterparty_indices:
                #need to choose utxos such that the amount is big enough
                #do a crude version of select()
                #1. try to find one utxo > total, if so use that.
                #2. if not, take the largest, try to find one more > new total.
                #etc down the list, fail if not enough.
                utxos_to_be_used = []
                used_amt = 0
                tempwallet = copy.deepcopy(wallets[c][i])
                enough = False
                for q in range(len(tempwallet)):
                    #1. sort the available utxos by size.
                    tempwallet = sorted(tempwallet, key=lambda x: x[1],
                                        reverse=True)
                    utxos_to_be_used.append(tempwallet[0])
                    used_amt += tempwallet[0][1]
                    del tempwallet[0]
                    if used_amt > total_amt:
                        enough = True
                        break
                if not utxos_to_be_used or not enough:
                    print "Counterparty didn't have enough coins"
                    continue
                #check for matching amounts; if so, deanonym won't work
                if not set([_[1] for _ in utxos_to_be_used]).isdisjoint(
                    set([_[1] for _ in wallet_ins[0]])):
                    print 'wasnt disjoint, not adding these utxos:'
                    print utxos_to_be_used
                    continue
                else:
                    wallet_ins.append(utxos_to_be_used)
                    wallets[c][i] = tempwallet #they've been used so update
                if len(wallet_ins)==nc+1:
                    break
                
            print 'about to create a transaction, from mixdepth: '+str(i)
            print 'wallet ins is: '
            print wallet_ins
            newtx = create_tx(wallet_ins,total_amt-txfee-cjfee,txfee,cjfee,0)
            #add newly created outputs to relevant wallets
            #new outputs are in the same order as inputs, not shuffled; this is
            #a trick, don't let it mislead you!
            if i ==4:
                final_output = newtx.cjouts[0]
            else:
                original_wallets[0][i+1].append(newtx.cjouts[0])
                wallets[0][i+1].append(newtx.cjouts[0])
            if j != 2:
                original_wallets[0][i].append(newtx.chouts[0])
                wallets[0][i].append(newtx.chouts[0])
            
            for k in range(nc):
                #modulo for wraparound.
                original_wallets[counterparty_indices[k]][(
                    i+1)%n_mixdepths].append(newtx.cjouts[k+1])
                original_wallets[counterparty_indices[k]][i].append(
                    newtx.chouts[k+1])
                wallets[counterparty_indices[k]][(
                    i+1)%n_mixdepths].append(newtx.cjouts[k+1])
                wallets[counterparty_indices[k]][i].append(newtx.chouts[k+1])                
            txs.append(newtx)
            print 'did : '+str(len(txs)-1)+" transactions."
    
    all_linkages = []
    for tx in txs:
        all_linkages.extend(tx.linkages)
        
    closures = find_closures(all_linkages)
    print "Got these mixdepth closures: "
    print closures
    
    #see if the tumbler wallet's mixdepths correspond to closures, as we 
    #expect
    closed =[False]*n_mixdepths
    for i in range(num_wallets):
        for j in range(n_mixdepths):
            print '*'*20
            print 'wallet '+str(i)+ ' mixdepth: '+str(j)
            print 'has these utxos: '+str(original_wallets[i][j])
            ident = False
            for c in closures:
                if set(original_wallets[i][j])==set(c):
                    print '~'*20
                    print 'FULL MIXDEPTH CLOSURE'
                    print '~'*20
                    ident=True
                    if i==0:
                        closed[j]=True
                elif set(original_wallets[i][j]).issuperset(set(c)):
                    print 'identified that this closure belongs: '+str(c)
                    ident = True
            if not ident:
                print 'failed to link this mixdepth to any closure'
    if not all(closed):
        print 'failed to completely identify the mixdepth closures ' + \
              'for the tumbler, quitting.'
        exit(0)
    else:
        print 'success: identified the closures for all the tumbler mixdepths.'
        for i,t in enumerate(txs):
            print 'generated tx, number '+str(i)+': '
            t.printout()
    
    #from here we treat wallets[0] as the set of all correctly identified
    #closures, each of which contains the full set of utxos for that mixdepth.
    #Next we want to see if there are closure-closure mappings in transactions
    #which are unique. This allows to create linkages between closures, which is 
    #effectively a complete trace of the tumbler except for its final output.
    if len(list(set(map(tuple,closures)))) != len(closures):
        raise Exception('has repeats')
    else:
        print 'closures has: '+str(len(closures))+' unique items'
        
    for t in txs:
        #create a list of closures for ins, cjouts and chouts
        t.closures = [list() for _ in range(3)]
        for i,a in enumerate([t.ins, t.cjouts, t.chouts]):
            for c in closures:
                if not set(a).isdisjoint(set(c)):
                    if c not in t.closures[i]:
                        t.closures[i].append(c)
    
    #what we expect is that 1 closure will appear in the 
    #coinjoin outs and the inputs across each set of 3 transactions.
    success_closures = []
    for i in range(4): #not including final mixdepth
        #oversimplification: in reality, would have to deduce sweeps by
        #looking at number of chouts, here we just
        #cheat a little by knowing how many txs occur at each mixdepth.
        in_cj_mappings = []
        for j in range(3):
            t = txs[i*3+j]
            names1 = [nfc(x) for x in t.closures[0]]
            names2 = [nfc(x) for x in t.closures[1]]
            in_cj_mappings.append([item for item in product(names1, names2)])
            #(Sanity check: the closures for the change outputs should match
            #those for the inputs) (but not for sweep)
            if j != 2 and set(map(tuple,t.closures[0])) != set(
                map(tuple, t.closures[2])):
                raise Exception("some kind of failure")

        #success means all 3 have *exactly* one closure mapping in common
        print '*'*20
        print 'FOR MIXDEPTH '+str(i)
        for icjmi in range(3):
            print '*'*20
            print 'INCJMAPPINGS '+str(icjmi)+':'
            print in_cj_mappings[icjmi]
        success = list(set(in_cj_mappings[0]).intersection(
            set(in_cj_mappings[1])).intersection(set(in_cj_mappings[2])))
        
        if len(success) != 1:
            print "Closure mapping failed:"
            print success
            exit(0)
        else:
            print 'Closure mapping success:'
            print success
            success_closures.append(success) #a pair of closures, from 'product'
        
    #if all went well, we have a set of 5 closure maps like (C1, C2), (C2, C3)..
    for i in range(1,len(success_closures)):
        if success_closures[i-1][0][1] != success_closures[i][0][0]:
            print 'the closures dont chain'
            exit(0)
    print 'after the first 4 mixdepth steps, we have this chain: '
    print success_closures
    
    #for the final step, the analyst would have to find 3 (or similar)
    #transactions spending from the last of the above closures, with
    #the final one being a sweep. Assuming this is easily done, we can 
    #identify the coinjoin outputs for the final transaction.
    for i in range(3):
        t = txs[12+i]
        if not success_closures[-1][0][1] in [nfc(x) for x in t.closures[0]]:
            raise Exception("failed to chain closures to the last mixdepth")
        
    #all good; one of the final cjouts is definitely the spend
    print 'the real final output was: '+str(final_output)
    print 'we deduced it must be one of:'
    print txs[-1].cjouts
        
