#This script provide some functions to do the postprocess of the fitting sampling.
#
import os
import numpy as np
from scipy.interpolate import interp1d
ls_mic = 2.99792458e14 #unit: micron/s
Mpc = 3.08567758e24 #unit: cm
mJy = 1e26 #unit: erg/s/cm^2/Hz

def AddDict(targetDict, quantName, quant):
    """
    To add a quantity into the target dict.
    """
    if quantName in targetDict.keys():
        targetDict[quantName].append(quant)
    else:
        targetDict[quantName] = [quant]
    return None

def parStatistics(ppfunc, nSamples, ps, fargs=[], fkwargs={}):
    """
    Get the statistics of the model calculated parameters.

    Parameters
    ----------
    ppfunc : function
        The function to post process the model posterior sampling.
    nSamples : int
        The number of sampling when it calculate the parameter statistics.
    ps : array
        The posterior sampling.

    Returns
    -------
    pList : array
        The parameter list.

    Notes
    -----
    None.
    """
    pList = []
    for pars in ps[np.random.randint(len(ps), size=nSamples)]:
        pList.append(ppfunc(pars, *fargs, **fkwargs))
    pList = np.array(pList)
    return pList

def Luminosity_Integrate(flux, wave, DL, z, waveRange=[8.0, 1e3], frame="rest"):
    """
    Calculate the integrated luminosity of input SED with given wavelength range.

    Parameters
    ----------
    flux : float array
        The flux density used to integrate to the luminosity.
    wave : float array
        The wavelength of the SED.
    DL : float
        The luminosity distance of the source.
    z : float
        The redshift of the source.
    waveRange : float array
        The short and long end of the wavelength to integrate.
    frame : string
        The flux and wave should be consistently in the rest frame ("rest") or
        observing frame ("obs").

    Returns
    -------
    L : float
        The luminosity of the SED within the given wavelength range, unit: erg/s.

    Notes
    -----
    None.
    """
    nu = ls_mic / wave
    fltr = (wave > waveRange[0]) & (wave < waveRange[1])
    F = -1.0 * np.trapz(flux[fltr], nu[fltr]) / mJy #unit: erg/s/cm^2
    if frame == "rest":
        L = F * 4.0*np.pi * (DL * Mpc)**2.0 / (1 + z)**2
    elif frame == "obs":
        L = F * 4.0*np.pi * (DL * Mpc)**2.0
    else:
        raise ValueError("Cannot recognise the frame: {0}!".format(frame))
    return L

def Luminosity_Specific(flux, wave, wave0, DL, z, frame="rest"):
    """
    Calculate the specific luminosity at wave0 for the SED (wave, flux).

    Parameters
    ----------
    flux : float array
        The flux density of the SED.
    wave : float array
        The wavelength of the SED.
    wave0 : float (array)
        The wavelength(s) to be caculated.
    DL : float
        The luminosity distance.
    z : float
        The redshift.

    Returns
    -------
    Lnu : float (array)
        The specific luminosity (array) at wave0 that is (are) required, unit: erg/s/Hz.

    Notes
    -----
    None.
    """
    S0 = interp1d(wave, flux)(wave0)
    if frame == "rest":
        Lnu = S0 * 4.0*np.pi * (DL * Mpc)**2.0 / (1 + z)**2 / mJy #unit: erg/s/Hz
    elif frame == "obs":
        Lnu = S0 * 4.0*np.pi * (DL * Mpc)**2.0 / (1 + z) / mJy #unit: erg/s/Hz
    return Lnu

def L_Total(pars, sedModel, DL, z):
    """
    Calculate the total luminosity.
    """
    sedModel.updateParList(pars)
    wave = sedModel.get_xList()
    flux = sedModel.combineResult()
    L = Luminosity_Integrate(flux, wave, DL, z, waveRange=[8.0, 1e3], frame="rest")
    return L

def randomSampler(parRange, parType="D"):
    """
    This function randomly sample the given parameter space.
    """
    if parType == "D": #For discrete parameters
        p = np.random.choice(parRange)
    elif parType == "C": #For continuous parameters
        r1, r2 = parRange
        p = (r2 - r1) * np.random.rand() + r1
    else:
        raise ValueError("The parameter type '{0}' is not recognised!".format(parType))
    return p
