Minimal covering sets:

Let X denote elements to cover and let F denote a finite set of
subsets of X. We say that F covers X if the following property holds:

    X = \union{S \in F} S

For example, let us consider X={1,..,12} and F={S1,...,S6} as follows:

S1 = {1,2,3,4,5,6}
S2 = {5,6,8,9}
S3 = {1,4,7,10}
S4 = {2,5,7,8,11}
S5 = {3,6,9,10,12}
S6 = {10,11}

The set C1={S1,S4,S3,S6} is a set cover, but not minimal as
C2={S3,S4,S5} also covers X and is smaller compared to C1. In our
context, X denotes the set of statements to cover and F denotes the
list of seed files (tests), each one covering a set of statements in
X. Approximation greedy algorithm for computing minimal covering sets
exists. We base our implementation on the one from the paper
"Optimizing Seed Selection for Fuzzing, Rebert et al., USENIX 2014":

greedy-weighted-set-cover(X, F)
 U = X
 C = empty
 while U not empty
   S = max{S \in F} |S \inter U|/w(S)
   C = C \union S
   U = U \ S
 return C

Let us see how this algo works on the example above, for the
unweighted case, when w(S)=1.

Start of Iteration #                   U                         C
                   1     {1,2,3,4,5,6,7,8,9,10,11,12}          empty
                   2                 {7,8,9,10,11,12}           {S1}
                   3                        {9,10,12}        {S1,S4}
                   4                            empty     {S1,S4,S5}

The peach-minset(P, F) is another popular routing to minimize the set
of seeds. The excerpt below was taken from the same USENIX paper, but
we removed the statement that sort coverage as indicated in the paper
and fixed line 9 replacing cov[i] by S[i].

peach-min-set(P, F)
 C = empty
 i = 1
 for S in F
   cov[i] = MeasureCoverage(S)
   i = i + 1
 for i = 1 to |F|
   if cov[i]\C != \empty
     C = C U S[i]   
 return C

Let us see how this algo works on the example above.

Start of Iteration of 2n loop #                C
                              1              empty
                              2               {S1}
                              3            {S1,S2}
                              4         {S1,S2,S3}
                              5      {S1,S2,S3,S4}
                              6   {S1,S2,S3,S4,S5}

Note this minimization algorithm does not compute a miminal cover, but
an obvious improvement is to sort the set of |F| by the
cardinality. Here is the impact of this change:

S1 = {1,2,3,4,5,6}
S5 = {3,6,9,10,12}
S4 = {2,5,7,8,11}
S2 = {5,6,8,9}
S3 = {1,4,7,10}
S6 = {10,11}


Start of Iteration of 2n loop #                C
                              1              empty
                              2               {S1}
                              3            {S1,S5}
                              4         {S1,S5,S4}
