#!/bin/bash

input=$1
superproject=$2
project=$3


if [ -z "$input" ] || [ -z $superproject ] || [ -z "$project" ]; then
   echo
   echo "   Usage: molcas.sh <input> <superproject> <project>"
   echo
   echo "          <input>: Input-File and also name for the .err and .log file"
   echo "   <superproject>: The name of the higher-level project, e.g. the molecule name"
   echo "        <project>: The name of the specific project, e.g. the calculation method"
   echo 
   echo "   Why 2 project names, you ask?"
   echo
   echo "   The output files will be named <superproject>.RasOrb and such. But the scratch-directory will be:"
   echo
   echo "   /work/$USER/OpenMolcas/<superproject>/<project>/<superproject>"
   echo
   echo "   Thus all output files will have the same name, but different directories. I don't like the"
   echo "   last <superproject> directory, but that's Molcas!"
   echo
   echo "   Exiting..."
   exit 1
fi

tmp=/work/$USER/OpenMolcas/$superproject/$project

mkdir -p $tmp

CurrDir=$(pwd)

export MOLCAS=/usr/local/molcas
export MOLCAST_HOST=$(hostname)
export MOLCAS_PROJECT=$superproject
export MOLCAS_MEM=20000
export MOLCAS_WORKDIR=$tmp

if [ ! -f "$CurrDir/SCRATCH" ] && [ ! -L "$CurrDir/SCRATCH" ]; then
   ln -s $tmp/$superproject $CurrDir/SCRATCH
fi

while true; do
   echo "How many processors?"
   read n_procs
   if [ "$n_procs" != "" ] ; then
      export OMP_NUM_THREADS=$n_procs
      break
   fi
done


nohup pymolcas -b 1 -f $CurrDir/$input &
