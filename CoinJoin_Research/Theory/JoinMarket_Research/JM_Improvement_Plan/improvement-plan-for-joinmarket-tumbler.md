# Plan to improve the privacy of JoinMarket's tumbler script

24/02/2019

JoinMarket has a tumbler application which aims to send bitcoins in a way that delinks the origin and destination.

I have some thoughts on how and why to improve the tumbler algorithm.

Feel free to bikeshed some of these parameters (averages, counts, etc), as my important points are about other stuff.

Many of the thoughts in this post came to me while writing the [big bitcoin privacy literature review article of winter-2018](https://en.bitcoin.it/wiki/Privacy).

Following review from other people interested in JoinMarket, I'll try to implement these ideas soonish.

## Wait longer between coinjoins and switch to uniform distribution 

Waiting longer is free in money but costly in time. It increases the anonymity set by forcing an adversary to consider the longer time period.

The maximum wait time should be (finger in the air time) 2 hours, which is an average wait time of 1 hour.

Right now the tumbler waits a number of minutes drawn from an exponential distribution with an average of 30 minutes.

But the exponential distribution clumps up the txes towards the beginning of the time interval. In hindsight the exponential distribution was just cargo-culting; I copied the distribution of bitcoin block intervals.

## Generate amount fractions from the uniform distribution 

Right now amount fractions are generated from a power law with a default exponent of 100(!) That exponent makes no sense. Using a power law doesn't have a justification either.

The power law distribution is essentially cargo culting from me back in 2015, it came from a vague idea that everything in money and economics is a power law.

Also the random variable is a fraction so I'm not sure power law makes sense there.

Uniformly chopping up the interval [0, 1] is probably best. For example, to split up the interval [0, 1] into 3 chunks, generate 2 random numbers X and Y in [0, 1] then the three chunks are (X, Y-X, 1-Y) i.e. the random numbers are knives that tell you where to cut the real line.

## Increase the number of coinjoin counterparties 

This modification increases privacy by involving more entities. Consider the case where a taker creates 10 coinjoins each with 2 other counterparties, and compare that to creating 3 coinjoins each with 10 counterparties. The former case can have the same makers used many times for coinjoins, not so in the latter case which has more maker entities involved. So it's reasonable to say it has more privacy. Therefore leaning towards higher maker counts instead of more transactions seems that it would improve privacy.

This modification also makes coinjoins harder to untangle into their constituent makers and taker inputs. That analysis depends on solving a subset-sum problem using the amounts of the inputs and outputs. It can lead to clustering together inputs which are owned by individual coinjoin peers and linking them with their change addresses.

The paper (_Möser, Malte and Rainer Böhme. “Join Me on a Market for Anonymity.” (2016)._) studying JoinMarket transactions tried to do this subset-sum analysis. It studied the coinjoins in the years 2015-16 when JoinMarket mostly created 3-party coinjoins, yet it was still unable to fully solve for the makers and taker's inputs in about a third of all coinjoins. The Appendix shows an email exchange between me and an author of that paper who confirms that increasing the maker count would improve the privacy situation with subset-sum solving.

The sendpayment script should also have its default number of counterparties increased to match what tumbler does.

#### If N counterparties cant be found then search for N-1 counterparties

One thing stopping the counterparty-count parameter from being increased is that sometimes there may not be enough counterparties in the orderbook. If so then the tumbler script will stall.

Instead we should use an algorithm that searches for N counterparties and if it can't find them then search for N-1, recursively, down to a minimum counterparty count (probably 3) below which the function will return fail.

I think the default maximum number of counterparties to search for should be 15 (but as before, feel free to bikeshed). If the tumbler cant find that many counterparties and settles for 12 or 10 instead then that's fine.

## Reduce number of coinjoins

The previous modication of increasing the counterparty count has the effect of using more block space and hence costing more in miner fees.

We can partially counteract that by reducing the total number of transactions. And also as previously examined: more counterparties beats more transactions.

I think the number of coinjoins per mixdepth should be 2 or 3.

## Add a routine at the start of the tumbler schedule where all mixdepths are fully-spent with a no-change-coinjoin 

Equal-output coinjoins [reveal their change addresses](https://en.bitcoin.it/wiki/Privacy#Equal-output_CoinJoin). A way to avoid this is to create no-change-coinjoins also called sweep-coinjoins. A naïve question might be why doesn't the tumbler script _only_ create such no-change-coinjoins? The answer is then it would be easy to follow the trail of coins, because makers virtually-never create no-change-coinjoins. So to unmix such a tumbler script only requires following the coinjoin outputs which are later used to create no-change-coinjoin transactions. What tumbler should aim to do is create coinjoins that are in the same anonymity set as yield-generator coinjoins (and to a lesser extent send-payment coinjoins), and that requires that they create change addresses.

However without loss of privacy we can create no-change-coinjoins using coins that are sent into the wallet from outside JoinMarket. Consider when a user buys coins from an exchange where they give up all their personal dox because of AML/KYC, and they send the coins straight into a JoinMarket wallet. The exchange will know that the spending transactions are JoinMarket coinjoins, and if there was a change address then the exchange could still link it to the user. So no-change-coinjoins are appropriate here.

Therefore the proposal is that stage 1 of the tumbler script will sweep every mixdepth into one no-change-coinjoin, and stage 2 will be the same as today with with-change-coinjoins of randomly-generated amounts being sent to the next mixdepth and ultimately to the destination.

The no-change-coinjoins will also help with amount-based tracking. Imagine if the user bought 1.78213974 BTC from an exchange and they create a no-change-coinjoin with 15 other counterparties, that would result in 16 UTXOs having a face value of (slightly less than) 1.78213974 BTC. An adversary who uses tracking based on amounts now has to contend with 15 other UTXOs worth the same amount.

The wait time between all the no-change-coinjoins should be made quite long so they're not linked together (i suggest max 4 hours, with an average of 2 hours), and the wait time between with change-coinjoins can be shorter.

## Sometimes create coinjoins with round number amounts

When people use the sendpayment script they choose the coinjoin amount themselves. Humans choosing payment amounts gives rise to round numbers, either in bitcoin (eg. 1 BTC, 0.1 BTC, 0.01 BTC) or in another currency (2.24159873 BTC which when converted to USD may be close to $100). Tumbler should replicate this behaviour.

It should be done in two ways: 1) Occasionally chop off some decimal places (ie. uses the round() function) so that there are only 1 to 3 significant figures 2) Query bitcoin exchange rates and choose a round number amount of some fiat currency which is near the randomly-generated number being sent.

