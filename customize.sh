#!/bin/bash

. config 

if [ -z "$4" ]
then
	echo "Usage: $0 <name> <instrument_nr> <city> <country_nr>"
	exit 1
fi


if [ ! -d $MOUNTPOINT ]
then
	mkdir -p $MOUNTPOINT
fi

TIMEZONE="Europe/Berlin"

mount -o loop,offset=4194304 $IMAGE $MOUNTPOINT

echo $TIMEZONE > $MOUNTPOINT/payload/etc/timezone

NAME_B64=$(echo -n $1 |base64)
INSTRUMENT=$2
CITY_B64=$(echo -n $3 |base64)
COUNTRY=$4

sed -e "s/##NAME_B64##/$NAME_B64/;s/##INSTRUMENT##/$INSTRUMENT/;s/##COUNTRY##/$COUNTRY/;s/##CITY_B64##/$CITY_B64/" templates/Jamulus.ini > $MOUNTPOINT/payload/home/pi/.config/Jamulus/Jamulus.ini

echo << EOF > $MOUNTPOINT/payload/home/pi/.config/Jamulus/jamulus_start.conf
JAMULUS_AUTOSTART=$JAMULUS_AUTOSTART
JAMULUS_TIMEOUT=$JAMULUS_TIMEOUT
MASTER_LEVEL="80%"
CAPTURE_LEVEL="80%"
AJ_SNAPSHOT=ajs-jamulus-stereo.xml
JAMULUS_SERVER=$JAMULUS_SERVER
EOF

umount $MOUNTPOINT
