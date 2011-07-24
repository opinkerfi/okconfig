<?php
#
# Copyright (c) 2006-2008 Joerg Linge (http://www.pnp4nagios.org)
# Template for check_disk
# $Id: check_disk.php 631 2009-05-01 12:20:53Z Le_Loup $
#
#
#
#
#
$colors = array("#00FF00", "#FF0000");
$color = array_shift($colors);
foreach ($DS as $i) {
	$name = str_replace("__", ":", $NAME[$i]);
	$opt[$i] = "-A --vertical-label $UNIT[1] -l0  --title \"Disk Usage on $name on $hostname\" ";
	$name = str_replace(":", "\\:", $name);
	$def[$i] = "";

	$def[$i] .=  "DEF:var1=$rrdfile:$DS[$i]:AVERAGE " ;
	$def[$i] .= "AREA:var1$color:\"$name \\n\" " ;
	$def[$i] .= "GPRINT:var1:LAST:\"\t%6.2lf last\" " ;
	$def[$i] .= "GPRINT:var1:AVERAGE:\"%6.2lf avg\" " ;
	$def[$i] .= "GPRINT:var1:MAX:\"%6.2lf max\\n\" " ;
}

?>
