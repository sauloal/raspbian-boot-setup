#!/bin/bash
#
# /boot/simple_boot_setup.sh
#
# This script is executed by /etc/init.d/simple_boot_setup
#
# By default this script does nothing, and removes itself after the
# first run when called by /etc/init.d/simple_boot_setup

# This setting will cause this script to exit if there are any errors.
set -ue

DATESTR=`date +%Y%m%d_%H%M%S`
LOG=$0.$DATESTR.log


#disable video
#/opt/vc/bin/tvservice --off

echo "START" > $LOG

SRC=/boot/files

FIL=$SRC/disk
if [ -e $FIL ]; then
	python $SRC/attach_devices.py -c $FIL
fi

echo "END" >> $LOG
