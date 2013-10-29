#!/bin/python
"""
Saulo Alves - 2013
Given a config file, read the disk ID and the desired folders.

- Check if disks are already mounted
  + If not mounts the disks
- Adds the disk to fstab (if requested, creating a backup in /tmp)
  if not already there, confirming if destination is still the same

- Check if folders are already mounted
  + Bind mounts the folders
- Add the folder to fstab (if requested, creating a backup in /tmp)
  if not already there, confirming if destination is still the same
"""

import os, sys
import time
import datetime
import subprocess
import re
import shutil
from pprint import pprint as pp

DEFAULT_FS_TYPE    = 'auto'
DEFAULT_FS_OPTIONS = 'defaults'

#DEFAULT_FS_TYPE='ext4'
#DEFAULT_FS_OPTIONS='rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro'

debug = False

vinfo = sys.version_info
print 'PYTHON', vinfo
#sys.version_info
#(2, 5, 2, 'final', 0)

args  = None
pyver = '2.6'
if vinfo[0] > 2 or (vinfo[0] == 2 and vinfo[1] >= 7): # >= 2.7
	print "2.7 using argparse"
	pyver = '2.6'
	
else: # < 2.7
	print "2.6 using optparse"


if pyver == '2.7':
	import argparse
	
	parser = argparse.ArgumentParser(description='Attach Disks')
	parser.add_argument('-c', '--config-file', dest='config'     , default=None , action='store'      , metavar='CONFIG'     , type=str, nargs='?', help='config file')
	parser.add_argument('-n', '--dry-run'    , dest='real'       , default=True , action='store_false',                                             help='dry run'    )

	args     = parser.parse_args()
else:
	import optparse
	
	parser = optparse.OptionParser(description='Attach Disks')
	parser.add_option('-c', '--config-file', dest='config'     , default=None , action='store'      , metavar='CONFIG'     , type=str, nargs=1, help='config file')
	parser.add_option('-n', '--dry-run'    , dest='real'       , default=True , action='store_false',                                           help='dry run'    )

	(args, args2) = parser.parse_args()
	
	if args.config is None:
		print "NO CONFIG FILE GIVEN"
		parser.print_help()
		sys.exit(1)	
	
respaces = re.compile('\s+')
for_real = args.real

if debug:
	for_real = False


def main():
	fstab, setup = loadconfig()

	print "FSTAB"
	pp( fstab, indent=2 )
	
	print "SETUP"
	pp( setup, indent=2 )

	for mount in sorted( setup ):
		print "MOUNTING :: DEV", mount
		if setup[mount] is None: continue
		mountDev(setup[mount], fstab)

		for folder in setup[mount]['folders']:
			print "  BINDING FOLDER", folder
			mountFolder(folder, fstab)
			print "\n"
		print "\n\n"


def mountDev(cfg, fstab):
	dev          = cfg['device']
	mount        = cfg['mount' ]
	fstype       = cfg['fstype']
	fsopt        = cfg['fsopt' ]
	addDiskFstab = cfg['addDiskFstab' ]
	fsoptCmd     = '-o ' + fsopt
	
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"FS TYPE", fstype,"FS OPT", fsopt
	
	print
	if os.path.exists( dev ):
		mountCmd(   dev, mount, opts=fsoptCmd, fstype=fstype )
		
	else:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount, 'DEVICE DOES NOT EXISTS. ADDING TO FSTAB ONLY'
	print
	
	if addDiskFstab:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount, 'ADDING TO FSTAB'
		addToFstab( dev, mount, fstab, fstype, fsopt         )
	else:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount, 'SKIPPING FSTAB'



def mountFolder(cfg, fstab):
	src_folder     = cfg['src_folder'    ]
	dst_folder     = cfg['dst_folder'    ]
	addFolderFstab = cfg['addFolderFstab']
	fstype         = 'none'
	fsopt          = 'bind'
	fsoptCmd       = '--bind -o ' + fsopt

	print "MOUNTING :: BIND SRC FOLDER", src_folder,"DST FOLDER",dst_folder
	
	if not os.path.exists( src_folder ):
		print "    SOURCE FOLDER", src_folder, "DOES NOT EXISTS"
	
	else:
		if not os.path.exists( dst_folder ):
			print "    DESTINATION FOLDER", dst_folder, "DOES NOT EXISTS. CREATING"
			if for_real:
				os.makedirs( dst_folder )
	
	print
	if os.path.exists( src_folder ):
		mountCmd(   src_folder, dst_folder, opts=fsoptCmd )
		
	else:
		print "MOUNTING :: BIND SRC FOLDER", src_folder,"DST FOLDER",dst_folder,' :: SOURCE DOES NOT EXISTS. ADDING TO FSTAB ONLY'
		print
	
	if addFolderFstab:
		print "MOUNTING :: BIND SRC FOLDER", src_folder,"DST FOLDER",dst_folder,' :: ADDING TO FSTAB'
		addToFstab( src_folder, dst_folder, fstab, fstype, fsopt )
	else:
		print "MOUNTING :: BIND SRC FOLDER", src_folder,"DST FOLDER",dst_folder,' :: SKIPPING FSTAB'


