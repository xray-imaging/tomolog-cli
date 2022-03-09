import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

from mpl_toolkits.axes_grid1 import make_axes_locatable

from tomolog_cli import utils


def plot_projection(params, proj, file_name, scale=10000):
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
    ax.plot([params['width']*8.7/10, params['width']*8.7/10+scale/params['resolution']],
            [params['height']*9.5/10, params['height']*9.5/10], 'r')
    txt = ax.text(params['width']*8.7/10, params['height'] *
                  9.1/10, '10um', color='red', fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im, cax=cax)
    # plt.show()
    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)


def plot_recon(args, params, recon, file_name):
    '''Plot orthoslices with scalebars and colorbars, and save the figure as FILENAME_RECON
    '''

    fig = plt.figure(constrained_layout=True, figsize=(6, 12))
    grid = fig.add_gridspec(3, 1, height_ratios=[
                            1, 1, params['width']/params['height']])
    slices = ['x', 'y', 'z']
    # autoadjust colorbar values according to a histogram

    if params['min']==params['max']:
        params['min'], params['max'] = utils.find_min_max(np.concatenate(recon), params['scale'])

    scalebar = 10  # um
    # plot 3 slices in a column
    w = params['width']//params['binning']
    h = params['height']//params['binning']

    sl = [args.idx,args.idy,args.idz]#params['id'+slices[k]]
    for k in range(3):
        recon[k][recon[k] > params['max']] = params['max']
        recon[k][recon[k] < params['min']] = params['min']
        ax = fig.add_subplot(grid[k])
        im = ax.imshow(recon[k], cmap='gray')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        plt.colorbar(im, cax=cax)
        #sl = params['id'+slices[k]]
        ax.set_ylabel(f'slice {slices[k]}={sl[k]}', fontsize=14)
        if(k < 2):
            ax.set_xticklabels([])
        if k == 2:  # z slices
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/params['resolution'] /
                    params['binning']], [w*9.5/10, w*9.5/10], 'r')
            txt = ax.text(w*8.7/10, w*9.15/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])
        else:  # x,y slices
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/params['resolution'] /
                    params['binning']], [h*9.5/10, h*9.5/10], 'r')
            txt = ax.text(w*8.7/10, h*9.1/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])
    # plt.show()
    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)