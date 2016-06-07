# -*- coding: utf-8 -*-
"""
Created on Tue May 24 09:18:45 2016
@author: amylytle
"""

""" Program initialization """

# Import modules
import os
import math
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
import tkFileDialog

os.system("cls" if os.name == "nt" else "clear")

# Program header
print("---------------------------------------------------")
print(" Analysis Program for Counterpropagating Scan Data")
print(" Authors: R. Camuccio, T. Lehman-Borer, and A. Lytle")
print(" Version: 2.0")
print("---------------------------------------------------")
print

#### FUNCTIONS ####
def Smooth(position_array, wavelength_array, intensity_array, smooth_factor):
	""" This function accepts a wavelength and intensity array and returns a smoothed intensity array """

	# Create temporary list for value handling
	new_list = []

	# Calculate edge pixels to avoid smoothing
	edge_pixels = (smooth_factor - 1) // 2

	# Initialize sum and average
	current_sum = 0
	average = 0

	# Place front edge values into list
	for i in range(len(position_array)):
		for j in range(edge_pixels):
			new_list.append(intensity_array[j])

	# Place values of interest into smoothing algorithm
	for i in range(len(position_array)):
		for j in range(edge_pixels, len(intensity_array)-edge_pixels):

			# Slice the array around the pixels of interest
			slice_array = intensity_array[j-edge_pixels:j+edge_pixels+1]

			# Average the sliced array into one value
			for k in range(0, len(slice_array)):
				current_sum = current_sum + slice_array[k]
			average = current_sum / smooth_factor

			# Place averaged value into output list
			new_list.append(average)

			# Reset sum and average
			current_sum = 0
			average = 0

	# Place rear edge values into list
	for i in range(len(position_array)):
		for j in range(edge_pixels):
			new_list.append(intensity_array[len(intensity_array)-edge_pixels+j])

	# Convert list into array
	intensity_array = np.asarray(new_list)

	# Return smoothed intensity array
	return intensity_array

def wavel_to_pixel(wavelength):
	""" This function accepts a wavelength value and returns the corresponding pixel value """
 
	A0 = 348.4316445
	A1 = 0.069763835
	A2 = -2.98682E-6
	B0 = A0-((A1**2)/(4*A2))
	B1 = (A1)/(2*A2)

	# Calculation of minimum/maximum pixel number
	pixel = int(math.floor(-(math.sqrt(((wavelength-B0)/A2)))-B1))
     
	return pixel

def CropData(wavelength_array, intensity_array, spectrum_array):
	""" This function accepts a wavelength and intensity array and returns a sliced wavelength and intensity array """

	# Specify minimum wavelength
	print
	min_wavelength = input("Select minimum wavelength above 348.9 nm and below 561.7 nm: ")
	while min_wavelength < 348.9 or min_wavelength > 561.7:
		min_wavelength = input("ERROR! Minimum wavelength must be above 348.9 nm and below 561.7 nm: ")

	# Specify maximum wavelength
	print
	max_wavelength = input("Select maximum wavelength above 348.9 nm and below 561.7 nm: ")
	while max_wavelength < 348.9 or max_wavelength > 561.7:
		max_wavelength = input("ERROR! Maximum wavelength must be above 348.9 nm and below 561.7 nm: ")

	# Check that minimum and maximum are correct with respect to each other
	while max_wavelength <= min_wavelength:
		max_wavelength = input("ERROR! Maximum wavelength must be greater than minimum wavelength. Select another: ")

	# Calculation of minimum/maximum pixel number
	P_min = wavel_to_pixel(min_wavelength)
	P_max = wavel_to_pixel(max_wavelength)



	# Transpose wavelength array for slicing
	wavelength_array = np.transpose(wavelength_array)

	# Slice arrays
	intensity_array = intensity_array[P_min:P_max]
	wavelength_array = wavelength_array[P_min:P_max]
 	spectrum_array = spectrum_array[P_min:P_max]

	# Transpose wavelength array back to original transposition
	wavelength_array = np.transpose(wavelength_array)

	return wavelength_array, intensity_array, P_min, spectrum_array
########################

################## Read in data ##################
print('Please select the A File.')
user_input1 = tkFileDialog.askopenfile()
print('Please select the B File.')
user_input2 = tkFileDialog.askopenfile()

