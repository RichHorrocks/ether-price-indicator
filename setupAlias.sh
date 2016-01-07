#!/bin/bash
# Adds "ether-indicator" command to run the indicator.
# Use current directory as directory with python file if no directory given.
if [ -z "$1" ]
  then
    currDir=$(pwd)
	currFile=""$currFile"/ether-price-indicator.py"
else
  currFile=$1
fi

if grep -q ether-indicator= ~/.bashrc; then
	exit 1
fi
echo " " >> ~/.bashrc
echo "#" >> ~/.bashrc
echo "#     Ether-Indicator" >> ~/.bashrc
echo "#" >> ~/.bashrc
echo "alias ether-indicator='python "$currFile"'" >> ~/.bashrc
