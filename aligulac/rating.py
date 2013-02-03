'''
This is where the rating magic happens. Imported by period.py.
'''

from numpy import *
from scipy.stats import norm
import scipy.optimize as opt

MIN_DEV = 0.05
INIT_DEV = 0.6

def ceilit(arr):
    """Prevents RDs from going above INIT_DEV."""
    for i in range(0,len(arr)):
        arr[i] = min(arr[i], INIT_DEV)

def check_max(func, x, i, name, disp):
    """Auxiliary function to perform numerical optimization. Will check the return flags and return the
    argmin, or None if an error occured."""
    try:
        ret = func(x)
        if ret[i] == 0:
            return ret[0]
        print 'OPT.' + name + ': did not converge'
    except:
        print 'OPT.' + name + ': error'
    return None

def maximize(L, DL, D2L, x, method=None, disp=False):
    """Main function to perform numerical optimization. L, DL and D2L are the objective function and its
    derivative and Hessian, and x is the initial guess (current rating).
    
    It will attempt the maximization using four different methods, from fastest and least robust, to slowest
    and most robust. It returns the argmin, or None if an error occured."""
    mL = lambda x: -L(x)
    mDL = lambda x: -DL(x)
    mD2L = lambda x: -D2L(x)

    # Newton Conjugate Gradient
    if method == None or method == 'ncg':
        func = lambda x0: opt.fmin_ncg(mL, x0, fprime=mDL, fhess=mD2L, disp=disp, full_output=True, avextol=1e-10)
        xm = check_max(func, x, 5, 'NCG', disp)
        if xm != None:
            return xm

    # Broyden-Fletcher-Goldfarb-Shanno
    if method == None or method == 'bfgs':
        func = lambda x0: opt.fmin_bfgs(mL, x0, fprime=mDL, disp=disp, full_output=True, gtol=1e-10)
        xm = check_max(func, x, 6, 'BFGS', disp)
        if xm != None:
            return xm

    # Powell
    if method == None or method == 'powell':
        func = lambda x0: opt.fmin_powell(mL, x0, disp=disp, full_output=True, ftol=1e-10)
        xm = check_max(func, x, 5, 'POWELL', disp)
        if xm != None:
            return xm

    # Downhill simplex (last resort)
    func = lambda x0: opt.fmin(mL, x0, disp=disp, full_output=True, ftol=1e-10)
    xm = check_max(func, x, 4, 'DOWNHILL_SIMPLEX', disp)
    return xm

def fix_ww(myr, mys, oppr, opps, oppc, W, L):
    """This function adds fake games to the oppr, opps, oppc, W and L arrays if the player has 0-N or N-0
    records against any category."""
    played_cats = sorted(unique(oppc))
    wins = zeros(len(played_cats))
    losses = zeros(len(played_cats))
    M = len(W)

    # Count wins and losses against each category
    for j in range(0,M):
        wins[played_cats.index(oppc[j])] += W[j]
        losses[played_cats.index(oppc[j])] += L[j]

    # Find the categories where the record is 0-N or N-0 with N>0
    pi = nonzero(wins*losses == 0)[0]

    # Add fake games for each of the relevant categories
    for c in pi:
        W = append(W, 1)
        L = append(L, 1)
        oppr = append(oppr, myr[1+played_cats[c]])
        opps = append(opps, mys[1+played_cats[c]])
        oppc = append(oppc, played_cats[c])

    # Return the new arrays
    return (oppr, opps, oppc, W, L)