def mountCmd( dev, mount, opts="", fstype="" ):
	mounted = getMounted()

	devLnk  = dev
	if os.path.islink( dev ):
		devLnk  = os.readlink( dev )
	
	if fstype == 'auto':
		fstype = ''
	
	if fstype != '':
		fstype = '-t '+fstype
		
		
	if not (
		(mount  in mounted['mount']) or 
		(dev    in mounted['dev'  ]) or 
		(devLnk in mounted['dev'  ])):
		
		print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"MOUNTING"

		if not os.path.exists( mount ):
			print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: CREATING DIR"
			print "L"*100
			print "CREATING MOUNT DIR", mount
			if for_real:
				print "COPYING"
				os.makedirs( mount )
			print "T"*100 + "\n\n"


		cmd = 'mount %s %s %s %s' % ( fstype , opts, dev, mount )
		print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING"
		print "L"*100
		print "CALLING MOUNT",cmd
		if for_real:
			print "MOUNTING"
			res1 = subprocess.call( cmd, shell=True )
		else:
			res1 = 0
		print "T"*100 + "\n\n"


		if res1 != 0:
			print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING :: FAILED", res1
			sys.exit(1)

		print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING :: success"

	else:
		print "MOUNTING CMD :: DEV", dev,"MOUNT POINT",mount,"ALREADY MOUNTED. SKIPPING"


def getMounted():
	if pyver == '2.7':
		mounted    = subprocess.check_output(['mount'])
	else:
		mounted    = subprocess.Popen(['mount'], stdout=subprocess.PIPE).stdout.readlines()
	
	pp( mounted, indent=2 )
	
	mnt = { 'dev': [], 'mount': [] }
	for line in mounted:
		cols = line.split()
		mnt['dev'  ].append( cols[0] )
		mnt['mount'].append( cols[2] )
	
	pp( mnt, indent=2 )
	
	return mnt


def addToFstab( dev, mount, fstab, fstype, fsopt ):
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB"
	if dev not in fstab:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB"
		ts  = time.time()
		st  = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S-%f')
		bkp = "/tmp/fstab-" + st
		
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB :: BKP"
		print "L"*100
		print "MAKING BACKUP OF FSTAB TO", bkp
		if for_real:
			print "COPYING"
			shutil.copy( "/etc/fstab", bkp )
		print "T"*100 + "\n\n"


		#dev, tgt, type, conf, st, nd
		#rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro
		fscmd = "\n\n#%s\n%s\t%s\t%s\t%s\t%s" % ( st, dev, mount, fstype, fsopt, '0\t0\n' )
		

		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB :: APPENDING"
		print "L"*100
		print "APPENDING TO FSTAB"
		print fscmd
		if for_real:
			print "WRITING"
			open( '/etc/fstab', 'a' ).write( fscmd )
		print "T"*100 + "\n\n"

	else:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: ALREADY IN FSTAB"


def loadFstab():
	fstab  = {}
	
	print "LOADING FSTAB"
	
	with open('/etc/fstab', 'r') as ftb:
		for line in ftb:
			line         =       line.strip()
			if len(line) ==   0: continue
			if line[0]   == "#": continue
			cols = respaces.split( line )
			print "  FSTAB COLS", cols
			#dev, tgt, type, conf, st, nd
			dev   = cols[0]
			mount = cols[1]
			fstab[ dev ] = mount
	
	print "FSTAB LOADED\n\n"
	
	return fstab