There is a paper that analyses the blockchain with round numbers to try to detect the geographical economic location of bitcoin users (_"Gervais, Arthur & Ritzdorf, Hubert & Lucic, Mario & Lenders, Vincent & Capkun, Srdjan. (2016). Quantifying Location Privacy Leakage from Transaction Prices. 9879. 382-405. 10.1007/978-3-319-45741-3_20. "_). The paper has some measurements which we could copy for choosing which fiat currencies to use in which proportion, but its probably good enough to guess the weights ourselves eg. USD 70%, EUR 20%, JPY 3% and so on.

## Appendix

    >
    > Hello,
    >
    > I'm reading your 2016 paper Join Me On A Market For Anonymity.
    > This is written:
    >
    > "To tell apart takers’ inputs from makers’ inputs, we use subset
    > matching (cf. [5, 26]). We could unanimously identify the taker’s subset
    > of inputs and outputs for 5,788 transactions (67 %). In these cases, the
    > taker’s subset is the combination that loses value. The makers’ subsets
    > usually increase as they collect a maker fee from the taker."
    >
    > I'm very interested in the 67% figure, why couldn't you separate the
    > taker's and maker's UTXOs in 100% of cases? What happened in the 33% of
    > transactions where it wasn't possible to find the taker's UTXOs?
    >
    > Thanks in advance,
    >
    > Regards
    > Chris Belcher
    
    Hi Chris,
    if I remember correctly, there were two cases where we couldn’t tell them apart:
    
    a) there were multiple possibilities to group inputs/outputs into subsets
    b) there were too many inputs and outputs, making subset matching computationally infeasible (at least with my algorithm)
    
    Best,
    Malte
