# In more basic terms

The analysis compares a particular balance among three mutation routes across experimental contexts. Before comparison, recovery controls try to correct for some routes being easier to recover or detect than others.

A difficulty remains: control material can recover differently from biological material. If that difference varies by route and by context, it can make the route balances appear different even when the biological balance is the same.

This package asks how much such mismatch would be enough to explain an apparent difference. It starts from previously calculated uncertainty intervals, enlarges them using an explicitly assumed mismatch range, and checks whether the intervals can share a common value. Sampling uncertainty and assumed recovery mismatch both count.

The factor `R` describes the mismatch in the recovery **change between baseline and selected branches**, relative to the change measured by controls. At `R=1.25`, each differential residual may lie between 0.8 and 1.25. Those are sensitivity assumptions, not measured error bars. Bounding each branch separately would allow more total mismatch and require a different calculation.

All 40 strongly separated synthetic examples still reject a common balance at factors up to 1.25. All become compatible by 1.5. Their individual switching points range from about 1.263 to 1.420. This tells us how sensitive that statistical procedure is to its recovery assumptions. It does not tell us that actual laboratories have this amount of mismatch, that the biological balances are equal, or that the underlying mechanism is established.

The other 120 synthetic results already did not reject. Forty of those have intervals that remain unbounded in the log contrast because recovery information is weak. Their compatibility therefore provides little constraint.

An explicit example shows why the issue matters. Its biological balance is exactly the same in two contexts. Recovery alone makes the corrected observed balances look far apart, so an analysis assuming perfect control transfer rejects. Allowing the recovery mismatch that was built into the example makes the intervals compatible again.

The calculations use all 160 stored synthetic results from the public 0.5.0 package. They do not add experimental observations or new random samples. The useful next scientific step is independent evidence about how well recovery controls transfer, alongside a justified baseline and genuinely held-out biological observations.
