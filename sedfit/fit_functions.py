import numpy as np
from scipy.special import erf
import george
from george import kernels
sqrt2 = np.sqrt(2)
PI2 = 2. * np.pi

#-->There are three ways to define the chi-square function to consider the
#upperlimits. The ChiSq functions are defined as (-2)*lnLikelihood.
#->The ChiSq_erf is preferred since it smoothly change the chis quare and recently
#many works use it.
def ChiSq_erf(data, model, unct=None, flag=None):
    '''
    This function calculate the Chi square of the observed data and
    the model. The upper limits are properly deal with using the method
    mentioned by Sawicki (2012).

    Parameters
    ----------
    data : float array
        The observed data.
    model : float array
        The model.
    unct : float array
        The uncertainties.

    Returns
    -------
    chsq : float
        The Chi square

    Notes
    -----
    None.
    '''
    if unct is None:
        unct = np.ones_like(data)
    if flag is None:
        flag = np.zeros_like(data)
    fltr_dtc = flag == 0
    fltr_non = flag == 1
    if np.sum(fltr_dtc)>0:
        wrsd_dtc = (data[fltr_dtc] - model[fltr_dtc])/unct[fltr_dtc] #The weighted residual
        chsq_dtc = np.sum(wrsd_dtc**2) + np.sum( np.log(PI2 * unct[fltr_dtc]**2) )
    else:
        chsq_dtc = 0.
    if np.sum(fltr_non)>0:
        wrsd_non = (data[fltr_non] - model[fltr_non])/(unct[fltr_non] * sqrt2)
        chsq_non = -2.* np.sum( np.log( 0.5 * (1 + erf(wrsd_non)) ) )
    else:
        chsq_non = 0.
    chsq = chsq_dtc + chsq_non
    return chsq

def ChiSq_hg(data, model, unct=None, flag=None):
    '''
    This is a generalized chi-square function that allows y to be upperlimits.
    It contributes zero to the chi square that the model is below the upperlimits,
    while it contributes as the normal detected points whtn the model is above
    the upperlimits.

    Parameters
    ----------
    data : float array
        The observed data and upperlimits.
    model : float array
        The model.
    unct : float array or Nobe by default
        The uncertainties.
    flag : float array or None by default
        The flag of upperlimits, 0 for detection and 1 for upperlimits.

    Returns
    -------
    chsq : float
        The Chi square

    Notes
    -----
    This chi-square form consider the x and y asymmetrically except for some special
    situations.
    '''
    if unct is None:
        unct = np.ones_like(data)
    if flag is None:
        flag = np.zeros_like(data)
    fltr_dtc = flag == 0
    fltr_non = flag == 1
    if np.sum(fltr_dtc)>0:
        wrsd_dtc = (data[fltr_dtc] - model[fltr_dtc])/unct[fltr_dtc] #The weighted residual
        chsq_dtc = np.sum(wrsd_dtc**2) + np.sum( np.log(PI2 * unct[fltr_dtc]**2) )
    else:
        chsq_dtc = 0.
    if np.sum(fltr_non)>0:
        data_non  = data[fltr_non]
        model_non = model[fltr_non]
        unct_non  = unct[fltr_non]
        wrsd_non  = np.zeros_like(data_non)
        #Only the when the model is above the upperlimit, it contributes to the chi square.
        fltr =  model_non > data_non
        wrsd_non[fltr] = (model_non[fltr] - data_non[fltr]) / unct_non[fltr]
        chsq_non = np.sum(wrsd_non**2.) + np.sum( np.log(PI2 * unct_non[fltr]**2.) )
    else:
        chsq_non = 0.
    chsq = chsq_dtc + chsq_non
    return chsq

def ChiSq_af(data, model, unct=None, flag=None):
    '''
    This is a generalized chi-square function that allows y to be upperlimits.
    It consider the upperlimits with the method by the AGN fitter (Calistro Rivera et al. 2016).

    Parameters
    ----------
    data : float array
        The observed data and upperlimits.
    model : float array
        The model.
    unct : float array or Nobe by default
        The uncertainties.
    flag : float array or None by default
        The flag of upperlimits, 0 for detection and 1 for upperlimits.

    Returns
    -------
    chsq : float
        The Chi square

    Notes
    -----
    This chi-square form consider the x and y asymmetrically except for some special
    situations.
    '''
    if unct is None:
        unct = np.ones_like(data)
    if flag is None:
        flag = np.zeros_like(data)
    fltr_dtc = flag == 0
    fltr_non = flag == 1
    if np.sum(fltr_dtc)>0:
        wrsd_dtc = (data[fltr_dtc] - model[fltr_dtc])/unct[fltr_dtc] #The weighted residual
        chsq_dtc = np.sum(wrsd_dtc**2) + np.sum( np.log(PI2 * unct[fltr_dtc]**2) )
    else:
        chsq_dtc = 0.
    if np.sum(fltr_non)>0:
        data_non  = 0.5 * data[fltr_non]
        model_non = model[fltr_non]
        unct_non  = 0.5 * data[fltr_non]
        #Only the when the model is above the upperlimit, it contributes to the chi square.
        wrsd_non = (model_non - data_non) / unct_non
        chsq_non = np.sum(wrsd_non**2.) + np.sum( np.log(PI2 * unct_non**2.) )
    else:
        chsq_non = 0.
    chsq = chsq_dtc + chsq_non
    return chsq

