#!python3
#
# Proportional representation with approval and rated voting
#
# Plain approval voting
# Also rated
# Approval(BBox)
# Args: ballot-box object
# Returns: list of:
# - (Candidate, number of votes)
#
# Satisfaction approval voting
# Also rated
# https://en.wikipedia.org/wiki/Satisfaction_approval_voting
# Like plain approval voting, but divides the weight by the total of the votes
# SatAppvl(BBox)
# Args: ballot-box object
# Returns: what Approval() returns
#
# Proportional approval voting
# https://en.wikipedia.org/wiki/Proportional_approval_voting
# https://electowiki.org/wiki/Proportional_approval_voting
# PropAppvl(BBox, SatFunc, NSeats)
# Args: ballot-box object
# Returns: list of (NSeats) candidates which gave the most satisfaction
#
# Sequential proportional approval voting
# Reweighted approval voting
# Reweighted range voting
# https://en.wikipedia.org/wiki/Sequential_proportional_approval_voting
# https://electowiki.org/wiki/Sequential_proportional_approval_voting
# https://electowiki.org/wiki/Reweighted_range_voting
# Args: ballot-box object, weight function
# Returns: list of:
# - list of
# - - (Candidate, weighted number of votes)
#
# Eliminative proportional approval voting
# Eliminates candidates whose absence makes either the lowest or the highest satisfaction
# ElimPropAppvl(BBox, SatFunc, SortDir)
# Args: ballot-box object, satisfaction function, direction of sorting:
# True: worst to best, False: best to worst
# Returns: list of:
# - list of:
# - - (Candidate, total satisfaction (weighted sum) )
#
# Phragmen's algorithm
# https://en.wikipedia.org/wiki/Phragmen%27s_voting_rules
# https://electowiki.org/wiki/Phragmen%27s_voting_rules
# https://arxiv.org/abs/1611.08826 = Phragmén's and Thiele's election methods
#
# To implement:
# Method of Equal Shares
# https://en.wikipedia.org/wiki/Method_of_Equal_Shares
# https://electowiki.org/wiki/Method_of_Equal_Shares
#
# -
#
# Ballot-box format:
# (Candidates, Weights of ballots, Ballots)
# Ballots: indexed by (which ballot, candidate)
#
# Check it (returns boolean):
# IsBBox(BBox)
#
# Check on whether the votes are pure approval votes (0 or 1) (returns boolean):
# IsBBoxApproval(BBox)
#
#
# Highest-average weight parameters:
#
# Number i, factor f:
# weight(i,f) = 1/(1 + f*i)
#
# f = 0: Flat
# f = 1: D'Hondt
# f = 2: Sainte-Laguë
# f = None (infinity): Cliff
#
# for proportional-representation denominator (1/f) + i = (1 + f*i) / f
#
# Highest-average weight function:
# HighAvgWeight(i, f)
# Args: number, parameter
#
# Highest-average satisfaction function:
# HighAvgSatisfy(n, f)
# Args: number, parameter
#

from itertools import combinations
from functools import cache
from operator import itemgetter


TotalText = "(Total)"


# Check the ballot box
def IsBBox(BBox):
	if len(BBox) != 3: return False
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	NWts = len(Wts)
	if len(Votes) != NWts: return False
	for Vote in Votes:
		if len(Vote) != len(Cands): return False
	return True

# Are the ballots pure approval?
def IsBBoxApproval(BBox):
	if not IsBBox(BBox): return False
	Cands, Wts, Votes = BBox
	for Vote in Votes:
		for IndVote in Vote:
			if IndVote not in (0,1): return False
	return True


# Candidate-list ballots to standard format
def CandListsToBBox(BLists):
	# Get the candidates
	CSet = set()
	for BL in BLists:
		CSet |= set(BL[1])
	CList = list(CSet)
	CList.sort()
	
	CLIxs = {}
	for k, c in enumerate(CList):
		CLIxs[c] = k
	
	Wts = []
	Blts = []
	for Wt, CL in BLists:
		Vals = len(CList)*[0]
		for c in CL:
			Vals[CLIxs[c]] = 1
		Wts.append(Wt)
		Blts.append(tuple(Vals))
	
	return (tuple(CList), tuple(Wts), tuple(Blts))


# Highest-averages weighting
@cache
def HighAvgWeight(i, f):
	if f == None: return 1. if i == 0 else 0.
	else: return 1./(1. + f*i)

# Highest-averages satisfaction function
@cache
def HighAvgSatisfy(n, f):
	return sum(map(lambda i: HighAvgWeight(i, f), range(0,n+1)))