def update(myr, mys, oppr, opps, oppc, W, L, text='', pr=False, Ncats=3):
    """This function updates the rating of a player according to the ratings of the opponents and the games
    against them."""

    # If no games were played, do nothing.
    if len(W) == 0:
        return(myr, mys, [None] * (Ncats+1), [None] * (Ncats+1))

    # Add fake games to prevent infinities
    (oppr, opps, oppc, W, L) = fix_ww(myr, mys, oppr, opps, oppc, W, L)

    if pr:
        print text
        print oppr
        print opps
        print oppc
        print W
        print L

    played_cats = sorted(unique(oppc))          # The categories against which the player played
    tot = sum(myr[array(played_cats)+1])        # The sum relative rating against those categories
                                                # (will be kept constant)
    M = len(W)                                  # Number of opponents
    C = len(played_cats)                        # Number of different categories played

    # Convert global categories to local
    def loc(x):
        return array([played_cats.index(c) for c in x])

    # Convert local categories to global
    def glob(x):
        return array([played_cats[c] for c in x])

    # Extends a M-vector to an M+1-vector according to the restriction given
    # (that the sum of relative ratings against the played categories is constant)
    def extend(x):
        return hstack((x, tot-sum(x[1:])))

    # Prepare some vectors and other numbers that are needed to form objective functions, derivatives and
    # Hessians
    DM = zeros((M,C))
    DMex = zeros((M,C+1))
    DM[:,0] = 1
    DMex[:,0] = 1
    for j in range(0,M):
        lc = loc([oppc[j]])[0]
        if lc < C-1:
            DM[j,lc+1] = 1
        else:
            DM[j,1:] = -1
        DMex[j,lc+1] = 1

    mbar = oppr
    sbar = sqrt(opps**2 + 1)
    gen_phi = lambda j, x: norm.pdf(x, loc=mbar[j], scale=sbar[j])
    gen_Phi = lambda j, x: norm.cdf(x, loc=mbar[j], scale=sbar[j])

    # Objective function
    def logL(x):
        Mv = x[0] + extend(x)[loc(oppc)+1]
        Phi = array([gen_Phi(i,Mv[i]) for i in range(0,M)])
        return sum(W*log(Phi) + L*log(1-Phi))

    # Derivative
    def DlogL(x):
        Mv = x[0] + extend(x)[loc(oppc)+1]
        phi = array([gen_phi(i,Mv[i]) for i in range(0,M)])
        Phi = array([gen_Phi(i,Mv[i]) for i in range(0,M)])
        vec = (W/Phi - L/(1-Phi)) * phi
        return array(vec * matrix(DM))[0]

    # Hessian
    def D2logL(x, DM, C):
        Mv = x[0] + extend(x)[loc(oppc)+1]
        phi = array([gen_phi(i,Mv[i]) for i in range(0,M)])
        Phi = array([gen_Phi(i,Mv[i]) for i in range(0,M)])
        alpha = phi/Phi
        beta = phi/(1-Phi)
        Mvbar = (Mv-mbar)/sbar**2
        coeff = - W*alpha*(alpha+Mvbar) - L*beta*(beta-Mvbar)
        ret = zeros((C,C))
        for j in range(0,M):
            ret += coeff[j] * outer(DM[j,:], DM[j,:])
        return ret

    # Prepare initial guess in unrestricted format and maximize
    x = hstack((myr[0], myr[played_cats]))[0:-1]
    x = maximize(logL, DlogL, lambda x: D2logL(x,DM,C), x)

    # If maximization failed, return the current rating and print an error message
    if x == None:
        print 'Failed to converge for %s' % text
        return (myr, mys, [None]*(Ncats+1), [None]*(Ncats+1))

    # Extend to restricted format
    devs = maximum(-1/diag(D2logL(x, DMex, C+1)), MIN_DEV)
    rats = extend(x)

    # Compute new RD and rating for the indices that can change
    news = zeros(len(myr))
    newr = zeros(len(myr))

    ind = [0] + [f+1 for f in played_cats]
    news[ind] = 1./sqrt(1./devs**2 + 1./mys[ind]**2)
    newr[ind] = (rats/devs**2 + myr[ind]/mys[ind]**2) * news[ind]**2

    # Enforce the restriction of sum relative rating against played categories should be constant
    ind = ind[1:]
    m = (sum(newr[ind]) - tot)/len(ind)
    newr[ind] -= m
    newr[0] += m

    # Ratings against non-played categories should be kept as before.
    ind = setdiff1d(range(0,len(myr)), [0] + ind)
    news[ind] = mys[ind]
    newr[ind] = myr[ind]

    # Keep new RDs between MIN_DEV and INIT_DEV
    news = (abs(news-MIN_DEV)+news-MIN_DEV)/2 + MIN_DEV
    ceilit(news)

    # Ensure that mean relative rating is zero
    m = mean(newr[1:])
    newr[1:] -= m
    newr[0] += m

    # Extend the performance ratings to global indices
    devsex = [None] * (Ncats + 1)
    ratsex = [None] * (Ncats + 1)
    devsex[0] = devs[0]
    ratsex[0] = rats[0]
    for c in played_cats:
        devsex[c+1] = devs[played_cats.index(c)+1]
        ratsex[c+1] = rats[played_cats.index(c)+1]
    
    return (newr, news, ratsex, devsex)