ChiSq = ChiSq_erf
#Model to data function#
def Model2Data(sedModel, sedData):
    """
    Convert the continual model to the data-like model to directly
    compare with the data.

    Parameters
    ----------
    sedModel : ModelCombiner object
        The combined model.
    sedData : SEDClass object
        The data set of SED.

    Returns
    -------
    fluxModel : list
        The model flux list of the data.

    Notes
    -----
    None.
    """
    waveModel = sedModel.get_xList()
    fluxModel = sedModel.combineResult()
    fluxModelPht = sedData.model_pht(waveModel, fluxModel)
    fluxModelSpc = sedData.model_spc(sedModel.combineResult)
    fluxModel = fluxModelPht + fluxModelSpc
    return fluxModel

#Model to data function using Gaussian process regression
def Model2Data_gp(sedModel, sedData):
    """
    Convert the continual model to the data-like model to directly
    compare with the data.

    Parameters
    ----------
    sedModel : ModelCombiner object
        The combined model.
    sedData : SEDClass object
        The data set of SED.

    Returns
    -------
    fluxModel : list
        The model flux list of the data.

    Notes
    -----
    None.
    """
    waveModel = sedModel.get_xList()
    fluxModel = sedModel.combineResult()
    fluxModelPht = sedData.model_pht(waveModel, fluxModel)
    fluxModelSpc = sedData.model_spc(sedModel.combineResult)
    fluxDict = {
        "pht": fluxModelPht,
        "spc": fluxModelSpc
        }
    return fluxDict

#The log_likelihood function: for SED fitting
def logLFunc(params, data, model):
    """
    Calculate the likelihood of data according to the model and its parameters.

    Parameters
    ----------
    params : list
        The variable parameter list of the model.
    data : DataSet
        The data need to fit.
    model : ModelCombiner
        The model to fit the data.

    Returns
    -------
    logL : float
        The log likelihood.

    Notes
    -----
    None.
    """
    model.updateParList(params)
    y = np.array(data.get_List('y'))
    e = np.array(data.get_List('e'))
    f = np.array(data.get_List('f'))
    ym = np.array(Model2Data(model, data))
    logL = -0.5 * ChiSq(y, ym, e, f)
    return logL

#The log_likelihood function: for SED fitting using Gaussian process regression
def logLFunc_gp(params, data, model):
    """
    Calculate the likelihood of data according to the model and its parameters.

    Parameters
    ----------
    params : list
        The variable parameter list of the model.
    data : DataSet
        The data need to fit.
    model : ModelCombiner
        The model to fit the data.

    Returns
    -------
    lnL : float
        The ln likelihood.

    Notes
    -----
    None.
    """
    #Get the data and error
    xSpc = np.array(data.get_csList("x"))
    yPht = np.array(data.get_dsList("y"))
    ySpc = np.array(data.get_csList("y"))
    ePht = np.array(data.get_dsList("e"))
    eSpc = np.array(data.get_csList("e"))
    fPht = np.array(data.get_dsList("f"))
    #Calculate the model
    model.updateParList(params)
    yDict = Model2Data_gp(model, data)
    yPhtModel = np.array(yDict["pht"])
    ySpcModel = np.array(yDict["spc"])
    nParVary = len(model.get_parVaryList())
    #lnlikelihood for photometric data
    if len(yPhtModel):
        f = np.exp(params[nParVary]) #The parameter to control the model incompleteness
        nParVary += 1
        sPht = np.sqrt(ePht**2 + (yPhtModel * f)**2)
        lnlPht = -0.5 * ChiSq(yPht, yPhtModel, sPht, fPht)
    else:
        f = 0
        lnlPht = 0
    #lnlikelihood for spectral data using Gaussian process regression
    if len(ySpcModel):
        a, tau = np.exp(params[nParVary:]) #The covariance for spectral residual
        wave_length = data.spc_WaveLength
        flux_median = data.spc_FluxMedian
        a   = a * flux_median   #Make "a" a relative value
        tau = tau * wave_length #Make "tau" a relative value
        gp = george.GP(a * kernels.Matern32Kernel(tau))
        sSpc = np.sqrt(eSpc**2 + (ySpcModel * f)**2)
        gp.compute(xSpc, sSpc)
        lnlSpc = gp.lnlikelihood(ySpc - ySpcModel)
    else:
        lnlSpc = 0
    lnL = lnlPht + lnlSpc
    return lnL
