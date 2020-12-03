# Spec-Molcas
Take the output-file from a spin-orbit coupled  rassi-calculation from OpenMolcas and write/plot the electronic spectra

Usage:

spec-molcas.py rassi.log [options]

Help:

spec-molcas.py -h

spec-molcas.py --help

Output:

linespectrum.dat --> XY-file with wavenumbers and respective transition intensities

spectrum.dat --> XY-file with Gaussian-broadened transitions

energies.dat --> file with excited state energies relative to ground state

transitions.dat --> file with comprehensive information on the transitions
