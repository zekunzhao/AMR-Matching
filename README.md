# This repo is for amr matching between two ARM graph based on n-gram matching.


The base code is from SemBleu: A Robust Metric for AMR Parsing Evaluation

The repository corresponds to our ACL 2019 paper entitled "SemBleu: A Robust Metric for AMR Parsing Evaluation".
* *SemBleu* is fast, taking less than a second to evaluate a thousand AMR pairs.
* *SemBleu* is accuracy without any search errors.
* *SemBleu* considers high-order correspondences. From our experiments, it is mostly consistent with *Smatch*, but *SemBleu* can better capture performance variations.

## Usage

```
chmod a+x eval.sh
./eval.sh output-file-path reference-file-path
```

Same as Smatch, AMRs in each file are separated by one empty line, such as:

```
(a / ask-01 :ARG0 (b / boy) :ARG1 (q / question))

(a / answer-01 :ARG0 (g / girl) :ARG1 (q / question))

```