def loadconfig():
	fstab   = loadFstab()


	print "LOADING CONFIG"
	setup  = {}

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


	repeats = []
	devs    = {}
	with open(config, 'r') as cfg:
		for line in cfg:
			line         =       line.strip()
			if len(line) == 0  : continue
			if line[0]   == "#": continue

			cols = line.split(';')

			if len( cols ) != 8:
				print "wrong number of colums. %d. should be 8" % len(cols)
				print "/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder	addDiskFstab	addFolderFstab"
				print line
				sys.exit( 1 )

			print "  CONFIG COLS", cols
			#/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder
			device         = cols[0]
			mount          = cols[1]
			fstype         = cols[2]
			fsopt          = cols[3]
			src_folder     = cols[4]
			dst_folder     = cols[5]
			addDiskFstab   = cols[6]
			addFolderFstab = cols[7]

			# converting to None
			if len(device        ) == 0: device         = None
			if len(mount         ) == 0: mount          = None
			if len(fstype        ) == 0: fstype         = None
			if len(fsopt         ) == 0: fsopt          = None
			if len(src_folder    ) == 0: src_folder     = None
			if len(dst_folder    ) == 0: dst_folder     = None
			if len(addDiskFstab  ) == 0: addDiskFstab   = None
			if len(addFolderFstab) == 0: addFolderFstab = None

			# checking compulsory
			if device is None:
				print "    no device defined in config file"
				parser.print_help()
				sys.exit(1)

			if mount is None:
				print "    no mount point defined in config file"
				parser.print_help()
				sys.exit(1)

			if fstype is None:
				print "    no fs type defined in config file. using default", DEFAULT_FS_TYPE
				fstype = DEFAULT_FS_TYPE

			if fsopt is None:
				print "    no fs mount options defined in config file. using default", DEFAULT_FS_OPTIONS
				fsopt = DEFAULT_FS_OPTIONS

			if src_folder is None:
				print "    no source folder defined in config file"
				parser.print_help()
				sys.exit(1)
			else:
				src_folder = src_folder.strip("/")

			if dst_folder is None:
				print "    no destination folder defined in config file"
				parser.print_help()
				sys.exit(1)

			if addDiskFstab in ['1', 'true', 'True', 'TRUE']:
				addDiskFstab = True
			else:
				addDiskFstab = False

			if addFolderFstab in ['1', 'true', 'True', 'TRUE']:
				addFolderFstab = True
			else:
				addFolderFstab = False
				
				

			# check if repeated
			if mount in setup:
				print "    repeated mount point folder", mount
				print line
				print setup
				sys.exit( 1 )
				
			if dst_folder in repeats:
				print "    repeated destination folder", dst_folder
				print line
				print setup
				sys.exit( 1 )
			else:
				repeats.append( dst_folder )

			if (mount, src_folder) in repeats:
				print "    repeated source folder", mount, dst_folder
				print line
				print setup
				sys.exit( 1 )
			else:
				repeats.append( (mount, src_folder) )

			if device in devs:
				if devs[device] != mount:
					print "    device %s already setup but in a different mounting point: %s != %s" % (device, devs[device], mount)
			else:
				devs[device] = mount
			
			
			
			if mount not in setup:
				setup[ mount ] = {
							'device'      : os.path.join('/dev/disk/by-id', device ),
							'mount'       : mount,
							'fstype'      : fstype,
							'fsopt'       : fsopt,
							'addDiskFstab': addDiskFstab,
							'folders'     : [
								{
									'src_folder'    : os.path.join( mount, src_folder ),
									'dst_folder'    : dst_folder,
									'addFolderFstab': addFolderFstab
								}
							]
						}
			else:
				setup[ mount ]['folders'].append( {
						'src_folder'    : os.path.join( mount, src_folder ),
						'dst_folder'    : dst_folder,
						'addFolderFstab': addFolderFstab
					}
				)
	print "CONFIG LOADED\n\n"


	print "CHECKING CONFIG"
	mountToDel = []
	for mount in setup:
		dev     = setup[mount]['device']
		devLnk  = dev
		if os.path.islink( dev ):
			devLnk  = os.readlink( dev )

		for dp in [ dev, devLnk ]:
			if dp in fstab:
				print "  DEV",dev,'as',dp,"IN FSTAB"
				tgt = fstab[ dp ]
				if tgt != mount:
					print "  DEV",dev,'AS',dp,"IN FSTAB. TARGETS DO NOT MATCH"
					print "    FSTAB MOUNT POINT", tgt, "DOES NOT MATCH CONFIG MOUNT POINT", tgt, 'IGNORING'
					mountToDel.append(mount)
				else:
					print "  DEV",dev,"IN FSTAB. TARGETS MATCH",mount
			else:
				print "  DEV",dev,"not IN FSTAB"

	for mount in mountToDel:
		setup.pop( mount )
			
	print "CONFIG CHECKED\n\n"
	return ( fstab, setup )



if __name__ == "__main__": main()