# Approval voting
def Approval(BBox):
	if not IsBBox(BBox) return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	
	Sums = NCands*[0]
	for wt, vts in zip(Wts,Votes):
		for ix, vt in enumerate(vts):
			Sums[ix] += wt*vt
	
	TotWts = sum(Wts)
	
	csms = list(zip(Cands,Sums))
	csms.sort(key=itemgetter(1), reverse=True)
	csms += [(TotalText,TotWts)]
	
	return tuple(csms)


# Satisfaction approval voting
def SatAppvl(BBox):
	if not IsBBox(BBox) return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	
	NewWts = []
	for wt, vts in zip(Wts,Votes):
		VoteSum = sum(vts)
		newwt = wt/VoteSum if VoteSum != 0 else 0
		NewWts.append(newwt)
	
	NewBBox = (Cands, tuple(NewWts), Votes)
	
	return Approval(NewBBox)


# Proportional approval voting
# Needs a ballot box, a satisfaction function,
# and the number of seats
def PropAppvl(BBox, SatFunc, NSeats):
	if not IsBBoxApproval(BBox): return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	if NSeats > NCands: return None
	
	BestIxs = None
	BestSumSat = None
	for ixs in combinations(list(range(NCands)), NSeats):
		SumSats = 0
		for wt, vts in zip(Wts,Votes):
			SumSats += wt*SatFunc(sum( (vts[ix] for ix in ixs) ))
		if BestIxs == None:
			BestIxs = ixs
			BestSumSats = SumSats
		elif SumSats > BestSumSats:
			BestIxs = ixs
			BestSumSats = SumSats
	
	return tuple( (Cands[ix] for ix in BestIxs) )


# Sequential proportional approval voting
# Needs a ballot box, a weight function,
# and the number of seats
def SeqPropAppvl(BBox, WtFunc):
	if not IsBBox(BBox) return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	
	Cands = list(Cands)
	Votes = tuple(map(list,Votes))
	NBallots = len(Wts)
	Victs = NBallots*[0]
	CandRes = []
	for ic in range(NCands):
		NCands = len(Cands)
		Sums = NCands*[0]
		TotWts = 0
		for wt, vc, vts in zip(Wts,Victs,Votes):
			adjwt = wt*WtFunc(vc)
			TotWts += adjwt
			for ix,vt in enumerate(vts):
				Sums[ix] += adjwt*vt
		
		# Sort by the score to find the winner
		# Include the index to find the winner's index
		csms = zip(Cands,Sums,range(NCands))
		csms = list(sorted(csms,key=itemgetter(1),reverse=True))
		(mxcand, mxvts, mxix) = csms[0]
		
		for k in range(NBallots):
			Victs[k] += Votes[k][mxix]
		
		# Append the candidates with their scores
		csms = [cm[0:2] for cm in csms] + [(TotalText,TotWts)]
		CandRes.append(tuple(csms))
		
		# Delete the winner
		del Cands[mxix]
		for vts in Votes:
			del vts[mxix]
	
	return tuple(CandRes)

# Eliminative proportional approval voting
# Needs a ballot box, a weight function,
# and the direction of sorting (reverse: True, normal: False)
def ElimPropAppvl(BBox, SatFunc, SortDir):
	if not IsBBoxApproval(BBox): return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	
	Cands = list(Cands)
	Votes = tuple(map(list,Votes))
	TotWts = sum(Wts)
	CandRes = []
	for ic in range(NCands):
		NCands = len(Cands)
		Sums = NCands*[0]
		for wt, vts in zip(Wts,Votes):
			for ix in range(NCands):
				Sums[ix] += wt*SatFunc(sum(vts[:ix]) + sum(vts[ix+1:]))
		
		# Sort by the score to find the loser
		# Include the index to find the loser's index
		csms = zip(Cands,Sums,range(NCands))
		csms = list(sorted(csms,key=itemgetter(1),reverse=SortDir))
		(mxcand, mxvts, mxix) = csms[0]
		
		# Append the candidates with their scores
		csms = [cm[0:2] for cm in csms] + [(TotalText,TotWts)]
		CandRes.append(tuple(csms))
		
		# Delete the winner
		del Cands[mxix]
		for vts in Votes:
			del vts[mxix]
	
	return tuple(CandRes)


