import matplotlib.pyplot as plt
from astropy.io import fits
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import configparser
from fim_scripts.paths import FUTILITY_DIR
import os


def plotter(args, data_stats):
    infile = args['infile']
    chunks = args['chunks']
    medians = data_stats['medians']
    means = data_stats['means']
    stds = data_stats['stds']
    fwhms = data_stats['fwhms']
    spreads = data_stats['spreads']
    mags = data_stats['mags']
    x = data_stats['x']
    y = data_stats['y']
    elongations = data_stats['elongations']
    elev = args['elev']
    azim = args['azim']
    output_dir= args['output_dir']
    chunkwidth = args['chunkwidth']
    chunkheight= args['chunkheight']
    ortho=args['ortho']
    if output_dir == None or not output_dir:
        output_dir='plots'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    default = configparser.ConfigParser()
    default.read(f'{FUTILITY_DIR}/fim_scripts/default.cfg')


    

    if 'left' in infile:
        L = len(infile)
        name = infile[L-37:L-10]
    elif 'right' in infile:
        L = len(infile)
        name = infile[L-38:L-10]
    elif 'telescope' in infile:
        L = len(infile)
        i = infile.find('telescope')
        name = infile[i + 12:L-5]
    else:
        name=infile

    plt.ion() # comment this line out if you dont want the window to be interactive
    


    if chunks:
        xc = np.arange(chunkwidth + 1)
        yc = np.arange(chunkheight + 1)
        xc, yc = np.meshgrid(xc, yc)

        # Create a 3D plot of the medians
        fig = plt.figure(figsize=(10, 6))
        ax1 = fig.add_subplot(121, projection='3d')
        if ortho:
            ax1.set_proj_type('ortho')
        sc1 = ax1.scatter(xc, yc, medians, c=medians, cmap='viridis', marker='o')
        fig.colorbar(sc1, ax=ax1, shrink=.3, aspect=10)
        ax1.view_init(elev=elev, azim=azim)
        ax1.set_title('3D Plot of Medians')
        ax1.set_xlabel('Chunk Index X')
        ax1.set_ylabel('Chunk Index Y')
        ax1.set_zlabel('Median Value')

        # Create a 3D plot of the means

        ax2 = fig.add_subplot(122, projection='3d')
        if ortho:
            ax2.set_proj_type('ortho')
        sc2 = ax2.scatter(xc, yc, means, c=means, cmap='viridis', marker='o')
        fig.colorbar(sc2, ax=ax2, shrink=.3, aspect=10)
        ax2.view_init(elev=elev, azim=azim)
        ax2.set_title('3D Plot of Means')
        ax2.set_xlabel('Chunk Index X')
        ax2.set_ylabel('Chunk Index Y')
        ax2.set_zlabel('Mean Value')
        
        # Save the plot as a PNG
        output_path = os.path.join(output_dir, f'{name}_3d_info.png')
        plt.savefig(output_path, format='png')
        plt.show() # comment this out if you dont want popup Xwindow
        plt.close()
        print(f"3D plot saved as {output_path}")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Scatter plot for means vs. standard deviations
        ax.scatter(means.flatten(), stds.flatten(), s=10, alpha=0.7, color='blue', label='Means')

        # Scatter plot for medians vs. standard deviations
        ax.scatter(medians.flatten(), stds.flatten(), s=10, alpha=0.7, color='red', label='Medians')

        # Adding title and labels
        ax.set_title('Poisson Noise Statistics: Means and Medians vs Standard Deviations')
        ax.set_xlabel('Value')
        ax.set_ylabel('Standard Deviation')
        ax.grid(True)

        # Adding a legend
        ax.legend()

        # Save the plot as a PNG
        output_path = os.path.join(output_dir, f'{name}_ms_vs_stds_info.png')
        plt.savefig(output_path, format='png')
        plt.close()
        print(f"Plot saved as {output_path}")
    
    
    # plot the FWHM
    fig = plt.figure(figsize=(15, 9))

    ax1 = fig.add_subplot(221, projection='3d')
    if ortho:
        ax1.set_proj_type('ortho')
    sc1 = ax1.scatter(x, y, fwhms, c=fwhms, cmap='viridis', marker='o')
    fig.colorbar(sc1, ax=ax1, shrink=.3, aspect=10)
    ax1.view_init(elev=elev, azim=azim)
    ax1.set_title('3D Plot of FWHM of detected stars in given exposure')
    ax1.set_zlabel('FWHM Value')
    ax1.set_xlabel('Chunk Index X')
    ax1.set_ylabel('Chunk Index Y')
    

    # plot the spread

    ax2 = fig.add_subplot(222, projection='3d')
    if ortho:
        ax2.set_proj_type('ortho')

    sc2 = ax2.scatter(x, y, spreads, c=spreads, cmap='viridis', marker='o')
    fig.colorbar(sc2, ax=ax2, shrink=.3, aspect=10)
    ax2.view_init(elev=elev, azim=azim)
    ax2.set_title('Plot of spread value of stars in given exposure')
    ax2.set_zlabel('Spread Value')            
    ax2.set_xlabel('Chunk Index X')
    ax2.set_ylabel('Chunk Index Y')

    # plot the mags
    ax3 = fig.add_subplot(223, projection='3d')
    if ortho:
        ax3.set_proj_type('ortho')
    sc3 = ax3.scatter(x, y, mags, c=mags, cmap='viridis', marker='o')
    fig.colorbar(sc2, ax=ax3, shrink=.3, aspect=10)
    ax3.view_init(elev=elev, azim=azim)
    ax3.set_title('Plot magnitude of stars in given exposure')
    ax3.set_zlabel('Mag Value')
    ax3.set_xlabel('Chunk Index X')
    ax3.set_ylabel('Chunk Index Y')
    
    # plot the elongations

    ax4 = fig.add_subplot(224, projection='3d')
    if ortho:
        ax4.set_proj_type('ortho')
    sc4 = ax4.scatter(x, y, elongations, c=elongations, cmap='viridis', marker='o')
    fig.colorbar(sc4, ax=ax4, shrink=.3, aspect=10)
    ax4.view_init(elev=elev, azim=azim)
    ax4.set_title('Plot of star elongations in given exposure')
    ax4.set_zlabel('Elongation Value(a/b)')
    ax4.set_xlabel('Chunk Index X')
    ax4.set_ylabel('Chunk Index Y')
    
    # Save the plot as a PNG
    output_path = os.path.join(output_dir, f'{name}_3d_star_info.png')
    plt.savefig(output_path, format='png')
    plt.show() # comment this out if you dont want popup Xwindow
    plt.close()
    print(f"3D plot saved as {output_path}")
    return True