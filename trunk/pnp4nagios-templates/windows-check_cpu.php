<?php
#
# Copyright (c) 2006-2008 Joerg Linge (http://www.pnp4nagios.org)
# Plugin: check_load
# $Id: check_load.php 627 2009-04-23 11:14:06Z pitchfork $
#
#
$opt[1] = "--vertical-label $UNIT[1] -l0  --title \"CPU Load for $hostname / $servicedesc\" ";
#
#
#
$colors = array("#0000FF", "#00FF00", "#FF0000");
$def[1] = "";
foreach ($DS as $i) {
$color = array_shift($colors);
$def[1] .=  "DEF:var$i=$rrdfile:$DS[$i]:AVERAGE " ;
if ($i == 1) {
$def[1] .= "AREA:var$i$color:\"$NAME[$i] \\n\" " ;
} else {
$def[1] .= "LINE2:var$i$color:\"$NAME[$i] \\n\" " ;
}
$def[1] .= "GPRINT:var$i:LAST:\"\t%6.2lf last\" " ;
$def[1] .= "GPRINT:var$i:AVERAGE:\"%6.2lf avg\" " ;
$def[1] .= "GPRINT:var$i:MAX:\"%6.2lf max\\n\" " ;
}


#$def[1] .= "DEF:var2=$rrdfile:$DS[2]:AVERAGE " ;
#$def[1] .= "DEF:var3=$rrdfile:$DS[3]:AVERAGE " ;
#if ($WARN[1] != "") {
#    $def[1] .= "HRULE:$WARN[1]#FFFF00 ";
#}
#if ($CRIT[1] != "") {
#    $def[1] .= "HRULE:$CRIT[1]#FF0000 ";       
#}
#$def[1] .= "AREA:var3#FF0000:\"Load 15\" " ;
#$def[1] .= "AREA:var2#EA8F00:\"Load 5 \" " ;
#$def[1] .= "GPRINT:var2:LAST:\"%6.2lf last\" " ;
#$def[1] .= "GPRINT:var2:AVERAGE:\"%6.2lf avg\" " ;
#$def[1] .= "GPRINT:var2:MAX:\"%6.2lf max\\n\" " ;
#$def[1] .= "AREA:var1#EACC00:\"load 1 \" " ;
#$def[1] .= "GPRINT:var1:LAST:\"%6.2lf last\" " ;
#$def[1] .= "GPRINT:var1:AVERAGE:\"%6.2lf avg\" " ;
#$def[1] .= "GPRINT:var1:MAX:\"%6.2lf max\\n\" ";
?>
