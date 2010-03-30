<?php
#
# Template for check_swap
# Copyright (c) 2006-2008 Joerg Linge (http://www.pnp4nagios.org)
# $Id: check_swap.php 631 2009-05-01 12:20:53Z Le_Loup $
#
#
# RRDtool Options
#
#
# Graphen Definitions
$name = $NAME[1];
$name = str_replace("_", " ", $name);

$opt[1] = "-X 0 --vertical-label Units -l 0 -r --title \"Counter $name on $hostname\" ";


$def[1] =  "DEF:var1=$rrdfile:$DS[1]:AVERAGE " ;
$def[1] .=  "CDEF:sp1=var1,100,/,12,* " ;
$def[1] .=  "CDEF:sp2=var1,100,/,22,* " ;
$def[1] .=  "CDEF:sp3=var1,100,/,30,* " ;
$def[1] .=  "CDEF:sp4=var1,100,/,40,* " ;
$def[1] .=  "CDEF:sp5=var1,100,/,50,* " ;
$def[1] .=  "CDEF:sp6=var1,100,/,60,* " ;
$def[1] .=  "CDEF:sp7=var1,100,/,70,* " ;
$def[1] .=  "CDEF:sp8=var1,100,/,80,* " ;



$def[1] .= "AREA:var1#FF5C00:\"$name \\n\" " ;
$def[1] .= "AREA:sp8#FF7C00: " ;
$def[1] .= "AREA:sp7#FF8C00: " ;
$def[1] .= "AREA:sp6#FF9C00: " ;
$def[1] .= "AREA:sp5#FFAC00: " ;
$def[1] .= "AREA:sp4#FFBC00: " ;
$def[1] .= "AREA:sp3#FFCC00: " ;
$def[1] .= "AREA:sp2#FFDC00: " ;
$def[1] .= "AREA:sp1#FFEC00: " ;


#$def[1] = "DEF:var1=$rrdfile:$DS[1]:AVERAGE "; 
#$def[1] .= "AREA:var1#44ff44:\"$name\\n\" "; 
#$def[1] .= "LINE1:var1#00ff00: "; 
$def[1] .= "GPRINT:var1:LAST:\"\t%6.2lf $UNIT[1] Last \" ";
$def[1] .= "GPRINT:var1:MAX:\"\t%6.2lf Max\" ";
$def[1] .= "GPRINT:var1:AVERAGE:\"\t%6.2lf $UNIT[1] Average\" ";
?>
