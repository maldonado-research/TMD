# What one additional missed genotype does to inferred order

For the 1,118 sites with two observed genotypes across four *Shorea* trees, the smallest number of changed tip calls that makes a single stable change per site compatible with every physical tree is **seven**. At that minimum, each site has one compatible edge and 75,230 specific within-tree site pairs have a forced ancestral order. Allowing **one further missed tip call anywhere among all 1,118 sites** reduces the number of individually guaranteed orders to **59,736**. Each complete eight-miss reconstruction nevertheless contains between **75,226 and 75,440** ordered pairs. Most of the uncertainty here concerns the identities of the pairs whose order the data establish. [Study and sampling design](https://doi.org/10.7554/eLife.88456) · [Native supplementary workbook](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx)

## Counting changes

At each site, call a tip positive if its genotype differs from that tree’s observed basal cambium genotype. Suppose one stable change occurred on the rooted physical tree and every sampled descendant of that edge inherited the changed state. Each observed positive is treated as reliable. We allow some tips recorded as basal-like to be missed positives. One miss refers to one site and one tip. Neither the basal sample’s ancestral state nor complete transmission through mixed plant tissues was independently observed. These calculations describe possible reconciliations of the recorded calls under the specified model. The source does not measure seven genotyping errors.

The workbook has eight sample columns per individual. A four-point split test on the measured distances in sheet b independently recovers 13 edges of positive length for each tree. Adding the edge lengths along the path between every sample pair reproduces all 112 physical distances in integer centimetres. Thus the sampled metrics have resolved topologies at their stated precision. The basal sample orients those edges. Only strict nesting along one root-to-tip path forces precedence. Distances in metres supply no common calendar for ordering different paths. Events assigned to one edge can occur in either order.

All 28 genotype-disagreement counts for each block of sheet k match the corresponding genetic distances in sheet b under the species-matched reassignment of the printed F/S prefixes. Sheet f independently gives each matching block size. Unit-cost unordered-state parsimony on this physical tree yields 1,111 single-step and 25 two-step patterns across all 1,136 sites. The latter include all 18 sites with three recorded genotypes and seven sites with two. The authors mention possible genotyping errors among homozygous SNV calls. Each step here changes a categorical diploid state. It has no independently established mechanism. [Methods](https://elifesciences.org/articles/88456)

## A sharp whole-panel budget

Let $P_i$ be the observed positive tips at site $i$, and let $D_e$ be the tips below edge $e$. Edge $e$ is possible if $P_i$ is a subset of $D_e$. Its cost $c_i(e)$ counts the tips in $D_e$ outside $P_i$. Write $m_i$ for the minimum possible cost at that site. All site costs add over the panel. In these data the sum of their minima is $M=7$. Five costs occur in S1 and two in F2. All 1,118 sites have a unique minimum-cost edge on their respective trees. A shared allowance of $r$ extra misses covers each placement whose total cost is at most $M+r$.

For *distinct* sites $i$ and $j$, fixing their two edges to $e$ and $f$ is feasible precisely when

$$
c_i(e)-m_i+c_j(f)-m_j \le r.
$$

Every other site must incur at least its minimum cost. Assigning each its minimum-cost edge attains this bound, since separate sites have separate call decisions. This proves both necessity and sufficiency. We enumerate every feasible edge pair. Strict precedence is guaranteed when every such pair nests in the same direction. Equal call patterns are counted according to the actual number of distinct loci carrying the pattern. All comparisons are within one tree. The miss allowance spans the four trees jointly.

| Individual | Two-state sites | Within-tree pairs | Minimum misses | Forced orders, seven total | Forced orders, ≤8 total | Forced orders, ≤9 total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F1 | 105 | 5,460 | 0 | 2,899 | 2,658 | 2,384 |
| F2 | 68 | 2,278 | 2 | 608 | 569 | 531 |
| S1 | 711 | 252,405 | 5 | 59,209 | 45,441 | 34,500 |
| S2 | 234 | 27,261 | 0 | 12,514 | 11,068 | 10,444 |
| **Total** | **1,118** | **287,404** | **7** | **75,230** | **59,736** | **47,859** |

S1 supplies 252,405 of the 287,404 pairs. Reusing a site in comparisons with hundreds of other sites induces dependence. The table gives exact counts for the observed roster. It makes no sampling-independence claim.

With a total allowance of eight, there are 623 complete assignments: the unique minimum and 622 alternatives that move a single site to a more inclusive edge at one extra call. The alternative procedure in the verifier counts how moving each site changes its relations to every other site in the same tree. It yields the 75,226–75,440 range for the 622 alternatives. The 15,494 pairs that lose their guarantee from seven to eight form a union over these alternatives. A single alternative need not remove all 15,494 orders.

Under a separate rule permitting one miss **per site**, the fixed-direction pair count also equals 59,736 for these data. The feasible whole-panel assignments differ. With two misses per site the count is 47,881, whereas allowing two extra misses jointly above the seven required gives 47,859. A whole-panel budget can concentrate multiple misses on one previously discordant site. The per-site cap applies to the total at each site.

With every call taken literally, seven sites have no compatible stable-change placement. Restricting to pairs whose two sites each fit that exact-call model gives 72,219 strict orders. The whole panel admits no globally perfect assignment in that case. The seven-miss minimum allows those previously incompatible sites to enter the common reconstruction.

## Reproduction

The Python 3.11+ standard-library verifier reads the native XLSX directly, authenticates its SHA-256 digest, reconstructs the physical and genetic matrices, checks the source block mapping, and calculates the parsimony, pair and panel-budget results. From this directory run the following command. The input hash is `a5916e95facc077a137ce03627b2a94ef7ecf3cc9a148223587bdb719d2a06af`. [Workbook](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx)

```sh
python3 -B verify_satake_workbook.py elife-88456-supp1-v1.xlsx | diff - aggregate.json
```
