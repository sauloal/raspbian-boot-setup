NAM=simple_boot_setup
DST=/etc/init.d/$NAM
LNK=files/S10$NAM
SRC=/boot/$LNK
cp $SRC $DST
ln -s $DST /etc/rcS.d/$LNK
#ln -s $DST /etc/rc2.d/$LNK
#ln -s $DST /etc/rc3.d/$LNK
#ln -s $DST /etc/rc4.d/$LNK
#ln -s $DST /etc/rc5.d/$LNK
update-rc.d $NAM enable S
