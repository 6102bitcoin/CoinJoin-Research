[Posted](https://bitcoin.stackexchange.com/questions/87324/solving-subset-sum-for-two-sets/92652#92652) by Nopara73 on  Jan 4 2020

# Resources

- [Anonymous CoinJoin Transactions with Arbitrary Values](https://www.comsys.rwth-aachen.de/fileadmin/papers/2017/2017-maurer-trustcom-coinjoin.pdf) discusses the optimized and non-optimized version of it. In this reply I will discuss the non-optimized version of it.
- [CoinJoin Sudoku](https://www.coinjoinsudoku.com/) may also be something to look up.

# Tooling

I wrote a small command line tool in .NET Core that anyone can play around with. You can either provide an input and output list to it or a real txid. In case of txid, it will fetch the transaction from SmartBit and analyze that.

```Provide inputs or transaction ID! Example: 21,12,36,28.1 or 0f9f3b68f369b3b95779284d4d0607cb8f5051055c2e1b1813848370496e95aa
21,12,36,28.1
Provide outputs! Example: 25,8,50,14.1
25,8,50,14.1
```

Given `21,12,36,28.1` input list, and `25,8,50,14.1` output list the tool will output 2 sub mappings:

```Sub mappings:
21,12,36,28.1 -> 25,8,50,14.1
21,12 -> 25,8 | 36,28.1 -> 50,14.1
```

The first sub mapping (`21,12,36,28.1 -> 25,8,50,14.1`) is the transaction as it appears in the blockchain, it is called the non-derived mapping. This is the case if the transaction wasn't a coinjoin to begin with.

The second is a derived mapping (`21,12 -> 25,8 | 36,28.1 -> 50,14.1`). In this case it was a coinjoin with 2 participants, as 2 sub transaction has been identified.

However there is another important analysis that can be done on this coinjoin. We can tell what is the probability of two inputs or outputs are in the same transaction:

```Input match probabilities:
21 - inputs: 12(1) 36(0.5) 28.1(0.5) | outputs: 25(1) 8(1) 50(0.5) 14.1(0.5)
12 - inputs: 21(1) 36(0.5) 28.1(0.5) | outputs: 25(1) 8(1) 50(0.5) 14.1(0.5)
36 - inputs: 21(0.5) 12(0.5) 28.1(1) | outputs: 25(0.5) 8(0.5) 50(1) 14.1(1)
28.1 - inputs: 21(0.5) 12(0.5) 36(1) | outputs: 25(0.5) 8(0.5) 50(1) 14.1(1)

Output match probabilities:
25 - inputs: 8(1) 50(0.5) 14.1(0.5) | outputs: 21(1) 12(1) 36(0.5) 28.1(0.5)
8 - inputs: 25(1) 50(0.5) 14.1(0.5) | outputs: 21(1) 12(1) 36(0.5) 28.1(0.5)
50 - inputs: 25(0.5) 8(0.5) 14.1(1) | outputs: 21(0.5) 12(0.5) 36(1) 28.1(1)
14.1 - inputs: 25(0.5) 8(0.5) 50(1) | outputs: 21(0.5) 12(0.5) 36(1) 28.1(1)
```

For example input with value `21` and input with value `12`, there's 100% chance they are in the same sub-transaction, however input `21` with output `50`, there's only 50% chance that they are in the same sub-transaction.

# Example 2: Output for 2,3,4->4,5

For completeness here's the output for the numbers that were present in the question.

```Sub mappings:
2,3,4 -> 4,5
2,3 -> 5 | 4 -> 4

Input match probabilities:
2 - inputs: 3(1) 4(0.5) | outputs: 4(0.5) 5(1)
3 - inputs: 2(1) 4(0.5) | outputs: 4(0.5) 5(1)
4 - inputs: 2(0.5) 3(0.5) | outputs: 4(1) 5(0.5)

Output match probabilities:
4 - inputs: 5(0.5) | outputs: 2(0.5) 3(0.5) 4(1)
5 - inputs: 4(0.5) | outputs: 2(1) 3(1) 4(0.5)
```

# Background

Our basic building block is partitioning, so in order to understand the algorithm you must understand partitioning first. While understanding what the Bell Number is, not essential to understand the algorithm, it is essential to understand the limitations of this algorithm.

# Definition of Bell Number

The Bell Number is the number of partitions of a set.

# Examples

## Empty Set

Set:
```

```

Partitions:
```

```

Bell Number: 1

## Set with 1 element

Set:
```
a
```

Partitions:
```
a
```

Bell Number: 1

## Set with 2 elements

Set:
```
ab
```

Partitions:
```
ab
a b
```

Bell Number: 2

## Set with 3 elements

Set:
```
abc
```

Partitions:
```
abc
ab c
ac b
bc a
a b c
```

Bell Number: 5

# All Bell Numbers

` 1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147, 115975, 678570, 4213597, 27644437, 190899322, 1382958545, 10480142147, 82864869804, 682076806159, 5832742205057, ...`

# Application to CoinJoin

Given a transaction with 100 inputs, assuming brute forcing, one would need to iterate through Bell Number of 100 elements number of partitions in order to find valid partitions. The Bell Number of 100 elements is `47585391276764833658790768841387207826363669686825611466616334637559114497892442622672724044217756306953557882560751`.

# Non-Optimized Algorithm

First we need to iterate through all the input and output partitions.


``` foreach (var inputPartition in inputPartitions)
{
    foreach (var outputPartition in outputPartitions)
    {
```

Then we need to iterate through all parts of the input partition and find out if we have corresponding output partition part:

``` foreach (var inputPartitionPart in inputPartition)
{
    var foundValidOutputPartitionPart = remainingOutputPartition.FirstOrDefault(x => x.Sum() == inputPartitionPart.Sum());
```

If we find such valid output partition part, and we also only find valid parts when comparing the remaining parts, then we found a valid mapping.

# The Code

For reference the relevant codeblock looks like this. You may notice I made some optimizations to make it less painfully stupid.

``` var outputPartitions = Partitioning.GetAllPartitions(outputs.ToArray());
var inputPartitions = Partitioning.GetAllPartitions(inputs.ToArray());

foreach (var inputPartition in inputPartitions)
{
    foreach (var outputPartition in outputPartitions.Where(x => x.Length == inputPartition.Length))
    {
        var remainingOutputPartition = outputPartition;
        var validPartition = true;
        var subSetsBuilder = new List<(IEnumerable<decimal> inputs, IEnumerable<decimal> outputs)>();
        foreach (var inputPartitionPart in inputPartition)
        {
            var foundValidOutputPartitionPart = remainingOutputPartition.FirstOrDefault(x => x.Sum().Almost(inputPartitionPart.Sum(), Precision));
            // https://www.comsys.rwth-aachen.de/fileadmin/papers/2017/2017-maurer-trustcom-coinjoin.pdf
            // input partitions that include a set
            // with a sum that is not a sub sum of the outputs cannot
            // be part of a mapping
            if (foundValidOutputPartitionPart is null)
            {
                validPartition = false;
                break;
            }
            else
            {
                subSetsBuilder.Add((inputPartitionPart, foundValidOutputPartitionPart));
            }
        }

        if (validPartition)
        {
            var mapping = new Mapping(subSetsBuilder, Precision);
            mappings.Add(mapping);
            yield return mapping;
        }
    }
}
```

# Discussion

Notice this approach has a benefit compared to the optimized version, that it does not use recursion.
