# Analysis of tumbler privacy.

## Executive summary.

This document addresses the extent to which blockchain analysis can enable the linkage of addresses in a run of Joinmarket's script `tumbler.py` as of version 0.1.0. The first two sections on [wallet structure](#joinmarket-wallet-structure) and [transaction types](#joinmarket-transaction-types) introduce the basic structure of joinmarket in terms of wallets and transactions, and can be skipped by those who know how Joinmarket works.
The third [section](#tumbler-algorithm) describes in outline the default algorithm followed by the `tumbler.py` script.

The fourth [section](#threat-model) briefly outlines the threat model under discussion, for context.
 
The next two sections give an outline of a method that **might** practically identify the linkages between the addresses used by the user/runner of the tumbler script, under certain common scenarios. The word 'might' here is an acknowledgement of the uncertainty arising from the fact that the method described is a feasible, but not a certain, way of isolating the set of transactions which corresponded to a single tumbler run. There may be several factors affecting the likelihood of success, including the density of concurrent *other* joinmarket transactions going on by the same participants over the same time period. The final [section](#ameliorations), and the [conclusion](#conclusions), list a number of different improvements that will either partly or greatly ameliorate the weakness that is outlined.

In simple terms, the core functionality of a coinjoin transaction - extending the possible set of owners of specific utxos - remains in place. But this analysis illustrates that the privacy gains of doing a sequence of Joinmarket-style coinjoins do not necessarily compound, either multiplicatively or at all (put differently: in the most negative scenario, a sequence of 15 joinmarket transactions might offer no more privacy than a single transaction). Additional measures must be taken which may involve (a) user choosing or not choosing certain tumbler options, (b) changing the Joinmarket codebase or (c) changing the usage pattern. Most likely all of (a), (b) and (c) should be under consideration.

The analysis here applies to varying extents to the other joinmarket scripts (`yield-generator.py` and `sendpayment.py`, especially the former), but this is not fully addressed by this document.

## Joinmarket wallet structure

Joinmarket wallets are of the BIP32 Hierarchical Deterministic wallet form, starting from the root m/0. The branches are defined by m/0/mixdepth/[external/internal]. The value of mixdepth runs from 0..M-1, where M is the number of mixdepths chosen by the user; by default 5. The value of [external/internal] is 0 for external, 1 for internal. Thus a default wallet will contain 10 separate branches.

Typical output from script `wallet-tool.py` running against a testnet wallet seed:

    mixing depth 0 m/0/0/
     external addresses m/0/0/0/
      m/0/0/0/016 muijch3wHvCXm9pHJQiyQFWDZSngPUdLrB  new 0.00000000 btc 
      m/0/0/0/017 n35T2GFV2CQXuN2eZJWBG7GTkhJZs4swJD  new 0.00000000 btc 
      m/0/0/0/018 mgwSKYK1zssnJi5T9UaR1gxdzPmU6zobvk  new 0.00000000 btc 
      m/0/0/0/019 mmXouP3x92h5yvBLMn6So4BvTRShN318Za  new 0.00000000 btc 
      m/0/0/0/020 mhKpprCpmfnsS2AwBDjiRoArNjSRMKCXHL  new 0.00000000 btc 
      m/0/0/0/021 n1h6MYPJLsoJ1dz2HNGxM7L5ct4A84RvQW  new 0.00000000 btc 
     internal addresses m/0/0/1/
      m/0/0/1/048 mrytep7Ne1t2Epzrn1zWPrBAfaDWCtekqx used 4.87792833 btc 
    for mixdepth=0 balance=4.87792833btc
    mixing depth 1 m/0/1/
     external addresses m/0/1/0/
      m/0/1/0/045 mrjkGaHdvFqZiTXRWcvAqSTmLaxKRfDWB9 used 9.27910795 btc 
      m/0/1/0/046 mmMs5iHLZKaLHLG3zysHwEdBNVHGyCLXgf  new 0.00000000 btc 
      m/0/1/0/047 mfkPoc34Z2k15jhcwPc8ifywykXvkovv9z  new 0.00000000 btc 
      m/0/1/0/048 mn5AuW8due3KtTGXvi68xQQUyNkg8jo5uQ  new 0.00000000 btc 
      m/0/1/0/049 n4Wg3ajPgLvEpumK2sHZXiggUw3kX6XCSh  new 0.00000000 btc 
      m/0/1/0/050 mfnxp5n4nMa9fZogNBo5gTSA7HBRLYmCW2  new 0.00000000 btc 
      m/0/1/0/051 msRJ7MpC9gKjqi7GjJ8WrHqAnPwDT8Nxsc  new 0.00000000 btc 
     internal addresses m/0/1/1/
      m/0/1/1/043 mtBYHv4vmxKfqQT2Cr2vrA578EmUzcwwKA used 1.76456658 btc 
      m/0/1/1/044 mp9yvRWwu5Lcs5EAnvGSKMKWith2qv1Rxt used 4.58622784 btc 
    for mixdepth=1 balance=15.62990237btc
    mixing depth 2 m/0/2/
     external addresses m/0/2/0/
      m/0/2/0/042 muaApeqh9L4aQvR6Fn52oDiqz8jKKu9Rfz  new 0.00000000 btc 
      m/0/2/0/043 mqdZS695VHeNpk83YtBmutGFNcJsPC39wW  new 0.00000000 btc 
      m/0/2/0/044 mq32QZX7DszZCYzKP6TvZRom1xFMoUWkbS  new 0.00000000 btc 
      m/0/2/0/045 mterWqVTyj2oKHPr1raaY6iwqQTKbwM5ro  new 0.00000000 btc 
      m/0/2/0/046 mzaotzzCHvoZxs2RjYXWN2Yh9kB6F5gU8j  new 0.00000000 btc 
      m/0/2/0/047 mvJMCGoG5ZUARtAr5x2KD1ebNLuL618zXU  new 0.00000000 btc 
     internal addresses m/0/2/1/
    for mixdepth=2 balance=0.00000000btc
    mixing depth 3 m/0/3/
     external addresses m/0/3/0/
      m/0/3/0/002 mwjZyUbh78UndNtqsKathxpjE4EsYrhLzm used 3.00000000 btc 
      m/0/3/0/004 msMoHnZRKfNRPQqg2MUk1rXrqwM6VeLL8C used 0.30000000 btc 
      m/0/3/0/006 mhBHRaFwMTPPWLdukqgJaSMmmCeQ8ef6QV used 9.26824652 btc 
      m/0/3/0/007 mrdv38dX1eQsZjAof442G9Lj66bM5yUnjA used 4.58134572 btc 
      m/0/3/0/008 moWA3FEYkNbEJkHdnQbQYkrVztTviMaHwe used 5.39567085 btc 
      m/0/3/0/009 mgoTGzD46mWoMiH97QHh9TxuJp4NmVobNp used 3.00000000 btc 
      m/0/3/0/010 mjddF8HmBaenGBspTMzhF3qikbbLB4xGZN  new 0.00000000 btc 
      m/0/3/0/011 mnEvKc2JLj8s1GLfvtvqVt5pWTu5jCdtEk  new 0.00000000 btc 
      m/0/3/0/012 n1FwKgDEjzRj2YsZNoG5MWVnuq72wA8Mgr  new 0.00000000 btc 
      m/0/3/0/013 mq4vn4KX9SRrvhiRkg9KrYADhKNPAp2wyN  new 0.00000000 btc 
      m/0/3/0/014 n3nG4334F19THUACgEEveRX8JcE5awY1qz  new 0.00000000 btc 
      m/0/3/0/015 mz5yHHbud68b8CLeNk2MsnyFgSJ9rPGk7v  new 0.00000000 btc 
     internal addresses m/0/3/1/
      m/0/3/1/000 mfbeMyajM4wYRmpWVrYnd3rBqvtBniw8gj used 0.25672994 btc 
      m/0/3/1/001 mzkFk3C9J6D9KE9cV4kuSctUKZXkr1gaio used 0.51499000 btc 
      m/0/3/1/002 n3SCTwDs4wcn7yGhFq8HJwxQ9PzBXvTJdV used 0.04199000 btc 
      m/0/3/1/006 mow4CyHNssjo2CNHdg3DdbXWYNPfY8HEPe used 0.36073270 btc 
    for mixdepth=3 balance=26.71970573btc
    mixing depth 4 m/0/4/
     external addresses m/0/4/0/
      m/0/4/0/011 mzMWwUSvj4n3wgtSMLXt17hQTi2zinzYWZ used 2.00000000 btc 
      m/0/4/0/012 mrgNjQWjrBDB821o1Q3qG6EmKJmEqgjtqY  new 0.00000000 btc 
      m/0/4/0/013 msjynFwGoGePoheVABAEgjxjw8FNuPgtPC  new 0.00000000 btc 
      m/0/4/0/014 moJpd6ZvgAm1ZENmAuoPKnqAUntoSixao9  new 0.00000000 btc 
      m/0/4/0/015 muajyWxmjuHQDm3MpSr7Y3RLAWDqch1yix  new 0.00000000 btc 
      m/0/4/0/016 n2tPijSN4nBFGAKbXpp6H7hfznhsYWwR88  new 0.00000000 btc 
      m/0/4/0/017 mnkrhe7fMYy4yjPM54gEurgxWpDXJ3axtn  new 0.00000000 btc 
     internal addresses m/0/4/1/
    for mixdepth=4 balance=2.00000000btc
    total balance = 49.22753643btc

### Use of external and internal branches.

Payments into the wallet should be made into new addresses on the `external` branch for any mixdepth. For the above wallet, `muaApeqh9L4aQvR6Fn52oDiqz8jKKu9Rfz` (from mixdepth 2) or `mrgNjQWjrBDB821o1Q3qG6EmKJmEqgjtqY` (from mixdepth 4) would be suitable candidates. The index of the address on the branch is shown as the final 3 digit integer in the identifier. As usual with deterministic wallets, a configurable gap-limit variable is used to determine how far forwards to search after unused/new addresses are located.

In a joinmarket transaction (see the next section for details), outputs go to: (1) coinjoin outputs -> external addresses in the next mixdepth (where 'next' means (mixdepth+1 % M)), (2) change outputs -> internal addresses in the same mixdepth.

The logic is fairly straightforward: the coinjoin outputs of a transaction must not be reused with any of the inputs to that same transaction, or any other output that can be connected with them, as this would allow fairly trivial linkage. By moving coinjoin outputs to an entirely separate branch, isolation is enforced.

Coinjoin outputs may also represent external payments to entities outside the joinmarket wallet. The following very simple diagram gives a starting point for building up a mental model of what's going on.

![alt text](/images/source_sink.png)

The notation in the diagram is explained in the next section.

## Joinmarket transaction types

We can define 4 distinct joinmarket transaction types. We use the notation "JMTx" for all of these, and separate short hand versions for each one.

1. SourceJMTx
 This is usually an ordinary bitcoin transaction paying into an unused address on an external branch for any one of the mixdepths of the wallet. As such it has no special joinmarket structure; it will usually have a change output, which will go back to the wallet funding this one. It *could*, however, be a payment from another joinmarket wallet, although most users will not be using more than one joinmarket wallet. This doesn't affect the analysis, in any case.

2. (Canonical) CJMTx
 The most fundamental type of joinmarket transaction involves neither a 'source' nor a 'sink', but only spends from this joinmarket wallet to itself, in conjunction with joining counterparties. The coinjoin output goes to a new address on the external branch of the *next* mixdepth, as was described in the previous section.

 ![alt text](/images/CJMTx.png)

 **NOTE**: the above diagram ignores transaction fees and coinjoin fees for simplicity, which slightly change the size of the change outputs; this obviously cannot be ignored in real analysis.

3. SpendJMTx
 This is a 'sink' transaction. This, generated either by `sendpayment.py` or `tumbler.py` scripts usually, will be the same as the CJMTx above, except with the difference that the coinjoin output for the initiator (taker) goes to an external address, e.g. a payment or a transfer to an external wallet.

4. SweepJMTx
 This can be either a 'sink' or not, depending on the destination of the coinjoin output. A sweep is characterised by 2 things: (a) the initiator will not create a change output, and (b) the initiator will consume **all** of the utxos in the given mixdepth (both internal and external branches) as inputs, leaving no coins left in that mixdepth.

 ![alt text](/images/SweepJMTx.png)

### Identifying joinmarket transaction types

See [here](https://github.com/adlai/cjhunt) for an example of trying to identify Joinmarket transactions on the blockchain, by @adlai. All joinmarket transactions, except, usually, SourceJMTx, will have these properties:

* N equal sized outputs where N >=3 
* At least N inputs
* Either N or N-1 additional outputs of size different from the N equal outputs.

Note that it *is* possible to create JMTxs with N=2, but this is not recommended (as it gives the taker zero privacy against the maker), and few if any have been observed in practice.

Thus, the presence of N-1 non-equal outputs, instead of N, is nearly certainly an indication that the transaction is of type SweepJMTx (assuming it is indeed a JMTx at all), with the taker not using a change output, whereas for SpendJMTx and CJMTx, the number of change outputs will be N.

The cjhunt tool mentioned above uses a heuristic based on these concepts; it will naturally flag a number of false positives that happen to fit this pattern; however, this algorithm will most likely capture all joinmarket transactions seen on the blockchain, also.

## Tumbler algorithm

By default, the tumbler will follow these steps:

* User provides 1 or more addresses (the default is 3, although they can be added during the tumbler run) for payment along with several other configuration variables. See [here](https://github.com/JoinMarket-Org/joinmarket/blob/master/tumbler.py#L259-L299).
* Starting from one mixdepth (by default 0), follow these steps for each mixdepth:
 * Run several CJMTx of varying amounts with some makers.
 * Run a final SweepJMTx spending all remaining utxos to the next mixdepth, or to a chosen external address if more than one external address is specified.
* The final transaction sweep from the final mixdepth spends out to the (last) external address provided at the start, so is a SweepJMTx with a spend as described earlier.

The remainder of this document analyses focuses on the simplest case, where only 1 external address is specified, and it should be borne in mind that this is the 'weakest' case for privacy; however a lot of the conclusions drawn still apply in the case of multiple external addresses.

## Threat model

The adversary is considered to be a 'blockchain analyst': an actor with access to the Bitcoin blockchain, at some point in the future, thus seeing all the JMTxs in the tumbler run, as well as all other JMTxs during the same period of course. We assume that they are somewhat computationally bounded, but the degree to which this is true is not particularly relevant, since the computational resources needed to conduct [JMSudoku](#jmsudoku-coinjoin-sudoku-for-jmtxs) and [closure analysis](#joinmarket-wallet-closures) are small in the current design.

The threat is that the blockchain analyst is able to, with reasonably high probability, infer the output address or addresses from the input address(es) (i.e. the SourceJMTx(s)) for the tumbler run.

There are **at least** three attack vectors that the blockchain analyst can employ:

1. Timing correlation
2. Amount correlation
3. Wallet closure correlation

Two points of note: 'wallet closure' is a term explained below [here](#joinmarket-wallet-closures). Also, other metadata analysis may well be possible, the most obvious being network-level correlation (e.g. IP addresses) and transaction fee correlation. These will not be discussed, and there may be others.

Timing analysis correlation will provide strong evidence in the case where the volume of JMTxs is small; in the simplest case, we might assume that only one taker is operating at one time (i.e. there is one tumbler run and no other coinjoins). While this makes analysis much easier, it will not be assumed to be true in the remaining sections - it is not clear that large volume of JMTxs will prevent the kind of analysis described below, although it may make it harder.

Amount correlation is also important, and is not discussed in detail. Note from the previous section, that the breaking up of JMTxs into several CJMTxs followed by a sweep also breaks up the amounts in the mixdepths, which greatly obfuscates amounts. None of the method in the following sections depends on successful amount correlation.

## JMSudoku: Coinjoin Sudoku for JMTxs

A reminder that all (except source) JMTxs have this structure:

ins: 

x<sub>1</sub>,x<sub>2</sub>,..x<sub>n</sub> 

outs:

 coinjoin outs: 

 y<sub>1</sub>, .. y<sub>m</sub> 

 change outs: 

 z<sub>1</sub>, .. z<sub>k</sub>

where k ∈ {m,m-1} with very high probability.

The coinjoin outputs y obey: 

y<sub>i</sub> = y<sub>j</sub>=y ∀ i,j ∈ {1..m}

z<sub>i</sub> = subsetsum(x) - y + Δ

'subsetsum' means a sum of one particular subset of the vector x. Δ can be either positive or negative; for a taker, it will be negative, and the sum of transaction fee contribution and coinjoin fees to the makers. For the makers it will be positive, and will be the coinjoinfee contribution minus the transaction fee contribution.

Here is an example of applying the subsetsum in practice:

Consider a simulated set of input utxos:

[(49091, 130748995), (87060, 291461442), (87842, 288897067), (99229, 641357205), (39965, 803128130), (27195, 84442088)]

where the first entry in each pair is a random identifier (takes the role, in this simulation, of the txid) and the second is a bitcoin amount in satoshis. We can use a fairly elementary algorithm to calculate the sums of the amounts in all possible subsets of these inputs; the list has 2<sup>6</sup>-1, or 63 entries, ignoring the initial null set:

[(0, ()), (130748995, (0,)), (291461442, (1,)), (288897067, (2,)), (641357205, (3,)), (803128130, (4,)), (84442088, (5,)), (422210437, (0, 1)), (419646062, (0, 2)), (772106200, (0, 3)), (933877125, (0, 4)), (215191083, (0, 5)), (580358509, (1, 2)), (932818647, (1, 3)), (1094589572, (1, 4)), (375903530, (1, 5)), (930254272, (2, 3)), (1092025197, (2, 4)), (373339155, (2, 5)), (1444485335, (3, 4)), (725799293, (3, 5)), (887570218, (4, 5)), (711107504, (0, 1, 2)), (1063567642, (0, 1, 3)), (1225338567, (0, 1, 4)), (506652525, (0, 1, 5)), (1061003267, (0, 2, 3)), (1222774192, (0, 2, 4)), (504088150, (0, 2, 5)), (1575234330, (0, 3, 4)), (856548288, (0, 3, 5)), (1018319213, (0, 4, 5)), (1221715714, (1, 2, 3)), (1383486639, (1, 2, 4)), (664800597, (1, 2, 5)), (1735946777, (1, 3, 4)), (1017260735, (1, 3, 5)), (1179031660, (1, 4, 5)), (1733382402, (2, 3, 4)), (1014696360, (2, 3, 5)), (1176467285, (2, 4, 5)), (1528927423, (3, 4, 5)), (1352464709, (0, 1, 2, 3)), (1514235634, (0, 1, 2, 4)), (795549592, (0, 1, 2, 5)), (1866695772, (0, 1, 3, 4)), (1148009730, (0, 1, 3, 5)), (1309780655, (0, 1, 4, 5)), (1864131397, (0, 2, 3, 4)), (1145445355, (0, 2, 3, 5)), (1307216280, (0, 2, 4, 5)), (1659676418, (0, 3, 4, 5)), (2024843844, (1, 2, 3, 4)), (1306157802, (1, 2, 3, 5)), (1467928727, (1, 2, 4, 5)), (1820388865, (1, 3, 4, 5)), (1817824490, (2, 3, 4, 5)), (2155592839, (0, 1, 2, 3, 4)), (1436906797, (0, 1, 2, 3, 5)), (1598677722, (0, 1, 2, 4, 5)), (1951137860, (0, 1, 3, 4, 5)), (1948573485, (0, 2, 3, 4, 5)), (2109285932, (1, 2, 3, 4, 5)), (2240034927, (0, 1, 2, 3, 4, 5))]

It is impossible of course, within one JMTx, to identify which subset of x corresponds to which element of y, but 'coinjoin sudoku', a term coined by researcher K. Atlas [here](http://www.coinjoinsudoku.com/advisory/) in connection with the blockchain.info SharedCoin coinjoin implementation, allows us to associate each z<sub>i</sub> with some subsetsum(x) with high probability, as long as a few reasonable assumptions hold:

* The bitcoin amounts of the utxos is large compared with the size of Δ
* The differences in the bitcoin amounts for each pair (z<sub>i</sub>, z<sub>j</sub>) where i and j correspond to different owners, is >> Δ.
* The number of inputs is not unfeasibly large (the number of input subset sums, which is the power set of the inputs, is 2<sup>n</sup>-1)
* None of the pairs (x<sub>i</sub>,x<sub>j</sub>) ∀ i,j ∈ {1..n} are equal
* None of the pairs (z<sub>i</sub>,z<sub>j</sub>) ∀ i,j ∈ {1..k} are equal

Note that it is still possible for the algorithm to fail to identify a particular subset of x even if these assumptions hold, although rarely (where different combinations of inputs happen, by accident, to add up to the same total, within a small tolerance). 

The algorithm for such 'sudoku' is nothing more complicated than enumerating all subset sums of the elements of the vector x, and comparing them with the change outputs.

Pseudocode:

    for each i in 0..k: (i.e. loop over change outputs)
        for each subset of x:
            calculate |(sum_amounts(subset(x)) - z_i -y| = α
            if α < tolerance:
                 store a link from each element of subset to z_i
        check: not more than one subset generated a match; if so, fail.

This is the basic design of what we will call **JMSudoku**, although some tweaks may be needed for more robustness. 

The value of the tolerance parameter should be slightly larger than the typical total fee paid by the taker (since the magnitude of the Δ for the makers is guaranteed to be smaller), and can of course be adjusted for best results.

## Joinmarket wallet closures

The above process, when applied to a default tumbler process, consisting of several joinmarket transactions by one taker entity with multiple maker entities in a sequence, will result in a large set of linkages between change outputs and inputs over the whole transaction set.

We borrow the concept of 'wallet closure' from [here](https://github.com/sharkcrayon/bitcoin-closure), and modify it. The concept there was a natural extension of "Heuristic 1" described in Meiklejohn et al. [here](https://cseweb.ucsd.edu/~smeiklejohn/files/imc13.pdf), which itself was based on the erroneous statement in the original Bitcoin [whitepaper](https://bitcoin.org/bitcoin.pdf) that "..multi-input transactions ... necessarily reveal that their inputs were owned by the same owner" (the statement that is contradicted by the fact that Coinjoin is possible). To be fair, this paper clearly identifies the limitation of the heuristic, but in our context, the limitation is not merely theoretical but becomes central - in Coinjoin we cannot assume that all inputs are linked into one entity, but rather assume the opposite. 

However, in Joinmarket as described in the first sections of this document, we *can* define a wallet closure (more accurately, a *mixdepth* closure) as:

    A *closure* is: the union of all non-disjoint sets of utxos which are linked via JMSudoku in some set of JMTxs.

For every transaction in which JMsudoku is successful, a closure containing the inputs and the corresponding change output is created, for each participant (so N closures for a JMTx with N equal sized outputs). These closures can grow (by application of the above definition) if more transactions are done using the same wallet mixdepth (remembering that each JMTx generates a new change output in the same mixdepth). Note the final qualification - JMSudoku will *not*, in itself, generate closures spanning more than one mixdepth, since the only connection between mixdepths occurs in the coinjoin outputs, while JMSudoku does not (and cannot) deduce anything about the ownership of those utxos. It *would* be possible to add *all* the coinjoin outputs into the closure calculation, but this would result in "closures" which spanned different JM wallets from different participants, which is not what the analyst is trying to achieve.

Note that when a sweep is performed in that mixdepth, using up all its remaining utxos, that closure will be *completed*; there will never be more additions to it. We call this a **complete mixdepth closure** or **CMC**. It contains one or more external txos that were sent to the mixdepth to fund it, and all txos that were generated by it to spend those outputs, until a sweep transaction occurs.

Note also that, since coins can always be added to the external branch of the wallet in future, a single mixdepth may, over time, generate more than one CMC.

Since the tumbler sequence design is based on multiple CJMTxs followed by a single SweepJMTx for each mixdepth in the wallet, each included mixdepth will generate one CMC during the tumbler run.

Finally, note the important feature of sweeps mentioned above: since they don't have a change output for one party, this, in the current design, and with minor exceptions, unambiguously flags them as being of the sweep type (see the earlier section on Joinmarket transaction identification). For the purposes of this analysis, we assume that this is true.

## Mapping closure graphs in transactions

Closure analysis of a tumbler run will, assuming success in JMSudoku at every step, generate:
* 1 CMC per mixdepth for the taker (the runner of tumbler)
* A random number of other closures for other counterparties (makers)
These other closures, for the makers, may become CMCs later if those parties run sweep transactions for those mixdepths. 

Given this scenario, it will usually be possible to identify which coinjoin output is that owned by the tumbler runner for each of the successive transactions in the tumble. The analyst is presented with something like this:

![alt text](/images/Closures.png)

These three transactions, the last of which is a sweep, for some mixdepth, say m, all have utxos which are members of CMC C1 present in their inputs, and all have a utxo which is a member of C3 as one of their coinjoin outputs (note that this evidence would come from the future transactions which use the members of C3 as inputs).

Notice also that, while C4 is part of the coinjoin output set for TX0, it is not part of the coinjoin output set for TX1 or TX2; that's why we don't deduce that C1 and C4 are linked. If it was, then we would not know whether C1 paid to C3 or C4; a closure mapping could not be deduced (or, more pessimistically, the analyst would work with 2 possibilities and go from there).

So, this data will be sufficient evidence to isolate C3 as the mixdepth m+1 for wallet w, which has C1 as mixdepth m, with high probability, i.e. those two CMCs have the same owner.

The same logic can be applied up the chain of mixdepths. For the simplest kind of tumbler run, with one external payout, it merely remains to identify which of the final coinjoin outputs is the external spend, and which are payouts to the makers. Depending on the details, this will usually be fairly easy, since the makers in the majority of cases will consume these utxos in joinmarket style transactions, whereas the external payout will not.

See [simulation code](/simulations/tumbler_simulation.py). The simulation is a overly simplified case (fixed numbers of transactions per mixdepth, fixed fees for example), but simply running it will output an example of tracing all the way from the first transaction to the last (it generates random transaction data for each run, and will *usually*, but not always be successful). Note the artificiality - in this code, the full set of 15 transactions for one tumbler run are used, so in that sense the question is begged; we already know that this is a tumbler run - but the method of closure mapping is shown.

It is important to understand this issue in a broader context. The following subsection addresses this.

### Feasibility of isolating tumbler transactions.

As mentioned in the [introductory section](#executive-summary), it isn't obvious that the set of transactions constituting a particular tumbler run can be isolated from the general set of joinmarket transactions found on the blockchain. In times of low volume, such that only a tumbler run is occurring and no other JMTxs, it is of course much easier, but a more interesting question is what happens when there is a variety of activity going on at once: more than one tumbler, individual payments being sent etc. The following diagram shows that it still might be very feasible to carry out this linking analysis.

![](/images/Closures-TXs.png)

Worthy of note is the role played by yield generator algorithms. Yield generators ofer to mix from all of their mixdepths at different prices, generally. There is no guarantee that they will choose a different mixdepth from one transaction to the next, therefore closure mapping reuse on their part from one transaction to the next is far from unlikely. An example might be the linkage 3-6-8 in the above diagram. Is it a tumbler or simply the operation of a yield generator? It *seems* to be a good thing in the context of this analysis, as it will tend to increase obfuscation, but it's no simple matter.

## Ameliorations

1. One sweep, not multiple transactions?

 As is seen from the simple example above, using several transactions from one CMC/mixdepth to the next creates a pattern, if one uses different counterparties each time: because CMC C1 (as per the above diagram) goes to C3 in 3 different transactions, and not to any other CMC in *all* those transactions, the linkage can be detected. If there was only one transaction, that evidence would not exist. However, doing *only sweeps for the whole tumbler algorithm* would result in a victory for amount correlation - each step would use approximately the same amount, *if* the mixdepths were empty before the start. Variations can be considered such as (n CJMTxs followed by 1 SweepJMTx for mixdepth 1) (1SweepJMTx for mixdepth2) (n CJMTxs followed by 1 SweepJMTx for mixdepth3) ... , in an attempt to mix the advantages of both models: amount de-correlation by means of multiple transactions, and closure mapping de-correlation by means of sweep without closure mapping reuse.

2. Use the same counterparties.

 If the outputs from each of 3 transactions which all had inputs from C1, were to C4, C5 and C6, say, in every case, then there would be no evidence linking C1 to one of C4, C5 or C6. Thus it's specifically joining with **different parties multiple times from the same mixdepth** which causes an easy high-probability linkage between different CMCs/mixdepths. Note that 'different parties' here could include the same parties but different mixdepths, and so different closures. This suggestion is interesting, but the amount of coordination between parties required may not be very practical.

1. Not always sending to the same mixdepth in CJMTxs.
 Multiple CJMTxs spending from one mixdepth but paying to *different* mixdepths, i.e. not always to mixdepth m+1, would make the closure mapping either more difficult or impossible depending on the details. For this, it may be of considerable advantage to use more than the default number of mixdepths (5), although practical problems may limit how far this can go. Also note that might be applied to either maker bots (yield-generator) or to the tumbler, but its impact on the tumbler algorithm design would have to be carefully considered.

1. Use of more than one external spending address using the `-a` flag to `tumbler.py`.

 This is part of tumbler's design, with `-a 3` being the default. Consider the case of 3 total transactions for mixdepth m. If the first two are CJMTx and the third is a SweepJMTx to an external address, then only the first two CJMTx can be used to try to identify a mapping from the CMC C<sub>m</sub> for mixdepth m and the CMC C<sub>m+1</sub> for mixdepth m+1. As can be seen, this is useful precisely and only in connection with point 1 above; the more the CJMTxs occurring, the more likely the closure mapping will be successful, even if multiple payout addresses are used.

3. Break JMSudoku with equal sized inputs.

 Equal sized inputs and/or outputs are the basic way to defeat coinjoin sudoku in general, and certainly equal sized inputs *from different counterparties* breaks JMSudoku, and hence breaks the closure mapping approach described here. This situation arises quite frequently naturally, since coinjoin outputs are equal sized, so it is not uncommon for multiple counterparties to be consuming utxos of equal size in the inputs to a transaction. This can be encouraged or perhaps enforced.

4. Splitting change into multiple amounts

 If amount(z<sub>i</sub>) > y, create two change outputs (y, z<sub>i</sub> -y). This *considerably* increases the complexity/uncertainty of a sudoku-style analysis (more analysis is needed to establish whether it breaks it entirely). It could be achieved 'by force', if each counterparty selects sufficient utxos in their input to provide change+coinjoin amount; the disadvantage is that creating 2 change outputs means more utxos to be spent and paid for in transaction fees. If this extra change algorithm is not applied, it probably achieves little to simply create a split of change outputs (i.e. each counterparty creating more than one change output), since subset sum type analysis would still be able to find the input-change linkages as before. The additional combinatorial blowup is almost certainly not significant, considering that very small outputs will be impractical to spend (dust etc.).
 
4. High transaction volume

 The following has been kept mostly out of scope of the analysis: with every yield generator counterparty performing multiple other transactions concurrently with those for the one tumbler under consideration, it may be fairly difficult for the analyst to identify the exact set of transactions for this tumbler. It certainly complexifies the analysis, but the analysis is not computationally intensive (assuming transactions are not huge), and the closure mappings combined with fee payment are probably enough to filter the transaction data until the tumbler's subset is clear.

## Conclusions

The higher level conclusion from this analysis is something like this: while not reusing addresses prevents trivial linkages of one payment to another, to the extent that JMSudoku is possible, we have an effect similar to address reuse: "closure mapping reuse". Given the complexities of the general transaction graph, we cannot say that such reuse "breaks Joinmarket", or even "breaks the current version of the tumbler", but at the least we can say: reusing closure mappings like C1->C3 a large number of times is dangerous, and clearly we want to err on the side of caution, to whatever extent is practical. 

The two principal ways to address this: either break JMSudoku or avoid closure mapping reuse. Breaking of JMSudoku via modification of change outputs or changes to input selection should also be investigated, but is likely to be imperfect, at least, in practice (it can be made perfect, but only by using entirely impractical coinjoin designs like N equal inputs, N equal outputs). Avoiding or strictly limiting closure mapping reuse is much more practical, but requires careful thought.
