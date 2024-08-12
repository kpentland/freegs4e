"""
Plotting using matplotlib

Copyright 2024 Nicola C. Amorisco, Adriano Agnello, George K. Holt, Ben Dudson.

FreeGS4E is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FreeGS4E is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with FreeGS4E.  If not, see <http://www.gnu.org/licenses/>.

"""

from numpy import amax, amin, linspace

from . import critical


def plotCoils(coils, axis=None):
    import matplotlib.pyplot as plt

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    return axis


def plotConstraints(control, axis=None, show=True):
    """
    Plots constraints used for coil current control

    axis     - Specify the axis on which to plot
    show     - Call matplotlib.pyplot.show() before returning

    """

    import matplotlib.pyplot as plt

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    # Locations of the X-points
    for r, z in control.xpoints:
        axis.plot(r, z, "bx")

    if control.xpoints:
        axis.plot([], [], "bx", label="X-point constraints")

    # Isoflux surfaces
    for r1, z1, r2, z2 in control.isoflux:
        axis.plot([r1, r2], [z1, z2], ":b^")

    if control.isoflux:
        axis.plot([], [], ":b^", label="Isoflux constraints")

    if show:
        plt.legend()
        plt.show()

    return axis


def plotEquilibrium(
    eq, axis=None, show=True, oxpoints=True, wall=True, limiter=True
):
    """
    Plot the equilibrium flux surfaces

    axis     - Specify the axis on which to plot
    show     - Call matplotlib.pyplot.show() before returning
    oxpoints - Plot X points as red circles, O points as green circles
    wall     - Plot the wall (limiter)

    """

    import matplotlib.pyplot as plt

    psi = eq.psi()

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    levels = linspace(amin(psi), amax(psi), 50)

    axis.contour(eq.R, eq.Z, psi, levels=levels)
    axis.set_aspect("equal")
    axis.set_xlabel("Major radius [m]")
    axis.set_ylabel("Height [m]")

    try:
        eq._profiles

        if oxpoints:
            # Add O- and X-points
            # opt, xpt = critical.find_critical(eq.R, eq.Z, psi)
            opt = eq._profiles.opt
            xpt = eq._profiles.xpt

            for r, z, _ in xpt:
                axis.plot(r, z, "ro")
            for r, z, _ in opt:
                axis.plot(r, z, "gx")

            if xpt is not []:
                psi_bndry = xpt[0][2]
                if eq._profiles.flag_limiter:
                    # axis.contour(eq.R, eq.Z, psi, levels=[eq._profiles.psi_bndry], colors="k")
                    axis.contour(
                        eq.R,
                        eq.Z,
                        psi,
                        levels=[psi_bndry],
                        colors="r",
                        linestyles="dashed",
                    )
                    cs = plt.contour(
                        eq.R,
                        eq.Z,
                        psi,
                        levels=[eq._profiles.psi_bndry],
                        alpha=0,
                    )
                    paths = cs.collections[0].get_paths()
                    for path in paths:
                        vertices = path.vertices
                        if np.sum(vertices[0] == vertices[-1]) > 1:
                            axis.plot(vertices[:, 0], vertices[:, 1], "k")

                else:
                    axis.contour(
                        eq.R, eq.Z, psi, levels=[psi_bndry], colors="r"
                    )

                # Add legend
                axis.plot([], [], "ro", label="X-points")
                axis.plot([], [], "r", label="Separatrix")
            if opt is not []:
                axis.plot([], [], "go", label="O-points")

    except:
        print(
            "This equilibrium has not been solved: the separatrix can not be drawn."
        )
        print("Please solve first for a plot of the critical points.")

    if wall and eq.tokamak.wall and len(eq.tokamak.wall.R):
        axis.plot(
            list(eq.tokamak.wall.R) + [eq.tokamak.wall.R[0]],
            list(eq.tokamak.wall.Z) + [eq.tokamak.wall.Z[0]],
            "k",
        )
    if limiter and eq.tokamak.limiter and len(eq.tokamak.limiter.R):
        axis.plot(
            list(eq.tokamak.limiter.R) + [eq.tokamak.limiter.R[0]],
            list(eq.tokamak.limiter.Z) + [eq.tokamak.limiter.Z[0]],
            "k--",
            lw=0.5,
        )

    if show:
        plt.legend()
        plt.show()

    return axis


import numpy as np


def make_broad_mask(mask, layer_size=1):
    """Enlarges a mask with the points just outside the input, with a width=`layer_size`

    Parameters
    ----------
    layer_size : int, optional
        Width of the layer outside the limiter, by default 3

    Returns
    -------
    layer_mask : np.ndarray
        Mask of the points outside the limiter within a distance of `layer_size` from the limiter
    """
    nx, ny = np.shape(mask)
    layer_mask = np.zeros(
        np.array([nx, ny]) + 2 * np.array([layer_size, layer_size])
    )

    for i in np.arange(-layer_size, layer_size + 1) + layer_size:
        for j in np.arange(-layer_size, layer_size + 1) + layer_size:
            layer_mask[i : i + nx, j : j + ny] += mask
    layer_mask = layer_mask[
        layer_size : layer_size + nx, layer_size : layer_size + ny
    ]
    layer_mask = (layer_mask > 0).astype(bool)
    return layer_mask
