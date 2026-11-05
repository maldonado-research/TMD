# Native route controls and the eligibility denominator

The inspected native sources show that a wrinkly-spreader (WS) phenotype does not establish membership in Wsp/Aws/Mws. They do not supply an independent known-Other control denominator for a numerical false-entry bound.

[Lind et al. (2019), Results section s2-4](https://pmc.ncbi.nlm.nih.gov/articles/PMC6324874/#s2-4) reports 109 sampled WS mutants: 46 Wsp, 41 Aws, 18 Mws, and four in the previously described rare pathways PFLU0085 and PFLU0183. The last four are genuine non-focal biological examples in that reported collection. Methods s4-2 selects one colony with WS morphology per independent culture, with experiments conducted in different genetic backgrounds, including pathway double deletions. Methods s4-3 describes candidate-gene Sanger sequencing and genome sequencing for a few unresolved candidates. Thus 4/109 is a fraction among sampled, recovered WS mutants. It is not the probability that a known-Other unit passes the gate. There is no denominator containing all known-Other units before phenotype selection, including those failing the gate, and no independent evaluation of a frozen eligibility rule. The complementary 105/109 is likewise descriptive of this selected collection; it is not a transported predictive value for a target cohort.

[McDonald et al. (2009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2778958/), section “SWS: a wsp-, aws-, and mws-independent route to WS,” identifies one selected SWS strain (PBR715) derived from the triple-deletion parent PBR716. This supplies a direct biological counterexample to treating WS morphology as proof of focal-route membership. The reported 41 suppressor mutants arise from mechanistic analysis of that selected strain; they do not constitute 41 independent known-Other eligibility trials. Deleting swsR reverted its phenotype, but repeated sequencing did not identify a causal mutation. This evidence therefore also needs its own exact truth definition before any use as a control.

WSX is a different case. McDonald's [Table 1 footnote b](https://pmc.ncbi.nlm.nih.gov/articles/PMC2778958/#tblfn2) reports 17 wsp suppressor insertions and unsuccessful identification of the causal sequence mutation. The Discussion identifies functional Wsp dependence. Unknown molecular assignment must not be converted into known-Other truth, and 17 suppressor insertions must not be converted into a negative-control denominator.

The replay is limited to these cached sources. It makes no literature-wide absence claim, transfers no numerical calibration, and leaves native beta unset. A useful control collection would independently establish Other truth before applying the same frozen gate, retain every eligible control unit and its terminal outcome, and justify the replication unit and target-context match.

`verify_native_controls.py` checks source hashes and selected source statements, extracts the Lind counts, and writes the original evidence ledger without source-body redistribution. It uses only the Python standard library and makes no network calls. The cached markdown is a provider representation, not authenticated original publisher bytes. Third-party rights remain unchanged.

```sh
python -B verify_native_controls.py \
  --mcdonald-markdown /path/to/S03.md \
  --lind-jats /path/to/lind2019_pmc.xml \
  --output /tmp/NATIVE_CONTROL_EVIDENCE.json
```
