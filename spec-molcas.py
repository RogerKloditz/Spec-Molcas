#!/usr/bin/env python3


def get_input():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'Output-File',
		help='Output-File from a RASSI calculation'
	)
	parser.add_argument(
		'-s',
		'--sigma',
		required=False,
		type=float,
		default=150,
		help='Plotting option for gaussian broadening in cm**-1, default=150 cm**-1'
	)
	parser.add_argument(
		'-x0',
		'--begin',
		required=False,
		type=float,
		default=8000,
		help='Begin of the spectrum in cm**-1, default=8000 cm**-1'
	)
	parser.add_argument(
		'-p',
		'--points',
		required=False,
		type=int,
		default=1000,
		help='# of points the spectrum is plotted with, default=1000'
	)
	parser.add_argument(
		'-x1',
		'--end',
		required=False,
		type=float,
		default=25000,
		help='End of the spectrum in cm**-1, default=25000 cm**-1'
	)
	parser.add_argument(
		'-t',
		'--temperature',
		required=False,
		type=float,
		default=298.15,
		help='Temperature for Boltzmann distribution in K, default=298.15 K'
	)
	parser.add_argument(
		'-u',
		'--unit',
		required=False,
		type=str,
		default="cm**-1",
		help='Unit to plot the spectra - "cm**-1" or "nm", default="cm**-1"'
	)
	parser.add_argument(
        '-b',
        '--boltzmann',
        required=False,
        type=float,
        default=0.1,
   	    help="Threshold of Boltzmann factor for including initial states, default=0.1"
	)
	parser.add_argument(
        '-f',
        '--file',
        required=False,
        type=str,
        default=None,
   	    help="File with experimental values for additional plotting, default=None"
	)
	return vars(parser.parse_args())

def get_string_block(file,start,end):

	'''
	Extract a list of strings from a file from start to end.
	'''

	block = []
	with open(file) as f:
		Switch_Read = False
		for line in f:
			if start in line:          	# Start reading the important stuff here
				Switch_Read = True
			if Switch_Read == True:
				if end in line:     	# Stop if the end of the block is found
					break

				block.append(line)

	return block

def get_wavenumbers(input_file):
	
	'''
	Extract the wavenumbers from the spin-orbit states as a numpy list.
	'''

	start = 'Eigenvalues of complex Hamiltonian:'
	end = 'Weights of the five most important'
	pattern = re.compile('^\s+\d+\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+\.\d+)\s*$')
	wavenumbers = np.array([])

	print("Start reading the excited state energies...",end='')

	block = get_string_block(input_file,start,end)

	for line in block:
		match = pattern.match(line)
		if match:
			wavenumbers = np.append(wavenumbers,match.group(3))	# Save the wavenumbers 

	wavenumbers = wavenumbers.astype(float)

	print("done. ",end='')
	return wavenumbers

def get_transitions(input_file):

	'''
	Extract the oscillator strengths with the corresponding transitions.
	The first array has the initial states, the second the final states and the 
	third the oscillator strengths.
	'''

	print("Start reading the transitions..............",end='')

	start = '++ Dipole transition strengths (SO states):'
	end = '++ Velocity transition strengths (SO states):'
	pattern = re.compile('^\s+(\d+)\s+(\d+)\s+(\d\.\d+E[\+\-]\d{2})')
	osc = np.array([])
	init = np.array([])
	final = np.array([])

	block = get_string_block(input_file,start,end)
	
	for line in block:
		match = pattern.match(line)
		if match:
			a,b,c = match.group(1,2,3)	
			init = np.append(init,a)
			final = np.append(final,b)
			osc = np.append(osc,c)

	init = init.astype(int)
	final = final.astype(int)
	osc = osc.astype(float)

	print("done. ",end='')
	return init,final,osc

def get_trans_wvn(num,wvn,init,final):

	'''
	Find the wavenumbers for every transition,
	i.e. wavenumber(state_final) - wavenumber(state_initial).
	'''

	trans_wvn = np.ndarray(num)

	for index in range(num):
		init_wvn =  wvn[init[index]-1] # Wavenumber of the initial state
		final_wvn = wvn[final[index]-1] # Wavenumber of the final state
		trans_wvn[index] = final_wvn - init_wvn

	return trans_wvn

def get_boltzmann(num,wvn,temp):

	'''
	The Boltzmann distribution for the desired temperature is
	used to weight the transitions.
	'''

	boltz = np.ndarray(num)
	k_B = 1.380650e-23
	wvn_to_J = 6.6260688e-34 * 2.99792458e8 * 100.0		# E = h*c*mu[m**-1] 
	boltz = np.exp(-wvn_to_J * wvn/(k_B * temp))

	return boltz

