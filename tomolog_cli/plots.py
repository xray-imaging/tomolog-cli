import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

from mpl_toolkits.axes_grid1 import make_axes_locatable

from tomolog_cli import utils

    # dims          = meta[self.data_size][0].replace("(", "").replace(")", "").split(',')
    # width         = dims[2]
    # height        = dims[1]

    # plot_param = {}
    # plot_param['width']         = int(dims[2])
    # plot_param['height']        = int(dims[1])
    # plot_param['pixel_size']    = float(meta[self.pixel_size][0])
    # plot_param['resolution']    = float(meta[self.resolution][0])
    # plot_param['magnification'] = int(meta[self.magnification][0].replace("x", ""))
    # plot_param['binning']       = int(meta[self.binning][0])
    # plot_param['scale']         = args.scale
    # plot_param['idx']           = args.idx
    # plot_param['idy']           = args.idy
    # plot_param['idz']           = args.idz
    # plot_param['min']           = args.min
    # plot_param['max']           = args.max

def plot_projection(args, meta, proj, file_name, i):
    '''Plot the first projection with a scalebar and colorbar, and save it to FILENAME_PROJ
    '''
    pixel_size    = 'measurement_instrument_detector_pixel_size'
    magnification = 'measurement_instrument_detection_system_objective_camera_objective'
 
    resolution    = 'measurement_instrument_detection_system_objective_resolution'
    data_size     = 'exchange_data'

    dims          = meta[data_size][0].replace("(", "").replace(")", "").split(',')
    width         = int(dims[2])
    height        = int(dims[1])
    resolution    = float(meta[resolution][0])
    pixel_size    = float(meta[pixel_size][0])
    magnification = float(meta[magnification][0])

    # auto-adjust colorbar values according to a histogram
    mmin, mmax = utils.find_min_max(proj, 0.005)
    proj[proj > mmax] = mmax
    proj[proj < mmin] = mmin


    # plot
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    ax = fig.add_subplot()
    im = ax.imshow(proj, cmap='gray')
    if i==0:
        ax.plot([width*8.7/10, width*8.7/10+10000/resolution],
                [height*9.5/10, height*9.5/10], 'r')
        txt = ax.text(width*8.7/10, height *
                      9.1/10, '10um', color='red', fontsize=14)
    else:
        ax.plot([width*8.7/10, width*8.7/10+100/(pixel_size /
                magnification)], [height*9.5/10, height*9.5/10], 'r')
        txt = ax.text(width*8.5/10, height *
                      9.15/10, '100um', color='red', fontsize=14)

    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im, cax=cax)
    # plt.show()
    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)


def plot_recon(args, meta, recon, file_name):
    '''Plot orthoslices with scalebars and colorbars, and save the figure as FILENAME_RECON
    '''

    data_size     = 'exchange_data'
    binning_label = 'measurement_instrument_detector_binning_x'
    resolution    = 'measurement_instrument_detection_system_objective_resolution'

    dims          = meta[data_size][0].replace("(", "").replace(")", "").split(',')
    width         = int(dims[2])
    height        = int(dims[1])
    binning       = int(meta[binning_label][0])
    resolution    = float(meta[resolution][0])

    fig = plt.figure(constrained_layout=True, figsize=(6, 12))
    grid = fig.add_gridspec(3, 1, height_ratios=[
                            1, 1, width/height])
    slices = ['x', 'y', 'z']
    # autoadjust colorbar values according to a histogram

    if args.min==args.max:
        args.min, args.max = utils.find_min_max(np.concatenate(recon), args.scale)

    scalebar = 10  # um
    # plot 3 slices in a column
    w = width//binning
    h = height//binning

    sl = [args.idx,args.idy,args.idz]#params['id'+slices[k]]
    for k in range(3):
        recon[k][recon[k] > args.max] = args.max
        recon[k][recon[k] < args.min] = args.min
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
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/resolution /
                    binning], [w*9.5/10, w*9.5/10], 'r')
            txt = ax.text(w*8.7/10, w*9.15/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])
        else:  # x,y slices
            ax.plot([w*8.7/10, w*8.7/10+scalebar*1000/resolution /
                    binning], [h*9.5/10, h*9.5/10], 'r')
            txt = ax.text(w*8.7/10, h*9.1/10,
                          f'{scalebar}um', color='red', fontsize=14)
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=1, foreground='w')])
    # plt.show()
    # save
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0, dpi=300)