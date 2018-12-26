import pyjags
from math import ceil

def mean(X):
	return float(sum(X)) / len(X)

def median(X):
	X = sorted(X)
	if len(X) % 2 == 1:
		return X[((len(X)+1)/2)-1]
	else:
		return float(sum(X[(len(X)/2)-1:(len(X)/2)+1]))/2.0

def sd(X):
	ave = mean(X)
	total = sum([abs(x - ave) for x in X])
	sd = float(total) / len(X)
	return sd

def mad0(X):
	med = median(X)
	total = sum([abs(x - med) for x in X])
	mad = float(total) / len(X)
	if mad == 0:
		return sd(X)
	else:
		return mad

def bayesPairedTTest(X,Y):
	samples = pyJagsPairedTTest(X,Y)
	stats = mcmcStats(samples)
	return 1 - max(stats['mu_diff']['%>comp'],stats['mu_diff']['%<comp'])

def pyJagsPairedTTest(X,Y,compMu=0, nAdapt=500, nChains=3, nUpdate=100, nIter=5000,thin=1):
	pairDiff = [x-y for x,y in zip(X,Y)]
	pairMAD = mad0(pairDiff)
	dataList = {
				    'pair_diff' : pairDiff,
				    'mean_mu' : mean(pairDiff) ,
				    'precision_mu' : 1 / (pairMAD**2 * 1000000),
				    'sigma_low' : pairMAD / 1000 ,
				    'sigma_high' : pairMAD * 1000 ,
				    'comp_mu' : compMu
				}
	initList = {
				'mu_diff':mean(pairDiff),
				'sigma_diff':pairMAD,
				'nuMinusOne':4,
				}
	params = ["mu_diff", "sigma_diff", "nu", "eff_size", "diff_pred"]

	paired_samples_t_model_string = """
									 model {
											  for(i in 1:length(pair_diff)) {
											    pair_diff[i] ~ dt( mu_diff , tau_diff , nu )
											  }
											  diff_pred ~ dt( mu_diff , tau_diff , nu )
											  eff_size <- (mu_diff - comp_mu) / sigma_diff
											  
											  mu_diff ~ dnorm( mean_mu , precision_mu )
											  tau_diff <- 1/pow( sigma_diff , 2 )
											  sigma_diff ~ dunif( sigma_low , sigma_high )
											  # A trick to get an exponentially distributed prior on nu that starts at 1.
											  nu <- nuMinusOne + 1 
											  nuMinusOne ~ dexp(1/29)
											}
									"""
	jagsModel = pyjags.Model(paired_samples_t_model_string,data=dataList,chains=nChains,init=initList,adapt=nAdapt)
	jagsModel.update(nUpdate)
	sampled = jagsModel.sample(nIter,vars=params,thin=thin)
	return(sampled)


def mcmcStats(samples,credMass=0.95,comp=0):
	out = {}
	for key,sample in samples.items():
		out[key] = oneStat(sample.flatten(),credMass=credMass,comp=comp)
	return(out)

def binarySearchInd(val,l,lowI,topI):

	i = (lowI + topI) / 2
	low,high = l[max(0,i-1)], l[i]


	if low <= val and high >= val:
		return i
	elif lowI == topI:
		return i
	elif val < low:
		if i == topI:
			i -= 1
		return binarySearchInd(val,l,lowI,i)
	elif val > high:
		if i == lowI:
			i += 1
		return binarySearchInd(val,l,i,topI)
	else:
		print('PANIC')


def sampleHDI(sample,comp=0,credMass=0.95,equalRange=0.1):
	sample = sorted(sample)
	hdiLen = int(ceil( credMass * len(sample)))
	hdiVec = sample[:hdiLen]
	hdiInt = (hdiVec[0],hdiVec[-1])
	for i in range(1,len(sample) - hdiLen + 1):
		thisVec = sample[i:hdiLen+i]
		thisInt = (thisVec[0],thisVec[-1])
		if thisInt[1] - thisInt[0] < hdiInt[1] - hdiInt[0]:
			hdiInt = thisInt
			hdiVec = thisVec	

	compI = binarySearchInd(comp,sample,0,len(sample)-1)
	
	aboveCompI = len(sample) 
	for ind in range(compI,len(sample)):
		if sample[ind] - equalRange > comp:
			aboveCompI = ind
			break

	belowCompI = -1
	for ind in range(compI,-1,-1):
		if sample[ind] + equalRange < comp:
			belowCompI = ind
			break

	aboveComp = float(len(sample) - aboveCompI) / len(sample)
	belowComp = float(belowCompI + 1) / len(sample)

	return hdiInt,aboveComp,belowComp
	



def oneStat(samples,credMass=0.95,comp=0):
	hdiInt,aboveComp,belowComp = sampleHDI(samples,credMass=credMass,comp=comp)
	stats = {
				'mean' 	: mean(samples),
				'sd' 	: sd(samples),
				'HDI%' 	: credMass*100,
				'comp'	: comp,
				'HDIlo'	: hdiInt[0],
				'HDIup'	: hdiInt[1],
				'%>comp': aboveComp,
				'%<comp': belowComp,
				'median':median(samples)
			}
	return(stats)



if __name__ == '__main__':
	bpval = bayesPairedTTest([1.0012,2.3789548,3.53425,4.856,5.456,6.12,7.345,8.23],[2.3789548,3.53425,4.856,5.456,6.12,7.345,8.23,9.2123])
	print(bpval)
