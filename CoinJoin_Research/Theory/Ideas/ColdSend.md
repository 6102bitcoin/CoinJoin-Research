# ColdSend
## Send CoinJoin UTXO's to Cold Storage in a privacy preserving way with minimal user input.

### Motivation
Currently for a user to send mixed UTXO's to their Cold Storage they are advised to do so manually with great care to;
- Avoid merging utxo's (inc. dust).
- Avoid address reuse.
- Avoid use of same feerate (could make it easier to link tx's to one user).
- Avoid sending all transactions in one session (vunerable to timing analysis).
- Avoid use of wallet software made by hardware wallet providers (ledger & trezor software sends xpub to wallet server - linking utxo's)

### Required Work

Sending to Cold Storage could be simplified with the proposed ColdSend concept which requires the following 7 pieces of work;

1. Standardise ColdSend-Keychain.txt - A standard format for passing multiple addresses (not an xpub) from Cold Storage wallets to the CoinJoin tool.
2. Standardise ColdSend-QueueTX.txt  - A standard format for saving ready to broadcast tx's with suggested broadcast dates & times to lower risk of timing analysis. 
3. Add functionality within Cold Wallet tools to export ColdSend-Keychain.txt files.
4. Add functionality within CoinJoin tools to import ColdSend-Keychain.txt files
5. Add functionality within CoinJoin tools to export ColdSend-QueueTX.txt files
6. Add functionality within CoinJoin tools to import ColdSend-QueueTX.txt files
7. Add functionality within CoinJoin tools to automate broadcasting the tx's (from ColdSend-QueueTX.txt) in a privacy preserving way.

### Desired workflow
 
**Setup - Cold Storage Wallet Side**
- User opens Cold Storage wallet (i.e electrum with multisig with multiple hardware wallets using EPS /or/ Wasabi with Hardware Wallet)
- User navigates to /ColdSend/Keychain/Export
- User selects number of addresses to add to ColdSend-Keychain.txt (default could be, say, 100)
- User enters a password to encrypt ColdSend-Keychain.txt before file is saved
- ColdStorage Wallet automatically marks these as used to avoid address reuse (see concern 1)

**Setup - CoinJoin Tool Side**
- User opens CoinJoin Tool (i.e. Wasabi / Whirlpool / JoinMarket)
- User navigates to /ColdSend/Keychain/Import
- User enters password to decrypt ColdSend-Keychain.txt

**Use**
- User opens CoinJoin Tool and selects /ColdSend/QueueTX/Export
- User selects UTXO's they wish to send to cold storage (limited to number of unused Cold Storage Keychain addreses).
- They set the max fee they wish to pay 
- They set the max time they are willing to wait for all utxo's to be sent from the current date / blockheight.
- CoinJoin Tool presents overview of tx's and awaits user approval
- Upon approval, CoinJoin Tool signs tx's & they are saved locally (not broadcast) alongside the intended broadcast time & date (or blockheight) in a file called 'ColdSend-QueueTX.txt'  
- This file could be encrypted with the wallet password or with the (previously used) keychain password (see concern 2). 
- If CoinJoin Tool runs 24/7 tx's are broadcast when intended broadcast time & date (or blockheight) are reached.
  Wallet would have to be running but only with access to broadcast tx
  ColdSend-QueueTX.txt would have to be decrypted 
- If CoinJoin Tool runs intermittently tx's could be broadcast at next launch of the software after intended broadcast time & date (see concern 3)
  In this scenario the ColdSend-QueueTX.txt file could be encrypted and a second file (ColdSend-QueueTXtimes.txt) containing only the index & indended broadcast time & date could be saved unencrypted.

### Example Formats for ColdSend files

Example format for ColdSend-Keychain.txt `Index:Addr i.e. 00001:bc1#######################`
Example format for ColdSend-QueueTX.txt `Index:rawtx:Date:Time i.e. 00001:##rawtx###:20190817:1200`

### Concerns:
1. - When recovering wallet user will have to ensure the keychain length (say 100) is less than the cutoff setting in the wallet (after X empty addresses stop searching addresses and assume ok to use).
2. - If anyone accesses ColdSend-QueueTX.txt and it is unencrypted it would be damaging to privacy. If encrypted it can't be used automatically.
3. - If user opens CoinJoin Tool at regular time this could make the tx's succeptible to timing analysis (time of day) but less likley an issue. 

### Dedicated ColdSend Software:
- To reduce overhead on each project a standalone opensource tool could be developed to import the ColdSpend-QueueTX.txt file and broadcast these tx's at the desired time/date (or blockheight)
- The tool could send out tx's when the mempool is empty and transactions could be signed multiple times for a range of fee-rates to ensure that you can always broadcast the tx if fees increase, or reduce fees if fee rate drops.
- This software needn't be complicated as it could use tor to connect to a broadcast service & refresh identity between each broadcast.

### xpub
- You could simply pass an xpub from your Cold Storage Wallet to your CoinJoin Tool. 
- This is simpler but the potential for accidental address reuse is higher and any compromises to your CoinJoin Tool computer could leak your xpub affecting your other coldstorage coins.
- If an address private key and a single address are hacked, the xpub can be found and all addresses are linked. 
- If the address-reuse can be avoided and the above risk is deemed minimal then wallets could still use the suggested fee rate variance & time varience ideas to preserve privacy