def Phragmen(BBox):
	if not IsBBoxApproval(BBox): return None
	Cands, Wts, Votes = BBox
	NCands = len(Cands)
	
	# Precalculate voting-power denominator reciprocals
	vpdnm = NCands*[0]
	
	# Find the denominators
	for wt, vts in zip(Wts, Votes):
		for k in range(NCands):
			vpdnm[k] += wt*vts[k]
	
	# Take their reciprocals
	vdrcp = [1/float(x) for x in vpdnm]
	
	# The ballot loads (original Swedish: belastning)
	bloads = len(Wts)*[0]
	
	Cands = list(Cands)
	Votes = tuple(map(list,Votes))
	TotWts = sum(Wts)	
	CandRes = []
	for ic in range(NCands):
		# Find the voting powers
		NCands = len(Cands)
		vpnum = NCands*[1]
		
		for bl, wt, vts in zip(bloads, Wts, Votes):
			blwt = bl*wt
			for k in range(NCands):
				vpnum[k] += blwt*vts[k]
		
		vpwr = [rd*nm for nm, rd in zip(vpnum, vdrcp)]
		
		# Sort by the score to find the winner
		# Include the index to find the winner's index
		csms = zip(Cands,vpwr,range(NCands))
		csms = list(sorted(csms,key=itemgetter(1),reverse=False))
		(mncand, mnvp, mnix) = csms[0]
		
		# Update the ballot loads
		bloads = [ mnvp if vts[mnix] != 0 else bl \
			for vts, bl in zip(Votes, bloads)]
		
		# Append the candidates with their scores
		csms = [(cm[0],1./cm[1]) for cm in csms] + [(TotalText, TotWts)]
		CandRes.append(tuple(csms))
		
		# Delete the winner
		del Cands[mnix]
		del vdrcp[mnix]
		for vts in Votes:
			del vts[mnix]
	
	return tuple(CandRes)
	
#
# Examples
#

HAFactorList = (0, 1, 2, None)

HAFactorDesc = {0: "0 -- Flat", 1: "1 -- D'Hondt", 2: "2 - Sainte-Laguë",
	None: "Infinity -- Cliff"}

def printlist(res):
	for r in res: print(r)

def DumpAll(BBox, NSeats):
	print(f"Number of Seats: {NSeats}")
	print("Approval")
	print(Approval(BBox))
	print("Satisfaction Approval")
	print(SatAppvl(BBox))
	for fac in HAFactorList:
		print(HAFactorDesc[fac])
		print("Plain PAV")
		print(PropAppvl(BBox, lambda n: HighAvgSatisfy(n,fac), NSeats))
		print("Sequential PAV")
		printlist(SeqPropAppvl(BBox, lambda n: HighAvgWeight(n,fac)))
		print("Eliminative PAV - Rev")
		printlist(ElimPropAppvl(BBox, lambda n: HighAvgWeight(n,fac), True))
		print("Eliminative PAV - Norm")
		printlist(ElimPropAppvl(BBox, lambda n: HighAvgWeight(n,fac), False))
	print("Phragmen")
	printlist(Phragmen(BBox))
	print()

if __name__ == "__main__":
	
	# From Wikipedia, Electowiki on PAV
	print("Example: Wiki PAV")
	CLPAV = ((5, ("A","B")), (17,("A","C")), (8,("D",)))
	DumpAll(CandListsToBBox(CLPAV), 2)
	
	# From Wikipedia on SPAV
	print("Example: Wiki SPAV")
	CLSPAV = ((112, ("A","B","C")), (6, ("B","C")), (4,("A","B","C","X")),
		(73, ("X","Y","Z")), (4,("C","X","Y","Z")), (1,("X","Y")))
	DumpAll(CandListsToBBox(CLSPAV), 3)
		
	# From https://electionscience.org/voting-methods/getting-proportional-with-approval-voting/
	# Adapted from Brams, Kilgour, and Potthoff
	print("Example: BKP")
	CLBKP = ((2, ("A",)), (5, ("A","B")), (3,("A","C")), (2,("B","C")), (4,("D",)))
	DumpAll(CandListsToBBox(CLBKP), 3)
	
	# https://en.wikipedia.org/wiki/Satisfaction_approval_voting
	print("Example: Wiki SAV")
	CLSAV = ((4, ("A","B")), (3, ("C",)), (3, ("D",)))
	DumpAll(CandListsToBBox(CLSAV), 2)
		
	# https://en.wikipedia.org/wiki/Phragmen%27s_voting_rules
	print("Example: Wiki PRG")
	CLPRG = ((1034, ("A","B","C")), (519, ("P","Q","R")), (90, ("A","B","Q")),
		(47, ("A","P","Q")))
	DumpAll(CandListsToBBox(CLPRG), 3)
	
	# https://electowiki.org/wiki/Sequential_proportional_approval_voting
	# https://electowiki.org/wiki/Reweighted_range_voting
	print("Reweighted range voting")

	BBRRV = (("Red", "Green", "Yellow", "Blue"), 8*[1],
		((5,0,3,5), (5,0,0,4), (0,5,0,1), (1,2,4,3),
		(1,0,2,0), (1,3,0,1), (0,0,5,0), (5,0,0,4)))
	printlist(SeqPropAppvl(BBRRV, lambda n: HighAvgWeight(n,0.2)))
