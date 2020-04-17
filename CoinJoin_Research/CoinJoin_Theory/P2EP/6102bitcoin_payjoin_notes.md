# Some notes about payjoins
- Simple Chain Analysis

#### Simple Chain Analysis Example

Assume a store accepts payments via payjoin which are limited to 2 inputs, 2 outputs.

User 1 (`chain analysis company`) buys a product worth 0.05 BTC with payjoin, providing an input of 0.1 & recieving change of 0.05

INPUTS(User1, Merchant) -> OUTPUTS(User1, Merchant)
INPUTS(0.1, 0.2) -> OUTPUTS(0.05, 0.25)

*Note: This is indistinguishable onchain as a PayJoin because there is an output which is greater than the largest input && there is no subset of the inputs that would be sufficient to make this output, i.e. There are no redundant inputs*

The chain analysis company logs that the output worth 0.025 belongs to the merchant.

User 2 (`normal user`) buys a product worth 0.2 with payjoin, providing an input of 0.5 & recieving change of 0.3. 
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

#### Breaking Simple Chain Analysis Example

- Don't limit to 2in2out
- Merchant spends at other merchants who use payjoin (Scenario2)
- Merchant constructs transactions with redundant inputs to create false flag PayJoins
- Merchant uses PayJoin to make payment (the output they provide is a payment to some other user)
- Wallets construct transactions with redundant inputs to create false flag PayJoins
