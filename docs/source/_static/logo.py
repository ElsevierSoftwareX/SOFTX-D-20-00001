from __future__ import division

import os

import matplotlib.pyplot as plt
import microstructpy as msp
import numpy as np
from matplotlib import collections

__author__ = 'Kenneth (Kip) Hart'


def main(n_seeds, size_rng, pos_rng, k_lw):
    bkgrnd_color = 'black'
    line_color = (1, 1, 1, 1)  # white

    dpi = 300
    init_size = 2000
    logo_size = 1500
    favicon_size = 48

    logo_basename = 'logo.svg'
    favicon_basename = 'favicon.ico'
    path = os.path.dirname(__file__)
    logo_filename = os.path.join(path, logo_basename)
    favicon_filename = os.path.join(path, favicon_basename)

    # Set Domain
    domain = msp.geometry.Circle()

    # Set Seed List
    np.random.seed(size_rng)
    rs = 0.3 * np.random.rand(n_seeds)

    factory = msp.seeding.Seed.factory
    seeds = msp.seeding.SeedList([factory('circle', r=r) for r in rs])
    seeds.position(domain, rng_seed=pos_rng)

    # Create the Poly Mesh
    pmesh = msp.meshing.PolyMesh.from_seeds(seeds, domain)

    # Create and Format the Figure
    plt.clf()
    plt.close('all')
    fig = plt.figure(figsize=(init_size / dpi, init_size / dpi), dpi=dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.add_axes(ax)

    # Plot the Domain
    domain.plot(ec='none', fc=bkgrnd_color)

    # Plot the Facets
    facet_colors = []
    for neigh_pair in pmesh.facet_neighbors:
        if min(neigh_pair) < 0:
            facet_colors.append('none')
        else:
            facet_colors.append(line_color)

    lw = k_lw * init_size / 100
    pmesh.plot_facets(colors=facet_colors, linewidth=lw, capstyle='round')

    pts = np.array(pmesh.points)
    rs = np.sqrt(np.sum(pts * pts, axis=1))
    mask = np.isclose(rs, 1)

    edges = []
    for facet in pmesh.facets:
        if np.sum(mask[facet]) != 1:
            continue

        edge = np.copy(pts[facet])
        if mask[facet[0]]:
            u = edge[0] - edge[1]
            u *= 1.1
            edge[0] = edge[1] + u
        else:
            u = edge[1] - edge[0]
            u *= 1.1
            edge[1] = edge[0] + u
        edges.append(edge)

    pc = collections.LineCollection(edges, color=line_color, linewidth=lw,
                                    capstyle='round')
    ax.add_collection(pc)

    # Format the Plot and Convert to Image Array
    plt.axis('square')
    plt.axis(1.01 * np.array([-1, 1, -1, 1]))
    fig.canvas.draw()

    plt_im = np.array(fig.canvas.get_renderer()._renderer)
    mask = plt_im[:, :, 0] > 0.5 * 255

    # Create the Logo
    logo_im = np.copy(plt_im)

    xx, yy = np.meshgrid(np.arange(logo_im.shape[0]), np.arange(logo_im.shape[1]))
    zz = - 0.2 * xx +   0.9 * yy
    ss = (zz - zz.min()) / (zz.max() - zz.min())

    c1 = [67, 206, 162]
    c2 = [24, 90, 157]


    logo_im[mask, -1] = 0  # transparent background

    # gradient
    for i in range(logo_im.shape[-1] - 1):
        logo_im[~mask, i] = (1 - ss[~mask]) * c1[i] + ss[~mask] * c2[i]

    inds = np.linspace(0, logo_im.shape[0] - 1, logo_size).astype('int')
    logo_im = logo_im[inds]
    logo_im = logo_im[:, inds]

    pad_width =  logo_im.shape[0]
    pad_height = 0.5 * logo_im.shape[1]
    pad_shape = np.array([pad_width, pad_height, logo_im.shape[2]]).astype('int')
    logo_pad = np.zeros(pad_shape, dtype=logo_im.dtype)
    pad_im = np.concatenate((logo_pad, logo_im, logo_pad), axis=1)

    plt.imsave(logo_filename, logo_im, dpi=dpi)
    plt.imsave('pad_' + logo_filename, pad_im, dpi=dpi)

    # Create the Favicon
    fav_im = np.copy(logo_im)
    inds = np.linspace(0, fav_im.shape[0] - 1, favicon_size).astype('int')
    fav_im = fav_im[inds]
    fav_im = fav_im[:, inds]
    
    plt.imsave(favicon_filename, fav_im, dpi=dpi, format='png')


if __name__ == '__main__':
    n_seeds = 14
    size_rng = 4
    pos_rng = 7
    k_lw = 1.1

    main(n_seeds, size_rng, pos_rng, k_lw)