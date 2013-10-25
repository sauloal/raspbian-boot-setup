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

echo "START" > $LOG

if [[ -e "/boot/files/simple_boot_setup_0.sh" ]]; then
	echo   "$0: running simple_boot_setup_0.sh"       >>       $LOG
	logger "$0: running simple_boot_setup_0.sh"
	/bin/bash /boot/files/simple_boot_setup_0.sh 2>&1 | tee -a $LOG
fi

if [[ -e "/boot/files/simple_boot_setup_1.sh" ]]; then
	echo   "$0: running simple_boot_setup_1.sh"       >>       $LOG
	logger "$0: running simple_boot_setup_1.sh"
	/bin/bash /boot/files/simple_boot_setup_1.sh 2>&1 | tee -a $LOG
fi

echo "END" >> $LOG
