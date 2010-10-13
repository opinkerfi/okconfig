#!/bin/sh

CONTACTPAGER=$1


/usr/bin/smssend "$CONTACTPAGER" "Nagios
$2
$3
$4
$5
$6
$7
$8
$9"

