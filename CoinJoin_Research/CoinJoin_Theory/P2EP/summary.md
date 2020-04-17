|               	| 				|
| ----------- 		| ----------	| 
| Project Name 		| P2EP / PayJoin |
| Dev				| Multiple	|
| Page				| Multiple	|
| Paper				| NA		|

A meeting took place in which a number of individuals developed P2EP. 
Some summaries / overviews are:
- [P2EP Meeting Overview](https://medium.com/@nopara73/pay-to-endpoint-56eb05d3cac6) by Adam Fiscor (Nopara73)
- [Block Digest_118 from 40:30](https://youtu.be/0-DS7X99F7Y?t=2415) by Adam Gibson (Waxwing)
- [P2EP overview](https://blockstream.com/2018/08/08/en-improving-privacy-using-pay-to-endpoint/) by Matthew Haywood

Waxwing later proposed the varient of P2EP called PayJoin
- [PayJoin](https://joinmarket.me/blog/blog/payjoin/) by Waxwing
- [Demo](https://joinmarket.me/blog/blog/payjoin-basic-demo/)

There are currently 3 live implementations;
- A feature in Samourai Wallet called [Stowaway](https://samouraiwallet.com/stowaway)
- A feature in Joinmarket ([PayJoin](https://github.com/Joinmarket-Org/joinmarket-clientserver/blob/master/docs/PAYJOIN.md))
- A feature in BTCPayServer called [P2EP](https://blog.btcpayserver.org/btcpay-server-1-0-4-0/) ([Specification](https://blog.btcpayserver.org/btcpay-server-1-0-4-0/), [Guide](https://docs.btcpayserver.org/features/payjoin))

There are plans for implementation in the following wallets;
- [Wasabi Wallet](https://github.com/zkSNACKs/WalletWasabi/pull/3528)
- [Blue Wallet](https://github.com/BlueWallet/BlueWallet/pull/984)
- [Blockstream Green](https://blockstream.com/2020/04/16/en-bitcoin-privacy-improves-with-btcpay-servers-p2ep-implementation/)

See Also
- [BustaPay](https://github.com/6102bitcoin/CoinJoin-Research/tree/master/CoinJoin_Implementations/13_BustaPay-rhavar)

# Further Reading
- https://en.bitcoin.it/wiki/PayJoin

# Implementations

There are currently 3 live implementations;
- A feature in Samourai Wallet called [Stowaway](https://samouraiwallet.com/stowaway)
- A feature in Joinmarket ([PayJoin](https://github.com/Joinmarket-Org/joinmarket-clientserver/blob/master/docs/PAYJOIN.md))
- A feature in BTCPayServer called [P2EP](https://blog.btcpayserver.org/btcpay-server-1-0-4-0/) ([Specification](https://blog.btcpayserver.org/btcpay-server-1-0-4-0/), [Guide](https://docs.btcpayserver.org/features/payjoin))

There are plans for implementation in the following wallets;
- [Wasabi Wallet](https://github.com/zkSNACKs/WalletWasabi/pull/3528)
- [Blue Wallet](https://github.com/BlueWallet/BlueWallet/pull/984)
- [Blockstream Green](https://blockstream.com/2020/04/16/en-bitcoin-privacy-improves-with-btcpay-servers-p2ep-implementation/)


# Simple Example

Assume a store accepts payments via payjoin which are limited to 2 inputs, 2 outputs.

User 1 buys a product worth 0.05 BTC with payjoin, providing an input of 0.1 & recieving change of 0.05

INPUTS(User1, Merchant) -> OUTPUTS(User1, Merchant)

INPUTS(0.1, 0.2) -> OUTPUTS(0.05, 0.25)

This is a Steganographic transaction, it is **indistinguishable onchain as a PayJoin** because there is an output which is greater than the largest input && there is no subset of the inputs that would be sufficient to make this output, *i.e. There are no redundant inputs*.

# Limitations

The fact that some payjoin transactions are steganographic should not be misunderstood to mean that all payjoins are non-trivial to figure out, particularly if the snowballing of the receiver utxo's is done in a non steganographic way.

If the sending wallet is restricted to only steganographic transactions then it is likely that the sender will either;
- Need many utxo's to pick from
- Be unable to participate in many potential PayJoin transactions
- Need to pre process utxo's to make it possible to participate regularly.

As such, payjoin is not strictly superior to a CoinJoin. 
An equal output CoinJoin is not steganographic like PayJoin can be, but it is a useful tool for breaking deterministic links & has other benefits which PayJoin doesn't offer.
They are both types of multiparty bitcoin transactions.
Other types include CoinSwap & CoinMerge.

# Simple Chain Analysis Example

Now suppose User 1 in the above example was a chain analysis company.

The chain analysis company logs that the output worth 0.025 belongs to the merchant.

User 2 (a normal user) buys a product worth 0.2 with payjoin, providing an input of 0.5 & recieving change of 0.3. 
Merchant uses the output from the previous payjoin as an input in this one.

From the perspective of the chain analysis company:

INPUTS(Merchant, ?) -> OUTPUTS(?, ?)

INPUTS(0.25, 0.5) -> OUTPUTS(0.45, 0.3)

The chain analysis company detect that there is a redundant input here (the 0.025 input is not required to pay a 0.045 output).
As such, they may flag as a possible payjoin. 

They can compute the possible scenarios:
- Scenario1, Merchant paid 0.2 BTC: 0.25->0.45 (+0.2) , 0.5->0.3 (-0.2)
- Scenario2: Merchant pays 0.05 BTC: 0.25->0.3 (+0.05), 0.5->0.45 (-0.05)

They know that it's possible (maybe even likely) that the merchant is getting paid by another user via payjoin, thus they conclude that Scenario1 is highly likely.

They can then track the resulting output (0.45) which they believe to be the merchant and repeat.

Additionally they now suspect that the user spent 0.2 BTC at the store, which could later be useful information.

# Breaking Simple Chain Analysis Example

- Don't limit to 2in2out
- Merchant spends at other merchants who use payjoin (Scenario2)
- Merchant constructs transactions with redundant inputs to create false flag PayJoins
- Merchant uses PayJoin to make payment (the output they provide is a payment to some other user)
- Wallets construct transactions with redundant inputs to create false flag PayJoins

# Fake PayJoin Implementations

There are currently no wallets which have an explicit fake payjoin feature (where a redundant input is used).

