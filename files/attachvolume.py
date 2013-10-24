#!/bin/python
import os, sys
import time
import datetime
import subprocess
import argparse
import re
import shutil

#DEFAULT_FS_TYPE='ext4'
#DEFAULT_FS_OPTIONS='rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro'


parser = argparse.ArgumentParser(description='Attach Disks')
parser.add_argument('-c', '--config-file', dest='config'     , default=None , action='store'      , metavar='CONFIG'     , type=str, nargs='?', help='config file')
parser.add_argument('-n', '--dry-run'    , dest='real'       , default=True , action='store_false',                                             help='dry run'    )

args     = parser.parse_args()
respaces = re.compile('\s+')
for_real = args.real

def main():
	fstab, setup = loadconfig()

	print "FSTAB", fstab
	print "SETUP", setup

	for mount in sorted( setup ):
		print "ATTACHING", mount

		if setup[mount] is None: 
			print "ATTACHING", mount, "EMPTY. SKIPPING"
			continue

		if not for_real: 
			print "ATTACHING", mount, "NOT FOR REAL. NOT ATTACHING. SKIPPING"
			continue


	for mount in sorted( setup ):
		if setup[mount] is None: continue
		mountvol(setup[mount], fstab)

	for mount in sorted( setup ):
		if setup[mount] is None: continue
		mountfolder(setup[mount], fstab)



def mountfolder(vars, fstab):
	src_folder = vars['src_folder']
	dst_folder = vars['dst_folder']
	
	if not os.path.exitsts( src_folder ):
		print "SOURCE FOLDER", src_folder, "DOES NOT EXISTS"
		sys.exit(1)
	
	if not os.path.exitsts( dst_folder ):
		print "DESTINATION FOLDER", dst_folder, "DOES NOT EXISTS. CREATING"
		os.makedirs( dst_folder )
	
	mountDev(   dev, mount, opts="" )
	addToFstab( dev, mount, fstab, fstype, fsopt )


def mountvol(vars, fstab):
	dev        = vars['device']
	mount      = vars['mount' ]
	fstype     = vars['fstype']
	fsopt      = vars['fsopt' ]
	
	print "MOUNTING"
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"FS TYPE", fstype,"FS OPT", fsopt,'SRC FOLDER',src_folder,'DST FOLDER',dst_folder

	mountDev(   dev, mount                       )
	addToFstab( dev, mount, fstab, fstype, fsopt )


def mountDev( dev, mount, opts="" ):
	mounted    = subprocess.check_output(['mount'])
	if not mount in mounted:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING"

		if not os.path.exists( mount ):
			print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: CREATING DIR"
			os.makedirs( mount )

		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING"

		res1 = subprocess.call( [ 'mount', opts, dev, mount ] )

		if res1 != 0:
			print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING :: FAILED", res1
			sys.exit(1)

		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING :: success"

	else:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ALREADY MOUNTED. SKIPPING"


def addToFstab( dev, mount, fstab, fstype, fsopt ):
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB"
	if dev not in fstab:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB"
		ts  = time.time()
		st  = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
		bkp = "/tmp/fstab-" + st
		shutil.copy( "/etc/fstab", bkp )
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB :: BKP", bkp

		#dev, tgt, type, conf, st, nd
		#rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro
		fscmd= "\n\n#%s\n%s\t%s\t%s\t%s\t%s" % ( st, dev, mount, fstype, fsopt, '0\t0' )
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB ::", fscmd
		open( '/etc/fstab', 'a+' ).write( fscmd )
	else:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: ALREADY IN FSTAB"


#TODO: add to fstab
#if [[ -z `grep $EC2_EXTERNAL_CONFIG_SRC /etc/fstab` ]]; then
#    echo "adding external $EC2_EXTERNAL_CONFIG_SRC to fstab"
#    #http://blog.smartlogicsolutions.com/2009/06/04/mount-options-to-improve-ext4-file-system-performance/
#    #gid 19 = floppy
#    #data=ordered
  
#    echo "$EC2_EXTERNAL_CONFIG_SRC   $EC2_EXTERNAL_CONFIG_DST        ext4    rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro    0 0" >> /etc/fstab
  
#  else
#    echo "external already in fstab"
#  fi


