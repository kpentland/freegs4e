#!/usr/bin/env python
#
# Calculate the equilibrium for a plasma surrounded by a metal wall
# This is done by creating a ring of coils, with feedback control setting
# the poloidal flux to zero at the location of each coil.

import numpy as np

import freegs4e

#########################################
# Create a circular metal wall by using a ring of coils and psi constraints

R0 = 1.0  # Middle of the circle
rwall = 0.5  # Radius of the circular wall

npoints = 200  # Number of points on the wall

# Poloidal angles
thetas = np.linspace(0, 2 * np.pi, npoints, endpoint=False)

# Points on the wall
Rwalls = R0 + rwall * np.cos(thetas)
Zwalls = rwall * np.sin(thetas)

#########################################
# Create the machine, which specifies coil locations
# and equilibrium, specifying the domain to solve over

coils = [
    ("wall_" + str(theta), freegs4e.machine.Coil(R, Z))
    for theta, R, Z in zip(thetas, Rwalls, Zwalls)
]

tokamak = freegs4e.machine.Machine(coils)

eq = freegs4e.Equilibrium(
    tokamak=tokamak,
    Rmin=0.1,
    Rmax=2.0,  # Radial domain
    Zmin=-1.0,
    Zmax=1.0,  # Height range
    nx=65,
    ny=65,  # Number of grid points
    boundary=freegs4e.boundary.freeBoundaryHagenow,
)  # Boundary condition

#########################################
# Plasma profiles

profiles = freegs4e.jtor.ConstrainPaxisIp(
    1e4, 1e6, 2.0  # Plasma pressure on axis [Pascals]  # Plasma current [Amps]
)  # Vacuum f=R*Bt

#########################################
# Coil current constraints
#

# Same location as the coils
psivals = [(R, Z, 0.0) for R, Z in zip(Rwalls, Zwalls)]

constrain = freegs4e.control.constrain(psivals=psivals)

#########################################
# Nonlinear solve

freegs4e.solve(
    eq,  # The equilibrium to adjust
    profiles,  # The toroidal current profile function
    constrain,  # Constraint function to set coil currents
    psi_bndry=0.0,
)  # Because no X-points, specify the separatrix psi

# eq now contains the solution

print("Done!")

print("Plasma current: %e Amps" % (eq.plasmaCurrent()))
print("Plasma pressure on axis: %e Pascals" % (eq.pressure(0.0)))

##############################################
# Save to G-EQDSK file

from freegs4e import geqdsk

with open("metal-wall.geqdsk", "w") as f:
    geqdsk.write(eq, f)

##############################################
# Final plot

axis = eq.plot(show=False)
constrain.plot(axis=axis, show=True)