def write_transitions(num,thresh,trans,init,final,boltz,osc):
	with open('transitions.dat','w') as file:

		file.write('Transition in cm**-1  Initial state  Final state  Boltzmann factor  Weighted osc. strength\n')
		file.write('------------------------------------------------------------------------------------------\n')
		for index in range(num):
			if boltz[init[index] - 1] > thresh:
				file.write('{0:20.6f} {1:14d} {2:12d} {3:17.6f} {4:23.6f}\n'.format(
							trans[index],		# Transition wavenumber
							init[index],		# Initial state
							final[index],		# Final state
							boltz[init[index]-1],# Boltzmann factor of initial state
							osc[index]))		# Oscillator strength of transition

	print("\nFile transitions.dat written and contains relevant information.\n")

def get_index_list(num,trans_wvn,init,thresh,boltz):
	
	'''
	Get the indices for the trans_wvn list for which the Boltzmann-weighted .
	'''

	index_list = np.array([])

	for trans in range(num):
		if begin < trans_wvn[trans] < end:
			if boltz[init[trans] - 1] > thresh:
				index_list = np.append(index_list,trans)

	index_list = index_list.astype(int)

	return index_list

def get_line_spectrum(num,trans_wvn,osc,init,thresh,boltz):

	'''
	Write the line spectrum.
	'''

	index_list = get_index_list(num = num,trans_wvn = trans_wvn,init = init,thresh = thresh, boltz = boltz)
	print("Line spectrum...",end='')

	line_spectrum = np.zeros([len(index_list),2])

	for index,trans in enumerate(index_list):
		line_spectrum[index,0] = trans_wvn[trans]
		line_spectrum[index,1] = osc[trans]

	print('done.')
	return line_spectrum

def get_spectrum(linspec,begin,end,points):
	
	'''
	Write the Guassian-broadened spectrum within specified limits based on the line spectrum.
	'''

	print("Spectrum........",end='')

	spectrum = np.zeros([points+1,2])

	for point in range(points+1):
		spectrum[point,0] = begin + point/points * (end - begin)
		for trans,osc in linspec:
			spectrum[point,1] += np.exp(-0.5 * np.square((spectrum[point,0] - trans)/sigma)) * osc

	spectrum[:,1] = spectrum[:,1] / np.amax(spectrum[:,1])

	print("done. ")
	return spectrum

def write_spectrum(file,spec):

	'''
	Write x-y-data (spec) into a file named file.
	Assume that the x values can be cast as integers and y values as floats.
	'''

	with open(file,'w') as f:
		for line in spec:
			x,y = line
			f.write('{0:6d}{1:7.4f}\n'.format(int(x),float(y)))

def plot_spectra(spectrum,line_spectrum,unit,begin,end,exp_file):

	'''
	Plot section.
	'''

	import matplotlib as mpl
	import matplotlib.pyplot as plt

	# Parameters for plotting. Feel free to change!
	#---------------------------------------------------
	mpl.rcParams['font.family'] = 'serif'
	mpl.rcParams['font.sans-serif'] = 'Times'
	mpl.rcParams['font.size'] = '20'
	mpl.rc('text',usetex = True)
	mpl.rcParams['axes.linewidth'] = 2.0
	mpl.rcParams['xtick.labelsize'] = 'medium'
	mpl.rcParams['ytick.labelsize'] = 'medium'
	mpl.rcParams['xtick.major.size'] = 7.0
	mpl.rcParams['ytick.major.size'] = 7.0
	mpl.rcParams['xtick.minor.visible'] = True
	mpl.rcParams['ytick.minor.visible'] = True
	mpl.rcParams['xtick.minor.size'] = 4.0
	mpl.rcParams['ytick.minor.size'] = 4.0
	mpl.rcParams['xtick.major.width'] = 2.0
	mpl.rcParams['ytick.major.width'] = 2.0
	mpl.rcParams['xtick.minor.width'] = 2.0
	mpl.rcParams['ytick.minor.width'] = 2.0
	#---------------------------------------------------
	
	fig, ax = plt.subplots(figsize=(10,7))

	if unit == 'nm':
		
		begin = 1.0e7 / begin
		end = 1.0e7 / end
		spectrum[:,0] = 1.0e7 / spectrum[:,0]
		line_spectrum[:,0] = 1.0e7 / line_spectrum[:,0]

		begin,end = end,begin
		
		end = end - end%100 		# Round down to a full 100
		begin = begin - begin%100 	# Round down to a full 100

		step = 100		# Please change if necessary!
		xlabel = r'Wellenlänge [nm]'
	else:
		step = 2000		# Please change if necessary!
		xlabel = r'Wellenzahl [cm$^{-1}$]'

	x = spectrum[:,0]
	y = spectrum[:,1]
	
	# Plot spectrum
	ax.plot(x,y,color='k')

	# Plot line spectrum
	#for trans,osc in line_spectrum:
	#	ax.vlines(trans,0,osc,color='r',linewidth=1.0)

	x_ticks = [begin]

	while x_ticks[-1] < end:
		x_ticks.append(x_ticks[-1] + step)

	ax.set_xticks(x_ticks)
	ax.set_xlabel(xlabel,fontsize=24)
	ax.set_xlim(begin,end)
	ax.set_ylim(0,1)
	ax.set_ylabel('Normierte Intensität',fontsize=24)
	
	if exp_file:
		
		exp_x,exp_y = [],[]
		with open(exp_file) as f:
			for line in f:
				l1,l2 = map(float,line.split())
				if begin < l1 < end:
					exp_x.append(l1)
					exp_y.append(l2)
		
		if len(exp_x) == 0:
			print('Experimental data not within specified range! No experimental graph, then...')
		else:
			max_exp_y = sorted(exp_y)[-1]		# Get max y value
			for index in range(len(exp_y)):		# Normalize
				exp_y[index] = exp_y[index] / max_exp_y

			ax.plot(exp_x,exp_y,color='r',linestyle=':',linewidth='1.5')
	ax.text(0.85, 0.9, r'[Np(Salen)$_2$]',
			fontsize=24,
			ha='center',
			va='center',
			transform=ax.transAxes,
			bbox=dict(fc='lightgrey',edgecolor='k',pad=10.0))
	plt.tight_layout()
	plt.show()

