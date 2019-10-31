FAQ - CoinJoin

By [6102bitcoin](https://twitter.com/6102bitcoin)

# Background

Bitcoin transactions are public by nature; they map inputs (unspent utxo's) to outputs (new unspent utxo's) in a way that is auditable by anyone with access to the bitcoin blockchain (the history of transactions).

# The Problem

Because anyone can see the links between transaction inputs and outputs it's possible for anyone to analyse previous transaction behaviour in an attempt to link transactions and utxo's together, this process is sometimes called clustering.

Some companies specialise in this kind of analysis of the bitcoin blockchain and are known as 'Chain Analysis' companies. Some well known examples are chainalysis & crystal.

These companies claim that the purpose of this clustering is to 'detect fraud' or 'identify criminals'.
Despite their best efforts it is highly likely that they will at some point misidentify the owner of a utxo resulting in wrongful conviction as law enforcement blindly trusts these systems.

Alternately, clustering could just as easily be done by malicious adversaries who wish to identify people to target for ransom or blackmail.

Future criminals may intentionally create transactions in order to trick chain analysis companies into misidentifying users, allowing them to evade detection (after all, who continues searching for evidence after the criminal has been caught?)

Crucially, a user who's transactions / utxo's have been clustered will be unaware that this has happened and once the transactions have been made it is impossible to erase the trail on the blockchain.

# The (start of a) Solution - CoinJoin

Fortunately an innovative method of obfuscating the on-chain links between utxo's was explained by Greg Maxwell back in 2013 - he called it CoinJoin.

The basic idea is that a transaction is created with inputs from multiple users and outputs belonging to the same users.

The transaction is constructed such that it is not possible for someone analysing the blockchain to determine which output belongs to which user.

Let us look at a worked example;

Alice, Bob and Charlie are three individual bitcoin users looking to CoinJoin their utxo's

- Input 1: Alice's 0.1 BTC utxo from an exchange. 
- Input 2: Bob's 0.1 BTC utxo from the sale of a baseball card to a guy online. 
- Input 3: Charlie's 0.1 BTC utxo which he wants to one day give to his baby daughter.

Background information on why each participant wants to mix:
- Alice doesn't want the exchange to monitor her spending.
- Bob doesn't want the baseball guy to see how much bitcoin he has.
- Charlie he lives in a despotic country where owning bitcoin is illegal.

The CoinJoin transaction takes these three inputs and constructs a transaction which creates 3 new outputs

```
Input 1: 0.1 BTC (Alice)        Output 1: 0.1 BTC
Input 2: 0.1 BTC (Bob) 	    ->  Output 2: 0.1 BTC
Input 3: 0.1 BTC (Charlie)      Output 3: 0.1 BTC
```

It is not possible for someone analysing this transaction to identify which output is owned by which user.

# (Start of a) Solution?

The CoinJoin process explained above obfuscates the on-chain links.
This is a start - but as with many things the devil is in the details.

Lets break the process of participating in a CoinJoin down into 3 stages.
- Stage 1 | Pre-Mix : How you put inputs into a CoinJoin in a privacy preserving way
- Stage 2 | Mix : How the CoinJoin itself happens in a privacy preserving way
- Stage 3 | Post-Mix : How you use the CoinJoin outputs in a privacy preserving way

## Stage 1 | Pre-mix
I will add information about Stage 1 in the near future.

## Stage 2 | Mix

How the CoinJoin itself happens in a privacy preserving way.

Someone has to coordinate the construction of the CoinJoin transaction, lets work through the possible coordination approaches:

**Coordination Approach 1: Risk of privacy loss & bitcoin loss (DO NOT DO THIS)**

If Alice, Bob and Charlie are acquainted and fully trust each other with their bitcoin and their privacy then any one of them could coordinate the construction of this transaction with minimal effort - they would all share the private key's of their coins, one user would import these coins into a wallet and make a transaction paying out to each users new address.

**Coordination Approach 2: Risk of privacy loss**

An incremental improvement would be for one member of the group to collect the required information from each user and create a transaction which each user then individually signs.

The benefit With this approach is that there is no risk of loss of bitcoin (provided each user checks that the transaction they are signing sends their funds to addresses they wish to).

**Coordination Approach 3: No Risk of loss**

It is clearly preferable if Alice, Bob and Charlie can construct a transaction without having to trust anyone with either their bitcoin or their privacy.

This can be achieved by using blinded signatures to construct the transaction in such a way that each participant;
- Retains full control of their bitcoin at all times
- Is the sole individual who knows which output belongs to them

I won't go into the details here (at least not for now) but suffice to say that this **is possible** and much better than Coordination Approach 1 or 2.

## Stage 3 | Post mix

I will add information about Stage 3 in the near future.

# The Implementations

There have been many projects which attempted to make it possible for users to CoinJoin their utxo's, the three that are currently active are:
- [JoinMarket](https://github.com/JoinMarket-Org/joinmarket-clientserver)
- [Wasabi](https://wasabiwallet.io)
- [Whirlpool](https://github.com/Samourai-Wallet/Whirlpool)

I will attempt to provide a brief explanation of each tool.

## JoinMarket:
The core principle of JoinMarket is that markets are an efficient way to incentivise users to CoinJoin.

The [wiki](https://en.bitcoin.it/wiki/JoinMarket) describes this eloquently:

> A CoinJoin transaction requires other people to take part. The right resources (coins) have to be in the right place, at the right time, in the right quantity. This isn't a software or tech problem but an economic problem. JoinMarket works by creating a new kind of market that allocates these resources in the best way.

> This works by allowing coinjoin transactions to be paid-for. On one side there are time-rich coinjoiners who collect fees when other peers create coinjoins with them, called market makers. On the other side there are time-stressed coinjoiners who can coinjoin instantly and pay a fee, called market takers.

Put simply, JoinMarket makes it possible for individuals to pay other individuals to mix with them. Because this is a free market there are competitive fees.

I haven't dedicated enough time to getting JoinMarket running - the documentation is thorough but somewhat involved.
I will provide a more detailed review / comparison once I have tested the software myself - In the meantime I encourage you to give it a go also.

## Wasabi
Wasabi consists of a wallet which allows you to receive bitcoin, optionally mix, and then send bitcoin.

- Stage 1 | Pre-Mix : All communication done over TOR, [BIP 158](https://github.com/bitcoin/bips/blob/master/bip-0158.mediawiki) Block Filters (*see note*)
- Stage 2 | Mix : Coordination Approach 3
- Stage 3 | Post-Mix : utxo labelling & coin control, broadcast over TOR via random node

*Note on BIP 158*

*From the [Wasabi Docs](https://docs.wasabiwallet.io/FAQ/FAQ-UseWasabi.html#what-are-bip-158-block-filters)*

> The Wasabi coordinator will send you ... block filters, and you check locally if the block contains a transaction with your coins.
> If not, then the filter is stored for later reference and for syncing new wallets.
> If yes, then the wallet connects to a random Bitcoin peer-to-peer full node to request this entire block.
...
> For every block download, Wasabi establishes a new and unique tor identity, meaning that it is not easy to link that it is the same entity downloading all these blocks.

*Note*: BIP 158 is not as good as running your own node. You trust
- The Wasabi server gives you the correct filters
- The Wasabi server to not withhold any filters
- The block you download from a P2P node is actually in the valid chain

## Whirlpool
Whirlpool is a mixing tool which extends the functionality of the Samourai Wallet (SW) application for Android to include CoinJoin capabilities.
- Stage 1 | Pre-Mix : All communication done over TOR, Connect to own node or SW developers node (*see note*)
- Stage 2 | Mix : Coordination Approach 3
- Stage 3 | Post-Mix : utxo labelling & coin control, broadcast over TOR via your own node or SW developers node (*see note*)

*Note on using Own node or SW developers node*

Unless you connect to your own node you are trusting the SW developers not to log (I will expand on this in the near future)
- You should run your own DOJO node if you are using SW
- If you are mixing and not connected to your own node you are at risk of damaging your privacy (again you are trusting the SW developers not to log)
- If you are mixing and are connected to your own node but are exclusively mixing with participants who aren't connected to their own node be aware that you are trusting SW developers not to log to gain any privacy benefit
- If you are mixing and are connected to your own node and are mixing with at least one participant who is also connected to their own node you will still get some privacy benefit if the SW developers are logging
