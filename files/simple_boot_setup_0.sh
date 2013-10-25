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

#disable_after_first_run(){
#  if [[ $CALLED_BY == init && $0 == /boot/simple_boot_setup.sh ]]; then
#    mv $0 $0.removed_after_first_run
#    update-rc.d simple_boot_setup remove
#  fi
#}

echo "START" > $LOG

disable_after_first_run(){
  if [[ $0 == /boot/simple_boot_setup_0.sh ]]; then
    echo   "$0: FIRST RUN. DISABLING" >> $LOG
    logger "$0: FIRST RUN. DISABLING"
    mv $0 $0.removed_after_first_run
    #update-rc.d simple_boot_setup remove
  fi
}

####
##   This is where you put your setup code.
####

	SRC=/boot/files

    ## ## Here are some examples of things you might do...
    ##
    ## ## Remove unneeded packages
    echo   "$0: UNINSTALLING" >> $LOG
    logger "$0: UNINSTALLING"
    #apt-get -y remove --purge xserver-common x11-common gnome-icon-theme gnome-themes-standard penguinspuzzle
    #apt-get -y remove --purge desktop-base desktop-file-utils hicolor-icon-theme raspberrypi-artwork omxplayer
    #apt-get -y autoremove
    echo   "$0: UNINSTALLED"  >> $LOG
    logger "$0: UNINSTALLED"

    ##
    ## ## Install a package that will automatically mount & unmount USB drives
    #echo   "$0: INSTALLING"   >> $LOG
    #logger "$0: INSTALLING"
    #apt-get install usbmount
    #echo   "$0: INSTALLED"    >> $LOG
    #logger "$0: INSTALLED"
    ##
    ## ## Setup wifi so you can connect to a secured network without a keyboard & monitor!




    echo   "$0: Interfaces"    >> $LOG
    logger "$0: Interfaces"
	#http://shallowsky.com/blog/hardware/raspberry-pi-without-monitor.html
	#http://www.howtogeek.com/167425/how-to-setup-wi-fi-on-your-raspberry-pi-via-the-command-line/
	#http://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/setting-up-wifi-with-occidentalis
	# ATTENTION: NETWORK IP AND WIRELESS PASSWORDS SHOULD BE PASSED IN THIS FILE
	FIL=$SRC/interfaces
	DST=/etc/network/interfaces
	if [ -e $FIL ]; then
		if [ ! -e "$DST.bak" ]; then
			mv $DST $DST.bak
		fi
		cp $FIL $DST
	fi



    echo   "$0: DNS"    >> $LOG
    logger "$0: DNS"
	FIL=$SRC/resolv.conf
	DST=/etc/resolv.conf
	if [ -e $FIL ]; then
		if [ ! -e "$DST.bak" ]; then
			mv $DST $DST.bak
		fi
		cp $FIL $DST
	fi
	
	
    ##
    ## ## Add your SSH pub key
    ## (umask 077; mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys)
    ## chown -R $(id -u pi):$(id -g pi) ~/.ssh
    ## curl -sL https://raw.github.com/RichardBronosky/dotfiles/master/.ssh/authorized_keys >> ~/.ssh/authorized_keys
    ##
    ## ## fake completing the raspi-config
    ## sed '/do_finish()/,/^$/!d' /usr/bin/raspi-config | sed -e '1i ASK_TO_REBOOT=0;' -e '$a do_finish' | bash

	FIL=$SRC/authorized_keys
	FOL=/home/pi/.ssh
	DST=$FOL/authorized_keys
	(umask 077; mkdir -p $FOL)
	if [ -e $FIL ]; then
		if [ ! -e "$DST.bak" ]; then
			mv $DST $DST.bak
		fi
		cp $FIL $DST
	fi
	chown -R $(id -u pi):$(id -g pi) $FOL
	chmod 600 $FOL
	
	FIL=$SRC/id_rsa
	FOL=/home/pi/.ssh
	DST=$FOL/id_rsa
	(umask 077; mkdir -p $FOL)
	if [ -e $FIL ]; then
		if [ ! -e "$DST.bak" ]; then
			mv $DST $DST.bak
		fi
		cp $FIL $DST
	fi
	chown -R $(id -u pi):$(id -g pi) $FOL
	chmod 600 $FOL
	
	FIL=$SRC/id_rsa.pub
	FOL=/home/pi/.ssh
	DST=$FOL/id_rsa.pub
	(umask 077; mkdir -p $FOL)
	if [ -e $FIL ]; then
		if [ ! -e "$DST.bak" ]; then
			mv $DST $DST.bak
		fi
		cp $FIL $DST
	fi
	chown -R $(id -u pi):$(id -g pi) $FOL
	chmod 600 $FOL
	
	
	#TODO:
	#	CHANGE HOSTNAME
	#	CHAGE PASSWORD (OR NOT)
	#	TURN ON OVERCLOCK
	#	TURN OFF VIDEO
	#	CHANGE GPU MEMORY
	
# If you want this script to remain and run at ever boot comment out the next line.
#disable_after_first_run

echo "END" >> $LOG
