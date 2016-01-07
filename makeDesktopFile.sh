#!/bin/bash
# This creates a desktop file based on current directory.

# Remove any old versions.
rm ether-price-indicator.desktop

# Use current directory as directory with python file if no directory given.
if [ -z "$1" ]
  then
    currDir=$(pwd)
else
  currDir=$1
fi

# Create desktop file.
cp EtherIndicator.desktop ether-price-indicator.desktop
echo "Exec="$currDir"/ether-price-indicator.py" >> ether-price-indicator.desktop
echo "Icon="$currDir"/res/ethericon.png" >> ether-price-indicator.desktop
echo "Categories=Internet;" >> ether-price-indicator.desktop
echo "Type=Application" >> ether-price-indicator.desktop
echo "Terminal=false" >> ether-price-indicator.desktop
echo "X-Ayatana-Desktop-Shortcuts=Regular;" >> ether-price-indicator.desktop
echo "Name[en_US]=Ether Indicator" >> ether-price-indicator.desktop
echo " " >> ether-price-indicator.desktop