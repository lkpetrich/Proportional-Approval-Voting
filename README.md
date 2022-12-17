# Proportional-Approval-Voting
Implements proportional representation with approval and rated/range/score voting.
Several algorithms implemented.

- PropAppvl.py - in Python. Contains instructions on how to use it.
- Proportional Approval Voting.nb - in Mathematica.

Some of the algorithms also work on rated votes, and some only on approval votes (0 ot 1).

Single-round algorithms:

- Approval (also rated): the plain-vanilla method. It is not proportional.
- Proportional approval voting: finds the slate of candidates with the most total satisfaction.

Multi-round algorithms, removing a winner (or loser) before their next round.

- Satisfaction Approval (also rated): for each round, makes each voter's ratings add up to 1 if any nonzero ratings.
- Sequential Proportional Approval Voting (Reweighted Approval Voting; also rated): for each round, downweights each ballot by how many winners it has elected.
- Eliminative Proportional Approval Voting: for each round, eliminates the candidate with the most or least total satisfaction.
- Phragmen's algorithm
