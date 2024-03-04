"""
The paper says: For each language pair in JWSign we provide a
fixed, reproducible split into training, development
and test data, tailored towards machine translation
as the main use case.

It seems that those were lost, and must be recreated. -Colin

Colin: The Paper also says there's a splitting procedure. 
"Splitting procedure Our method for splitting
the data into training, development and test
sets is designed to eliminate multilingual “cross-
contamination” (the same sentence in two different
languages appearing both in the train and test set)
as much as possible. Multi-way parallel corpora
such as the IWSLT 2017 multilingual task data
(Cettolo et al., 2017) (where cross-contamination
does exist) are known to paint an overly optimistic
picture about the translation quality that can realis-
tically be obtained. A second goal is to maintain a
reasonable test set size for machine translation.
We select development and test data based on
an analysis of cross-lingual frequency (Figure 4).
We minimize the chances of a sample in the test
set in one sign language being found in the train
set in another language, which could lead to cross-
contamination when training a multilingual model
and possibly inflate the test set evaluation scores.
More details on the splitting procedure are given in
Appendix C."



"""

if __name__ == "__main__":

    # TODO: Adapt 