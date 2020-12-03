#!/usr/bin/env python3

import os,sys,getpass,shutil

print()

if not len(sys.argv) == 4:
	print('''
   ------------------------------------------------------------------------
   This script copies data from one directory to another which can be
   cumbersome for Molcas calculations.
   The root directory is:

   /work/$USER/OpenMolcas

   The script needs three arguments: the superproject,the source directory
   and the destination directory.
   If the destination does not exist, it will be created. If it is not
   empty, you will be asked to continue.  

   Example:
   copy-molcas.py U_Salen2 HF-MB CASSCF-MB
   
   All files inside 
   
   /work/$USER/OpenMolcas/U_Salen2/HF-MB/U_Salen2
   
   will be copied into
   
   /work/$USER/OpenMolcas/U_Salen2/CASSCF-MB/U_Salen2
   ------------------------------------------------------------------------
   ''')

	print('   Exiting...')
	exit()

ROOT = '/work/'+getpass.getuser()+'/OpenMolcas'
super_project = sys.argv[1]
source_dir = ROOT+"/"+super_project+"/"+sys.argv[2]+"/"+super_project
dest_dir = ROOT+"/"+super_project+"/"+sys.argv[3]+"/"+super_project

assert os.path.isdir(source_dir), "The source directory "+source_dir+" does not exist! Exiting..."

print("   I found the following files and directories to copy:")
print("-"*40)

for line in os.listdir(source_dir):
	if os.path.isdir(source_dir+"/"+line):
		print("   "+line+"  <---- is a directory and will not be copied!")
	else:
		print("   "+line)

print("-"*40)

print()
print("   DESTINATION: "+dest_dir)

if os.path.isdir(dest_dir):
	if os.listdir(dest_dir) == []:
		print("   DESTINATION does exist and is empty.")

	else:
		print("   DESTINATION does exist and contains:")
		print("-"*40)
		for line in os.listdir(dest_dir):
			print("   "+line)
		print("-"*40)
		print("   EXISTING FILES WILL BE OVERWRITTEN.")
else:
	print("   DESTINATION does not exist!")

print()

answer = input("   Everything fine? (yes = Enter, no = any key)"+"\n")
print()

if answer is "":
	if not os.path.isdir(dest_dir):
		os.makedirs(dest_dir)
		print("   The destination directory is created...")
	for line in os.listdir(source_dir):
		file = source_dir+"/"+line
		if os.path.isdir(file):
			continue
		else:
			shutil.copy(file,dest_dir)
	print("   Files are copied. Done!")
else:
	print("   Nothing was copied. Done!")

quit()
