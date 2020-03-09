# Combinatoric Considerations

A caution against using 'computational infeasibility' to avoid linking inputs to outputs (aka CashFusion).

_Notes / Thoughts by 6102bitcoin based on [WRC08](https://www.youtube.com/watch?v=bpLOSytc7vc)_

- It is a privacy guarantee which gets weaker with every day of technological advancement

- For Chain Analysis companies is this a search or an optimisation problem?
Maybe they only care about 1 participant or only need a certain confidence / precision which dramatically reduces the difficulty of finding a solution.

- Treating the whole of the invalid search space as relevant is potentially misleading.
Certain behaviour may be possible but highly implausible, e.g. 99 inputs from 1 user.
Also unclear whether there will be many similar mappings which result in poor privacy for a certain input.

- To follow on from above point, is the effectiveness of the scheme measured according to improvement to privacy on average or the implications for the user who gains the least privacy?

- Computational hardness against linear programming with suitable limitations (e.g. limiting inputs per user) is potentially weaker than the Bell / Stirling number would suggest.
Especially if precision does not need to be very high / confidence required is not very high.

Additionally, the Method is;
- Highly dependent on the number of inputs/outputs
- Highly sensitive to post-mix behaviour
- Highly dependent on the max number of inputs contributed by a single user
- Highly sensitive to pre-mix behaviour

As such, the Bell number should not be treated as security parameter - reality is much more complex than that and the realistic search space may by far far smaller than the bell number would suggest.
