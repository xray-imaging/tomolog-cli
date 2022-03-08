
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tomolog_cli import utils
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import numpy as np


def plot_projection2(pars, proj, file_name):
    '''Plot the first projection with a scalebar and colorbar, and save it to FILENAME_PROJ
    '''

    # auto-adjust colorbar values according to a histogram
    mmin, mmax = utils.find_min_max(proj, 0.005)
    proj[proj > mmax] = mmax
    proj[proj < mmin] = mmin

    # plot
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    ax = fig.add_subplot()
    im = ax.imshow(proj, cmap='gray')
    ax.plot([pars['width']*8.7/10, pars['width']*8.7/10+100/(pars['pixelsize'] /
            pars['cameraobjective'])], [pars['height']*9.5/10, pars['height']*9.5/10], 'r')
    txt = ax.text(pars['width']*8.5/10, pars['height'] *
                  9.15/10, '100um', color='red', fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im, cax=cax)

    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)


def plot_projection(pars, proj, file_name):
    '''Plot the first projection with a scalebar and colorbar, and save it to FILENAME_PROJ
    '''

    # auto-adjust colorbar values according to a histogram
    mmin, mmax = utils.find_min_max(proj, 0.005)
    proj[proj > mmax] = mmax
    proj[proj < mmin] = mmin

    # plot
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    ax = fig.add_subplot()
    im = ax.imshow(proj, cmap='gray')
    ax.plot([pars['width']*8.7/10, pars['width']*8.7/10+10000/pars['resolution']],
            [pars['height']*9.5/10, pars['height']*9.5/10], 'r')
    txt = ax.text(pars['width']*8.7/10, pars['height'] *
                  9.1/10, '10um', color='red', fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im, cax=cax)

    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)


def plot_recon(pars, recon, file_name):
    '''Plot orthoslices with scalebars and colorbars, and save the figure as FILENAME_RECON
    '''

    fig = plt.figure(constrained_layout=True, figsize=(6, 12))
    grid = fig.add_gridspec(3, 1, height_ratios=[
                            1, 1, pars['width']/pars['height']])
    slices = ['x', 'y', 'z']
    # autoadjust colorbar values according to a histogram
    if pars['min']==pars['max']:
        pars['max'], pars['min'] = utils.find_min_max(np.concatenate(recon), pars['scale'])

    scalebar = 10  # um
    # plot 3 slices in a column
    w = pars['width']//pars['binning']
    h = pars['height']//pars['binning']

    for k in range(3):
        recon[k][recon[k] > pars['max']] = pars['max']
        recon[k][recon[k] < pars['min']] = pars['min']
        ax = fig.add_subplot(grid[k])
        im = ax.imshow(recon[k], cmap='gray')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        plt.colorbar(im, cax=cax)
        sl = pars['id'+slices[k]]
        ax.set_ylabel(f'slice {slices[k]}={sl}', fontsize=14)
        if(k < 2):
            ax.set_xticklabels([])
        if k == 2:  # z slices
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/pars['resolution'] /
                    pars['binning']], [w*9.5/10, w*9.5/10], 'r')
            txt = ax.text(w*8.7/10, w*9.15/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])
        else:  # x,y slices
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/pars['resolution'] /
                    pars['binning']], [h*9.5/10, h*9.5/10], 'r')
            txt = ax.text(w*8.7/10, h*9.1/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])

    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)