raw_data = np.loadtxt(user_input1)

wocp = np.loadtxt(user_input2)
wocp = np.transpose(wocp)
NormSpec = wocp[0] #This is the spectrum we're normalizing to.

m = raw_data.shape[0]
n = raw_data.shape[1]

scan_length = m - 2

DeltaInt = raw_data[0:scan_length]
wavelengths = raw_data[scan_length:scan_length+1]
positions = raw_data[scan_length+1:scan_length+2]

positions = np.transpose(positions)
positions = positions[0:scan_length]
pos=positions[scan_length-1]
posscale=pos[0]
positions = np.transpose(positions)

DeltaInt = np.transpose(DeltaInt)

lmda = int(raw_input("Select wavelength for relative position lineout: "))

pixel=wavel_to_pixel(lmda)

# Prompt user input of smoothing factor
print
print("Length of input array = " + str(len(wavelengths[0])))
smooth_factor = input("Smoothing factor: ")

# Check if smoothing factor is within reasonable bounds
while smooth_factor > len(wavelengths[0]):
	smooth_factor = input("Choose smoothing factor less than length of array: ")

# Check if smoothing factor is integer type
while smooth_factor != int(smooth_factor):
	smooth_factor = input("Choose smoothing factor that is integer type: ")
######################################################

################## Smooth data ##################
DeltaIntSm = Smooth(positions, wavelengths, DeltaInt, smooth_factor)
######################################################
print("Smoothed")

################## Smooth normalization spectrum ##################
NormSpecSm = Smooth(positions, wavelengths, NormSpec, smooth_factor)
#I just made the position_array and wavelength_array variables that I passed in
#the same as when I smoothed the data, but I don't know if this is correct.
######################################################
print("Smoothed Spectrum")

################## Crop data ##################
CroppedData = CropData(wavelengths, DeltaIntSm, NormSpecSm)
wavelengthsCr = CroppedData[0]
DeltaIntSmCr = CroppedData[1]
MinPixel = CroppedData[2]
NormSpecSmCr = CroppedData[3]
######################################################
print("Cropped")

################## Normalize data ##################
DeltaIntSmCrNorm = np.transpose(DeltaIntSmCr)

for i in range(len(DeltaIntSmCrNorm)):
	DeltaIntSmCrNorm[i] = DeltaIntSmCrNorm[i] / NormSpecSmCr

DeltaIntNorm = np.transpose(DeltaIntSmCrNorm)
######################################################
print("Normalized")


################## Plot data ##################
xmin=-1 #positions[0].min()
xmax=1 #positions[0].max()

ymin=wavelengthsCr[0].min()
ymax=wavelengthsCr[0].max()


fig1 = plt.figure()
ax1 = fig1.add_subplot(221)
im1 = ax1.imshow(DeltaIntSmCr[:,0:199], vmin=DeltaIntSmCr.min(), vmax=DeltaIntSmCr.max(), interpolation="hanning",
     origin='lower', extent=[xmin, xmax, ymin, ymax])
ax1.set_aspect((xmax-xmin)/(ymax-ymin))
plt.colorbar(im1)
plt.xlabel("Relative position (um)")
plt.ylabel("Wavelength (nm)")

ax2 = fig1.add_subplot(222)
im2 = ax2.imshow(DeltaIntNorm[:,0:199], vmin=DeltaIntNorm.min(), vmax=DeltaIntNorm.max(), interpolation="hanning",
     origin='lower', extent=[xmin, xmax, ymin, ymax])
ax2.set_aspect((xmax-xmin)/(ymax-ymin))
plt.colorbar(im2)
plt.xlabel("Relative position (um)")
plt.ylabel("Wavelength (nm)")

ax3 = fig1.add_subplot(223)
plt.plot(positions[0], DeltaIntNorm[pixel-MinPixel])
plt.xlabel("Relative position (um)")
plt.ylabel("Intensity (arb. units)")

ax4 = fig1.add_subplot(224)
plt.plot(wavelengthsCr[0], NormSpecSmCr)
plt.xlabel("Relative position (um)")
plt.ylabel("Intensity (arb. units)")
plt.show()
######################################################