#--------------------------------------------------------

if __name__ == '__main__':

	args = get_input()

	import numpy as np
	import re

	output = args['Output-File']
	sigma = args['sigma']
	begin = args['begin']
	end = args['end']
	points = args['points']
	temp = args['temperature']
	unit = args['unit']
	thresh_boltz = args['boltzmann']
	exp_file = args['file']
	
	print()
	print("Begin spectrum at:             {0:7d} cm**-1".format(int(begin)))
	print("End spectrum at:               {0:7d} cm**-1".format(int(end)))
	print("Sigma for gaussian broadening: {0:7.1f} cm**-1".format(sigma))
	print("Used points for plotting:      {0:7d}".format(points))
	print("Temperature for Boltzmann:     {0:7.2f} K".format(temp))
	print("Spectra will be printed in:    {0:>7}".format(unit))
	print("Threshold of Boltzmann factor: {0:7.2f}".format(thresh_boltz))
	print("Experimental values from:      {0}".format(exp_file))
	print()

	wavenumbers = get_wavenumbers(output)
	
	num_states = len(wavenumbers)
	print("Found {0:4d} states.".format(num_states))
	
	init_state,final_state,osc_strength = get_transitions(output)

	num_trans = len(osc_strength)
	print("Found {0:5d} transitions.\n".format(num_trans))

	np.savetxt('energies.dat',wavenumbers)
	print('File energies.dat written and contains the state energies in cm**-1.\n')
	
	if num_trans == 0:
		print("No oscillator strengths found. I quit.")		
		quit()

	trans_wvn = get_trans_wvn(num = num_trans, wvn = wavenumbers, init = init_state,final = final_state)

	p_Boltzmann = get_boltzmann(num = num_trans, wvn = wavenumbers, temp = temp)

	# Weight oscillator strengths with Boltzmann factor and normalize
	for index in range(num_trans):
		osc_strength[index] = osc_strength[index] * p_Boltzmann[init_state[index] - 1]
	
	osc_strength = osc_strength / osc_strength.max()

	write_transitions(	num = num_trans,
						thresh = thresh_boltz,
						trans = trans_wvn,
						init = init_state,
						final = final_state,
						boltz = p_Boltzmann,
						osc = osc_strength)

	print('Start writing spectra.\n')

	line_spectrum = get_line_spectrum(	num = num_trans,
										trans_wvn = trans_wvn,
										osc = osc_strength,
										init = init_state,
										thresh = thresh_boltz,
										boltz = p_Boltzmann)

	write_spectrum('line_spectrum.dat',line_spectrum)
	print("File line_spectrum.dat written.")

	spectrum = get_spectrum(linspec = line_spectrum,begin = begin,end = end,points = points)

	write_spectrum('spectrum.dat',spectrum)
	print("File spectrum.dat written.")
	print()

	plot_spectra(spectrum = spectrum,line_spectrum = line_spectrum,unit = unit,begin = begin,end = end,exp_file = exp_file)

	print("All done!")
	print()