def loadconfig():
	setup  = {}
	fstab  = {}

	config = args.config
	
	if config is None:
		#no config file
		print "no config file"
		parser.print_help()
		sys.exit(1)
	
	if len(config) == 0:
		print "empty config file"
		sys.exit(1)

	if not os.path.exists(config):
		print "config file %s does not exists" % config
		sys.exit(1)

	with open('/etc/fstab', 'r') as ftb:
		for line in ftb:
			line         =       line.strip()
			if len(line) ==   0: continue
			if line[0]   == "#": continue
			cols = respaces.split( line )
			print "FSTAB COLS", cols
			#dev, tgt, type, conf, st, nd
			dev   = cols[0]
			mount = cols[1]
			fstab[ dev ] = mount

	repeats = []
	devs    = {}
	with open(config, 'r') as cfg:
		for line in cfg:
			line         =       line.strip()
			if len(line) == 0  : continue
			if line[0]   == "#": continue

			cols = line.split(';')

			if len( cols ) != 6:
				print "wrong number of colums. %d. should be 7" % len(cols)
				print "/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder"
				print line
				sys.exit( 1 )

			print "CONFIG COLS", cols
			#/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder
			device     = cols[1]
			mount      = cols[2]
			fstype     = cols[3]
			fsopt      = cols[4]
			src_folder = cols[5]
			dst_folder = cols[6]

			# converting to None
			if len(device    ) == 0: device     = None
			if len(mount     ) == 0: mount      = None
			if len(fstype    ) == 0: fstype     = None
			if len(fsopt     ) == 0: fsopt      = None
			if len(src_folder) == 0: src_folder = None
			if len(dst_folder) == 0: dst_folder = None

			# checking compulsory
			if device is None:
				print "no device defined in config file"
				parser.print_help()
				sys.exit(1)

			if mount is None:
				print "no mount defined in config file"
				parser.print_help()
				sys.exit(1)

			if fstype is None:
				print "no fs type defined in config file. using default", DEFAULT_FS_TYPE
				fstype = DEFAULT_FS_TYPE

			if fsopt is None:
				print "no fs mount options defined in config file. using default", DEFAULT_FS_OPTIONS
				fsopt = DEFAULT_FS_OPTIONS

			if src_folder is None:
				print "no source folder defined in config file"
				parser.print_help()
				sys.exit(1)

			if dst_folder is None:
				print "no destination folder defined in config file"
				parser.print_help()
				sys.exit(1)


			# check if repeated
			if mount in setup:
				print "repeated destination folder", dst_folder
				print line
				print setup
				sys.exit( 1 )
				
			if dst_folder in repeats:
				print "repeated destination folder", dst_folder
				print line
				print setup
				sys.exit( 1 )
			else:
				repears.append( dst_folder )

			if (mount, src_folder) in repeats:
				print "repeated source folder", mount, dst_folder
				print line
				print setup
				sys.exit( 1 )
			else:
				repeats.append( (mount, src_folder) )

			if device in devs:
				if devs[device] != mount:
					print "device %s already setup but in a different mounting point: %s != %s" % (device, devs[device], mount)
			else:
				devs[device] = mount
			
			if mount not in setup:
				setup[ mount ] = {
							'device'    : device,
							'mount'     : mount,
							'fstype'    : fstype,
							'fsopt'     : fsopt,
							'folders'   : []
						}
			else:
				setup[ mount ]['folders'].append( {
					'src_folder': os.path.join( mount, src_folder ),
					'dst_folder': dst_folder
				}


	print "CHECKING CONFIG"
	for mount in setup:
		dev = setup[mount]['device']
		if dev in fstab:
			print "CHECKING CONFIG :: DEV",dev,"IN FSTAB"
			tgt = fstab[ dev ]
			if tgt != mount:
				print "CHECKING CONFIG :: DEV",dev,"IN FSTAB. TARGETS DO NOT MATCH"
				print "  FSTAB MOUNT POINT", tgt, "DOES NOT MATCH CONFIG MOUNT POINT", tgt
			else:
				print "CHECKING CONFIG :: DEV",dev,"IN FSTAB. TARGETS MATCH",mount
		else:
			print "CHECKING CONFIG :: DEV",dev,"not IN FSTAB"

	return ( fstab, setup )



if __name__ == "__main__": main()
