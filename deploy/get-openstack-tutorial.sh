#!/bin/bash

START_TIME=$SECONDS

#SCENARIO_NAME=openstack_tutorial-mitaka_4n_classic_ovs-v05
#SCENARIO_NAME=openstack_lab-ocata_4n_classic_ovs-v04
#SCENARIO_NAME=openstack_lab-stein_4n_classic_ovs-v06
SCENARIO_NAME=openstack_lab-antelope_4n_classic_ovs-v03
WORKDIR=/mnt/tmp

cd $WORKDIR

if [ -e ${SCENARIO_NAME} ]; then 
    echo "--"
    echo "-- A previous copy of Openstack tutorial scenario found."
    echo "-- Moving it to /mnt/tmp/old directory"
    mkdir -p ${WORKDIR}/old
    mv ${SCENARIO_NAME} ${WORKDIR}/old/${SCENARIO_NAME}-$(date +%S%N)
    for f in $( ls ${SCENARIO_NAME}*.tgz ); do
        mv $f ${WORKDIR}/old/$f-$(date +%S%N)
    done 
fi

if [ -f "/lab/cnvr/repo/${SCENARIO_NAME}-with-rootfs.tgz" ]; then
    echo "--"
    echo "-- Copying ${SCENARIO_NAME}-with-rootfs.tgz file..."
    #time rsync -ah --progress /mnt/vnx/repo/openstack/${SCENARIO_NAME}-with-rootfs.tgz .
    time rsync -ah --progress /lab/cnvr/repo/${SCENARIO_NAME}-with-rootfs.tgz .
else
    echo "--"
    echo "-- Dowloading ${SCENARIO_NAME}-with-rootfs.tgz file..."
    time wget http://idefix.dit.upm.es/download/cnvr/${SCENARIO_NAME}-with-rootfs.tgz
fi

if [ ! $? -eq 0 ]; then
    echo "--"
    echo "-- ERROR: cannot get ${SCENARIO_NAME}-with-rootfs.tgz file...exiting"
    echo "--"
    exit 1
fi

echo "--"
echo "-- Unpacking ${SCENARIO_NAME}-with-rootfs.tgz file..."
sudo vnx --unpack ${SCENARIO_NAME}-with-rootfs.tgz

ELAPSED_TIME=$(($SECONDS - $START_TIME))
echo "--"
echo "-- Openstack tutorial scenario copied and unpacked in $ELAPSED_TIME seconds"
echo "--"