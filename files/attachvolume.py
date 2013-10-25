#!/bin/python
import os, sys
import time
import datetime
import subprocess
import re
import shutil
from pprint import pprint as pp

DEFAULT_FS_TYPE='auto'
DEFAULT_FS_OPTIONS='defaults'

#DEFAULT_FS_TYPE='ext4'
#DEFAULT_FS_OPTIONS='rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro'

debug = True

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



def mountFolder(cfg, fstab):
	src_folder = cfg['src_folder']
	dst_folder = cfg['dst_folder']
	fstype     = 'none'
	fsopt      = 'bind'
	fsoptCmd   = '--bind -o ' + fsopt

	
	if not os.path.exists( src_folder ):
		print "    SOURCE FOLDER", src_folder, "DOES NOT EXISTS"
		if for_real:
			sys.exit(1)
	
	if not os.path.exists( dst_folder ):
		print "    DESTINATION FOLDER", dst_folder, "DOES NOT EXISTS. CREATING"
		if for_real:
			os.makedirs( dst_folder )
	
	print
	mountCmd(   src_folder, dst_folder, opts=fsoptCmd )
	print
	addToFstab( src_folder, dst_folder, fstab, fstype, fsopt )


def mountDev(cfg, fstab):
	dev        = cfg['device']
	mount      = cfg['mount' ]
	fstype     = cfg['fstype']
	fsopt      = cfg['fsopt' ]
	fsoptCmd   = '-o ' + fsopt
	
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount
	print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"FS TYPE", fstype,"FS OPT", fsopt

	mountCmd(   dev, mount, opts=fsoptCmd, fstype=fstype )
	addToFstab( dev, mount, fstab, fstype, fsopt         )


def mountCmd( dev, mount, opts="", fstype="" ):
	if pyver == '2.7':
		mounted    = subprocess.check_output(['mount'])
	else:
		mounted    = subprocess.Popen(['mount'], stdout=subprocess.PIPE).stdout
		
	if fstype != '':
		fstype = '-t '+fstype
		
	if not mount in mounted:
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING"

		if not os.path.exists( mount ):
			print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: CREATING DIR"
			print "L"*100
			print "CREATING MOUNT DIR", mount
			if for_real:
				os.makedirs( mount )
			print "T"*100 + "\n\n"


		cmd = [ 'mount', fstype, opts, dev, mount ]
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"MOUNTING :: MOUNTING :: RUNNING"
		print "L"*100
		print "CALLING MOUNT",cmd
		if for_real:
			res1 = subprocess.call( cmd )
		else:
			res1 = 0
		print "T"*100 + "\n\n"


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
		
		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB :: BKP"
		print "L"*100
		print "MAKING BACKUP OF FSTAB TO", bkp
		if for_real:
			shutil.copy( "/etc/fstab", bkp )
		print "T"*100 + "\n\n"


		#dev, tgt, type, conf, st, nd
		#rw,user,auto,noatime,exec,relatime,seclabel,data=writeback,barrier=0,nobh,errors=remount-ro
		fscmd= "\n\n#%s\n%s\t%s\t%s\t%s\t%s" % ( st, dev, mount, fstype, fsopt, '0\t0' )
		

		print "MOUNTING :: DEV", dev,"MOUNT POINT",mount,"ADDING TO FSTAB :: NOT IN FSTAB :: APPENDING"
		print "L"*100
		print "APPENDING TO FSTAB"
		print fscmd
		if for_real:
			open( '/etc/fstab', 'a+' ).write( fscmd )
		print "T"*100 + "\n\n"

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

			if len( cols ) != 6:
				print "wrong number of colums. %d. should be 7" % len(cols)
				print "/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder"
				print line
				sys.exit( 1 )

			print "  CONFIG COLS", cols
			#/dev/disk/by-id	mount_point	fs_type	fs_options	src_folder	dst_folder
			device     = cols[0]
			mount      = cols[1]
			fstype     = cols[2]
			fsopt      = cols[3]
			src_folder = cols[4]
			dst_folder = cols[5]

			# converting to None
			if len(device    ) == 0: device     = None
			if len(mount     ) == 0: mount      = None
			if len(fstype    ) == 0: fstype     = None
			if len(fsopt     ) == 0: fsopt      = None
			if len(src_folder) == 0: src_folder = None
			if len(dst_folder) == 0: dst_folder = None

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

			if dst_folder is None:
				print "    no destination folder defined in config file"
				parser.print_help()
				sys.exit(1)


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
							'device'    : device,
							'mount'     : mount,
							'fstype'    : fstype,
							'fsopt'     : fsopt,
							'folders'   : [
								{
									'src_folder': os.path.join( mount, src_folder ),
									'dst_folder': dst_folder
								}
							]
						}
			else:
				setup[ mount ]['folders'].append( {
						'src_folder': os.path.join( mount, src_folder ),
						'dst_folder': dst_folder
					}
				)
	print "CONFIG LOADED\n\n"


	print "CHECKING CONFIG"
	for mount in setup:
		dev = setup[mount]['device']
		if dev in fstab:
			print "  DEV",dev,"IN FSTAB"
			tgt = fstab[ dev ]
			if tgt != mount:
				print "  DEV",dev,"IN FSTAB. TARGETS DO NOT MATCH"
				print "    FSTAB MOUNT POINT", tgt, "DOES NOT MATCH CONFIG MOUNT POINT", tgt
			else:
				print "  DEV",dev,"IN FSTAB. TARGETS MATCH",mount
		else:
			print "  DEV",dev,"not IN FSTAB"

	print "CONFIG CHECKED\n\n"
	return ( fstab, setup )



if __name__ == "__main__": main()

