<?php
# Template used with okc-get_network_interfaces_stat
#
$interfaces = array();

# 3 graphs per interface

# bytes graph
# packets graph
# other graph
$matcher = array(
    'bytes'   => '/_[tr]x_bytes$/',
    'packets' => '/_[tr]x_packets$/',
);


foreach ($this->DS as $KEY=>$VAL) {

    $int = preg_replace('/_[rt]x_.*$/', '', $VAL['NAME']);

    # Create map key
    if (! array_key_exists($int, $interfaces) ) {
        $interfaces[$int] = array(
            'bytes' => array('num' => 0, 'def' => ""),
            'packets' => array('num' => 0, 'def' => ""),
            'other' => array('num' => 0, 'def' => ""),
        );
    }

    # Match current DS into cat (graph)
    $cat = 'other';
    foreach ($matcher as $key=>$match) {
        if (preg_match($match, $VAL['NAME'])) {
            $cat = $key;
            break;
        }
    }
    
    # Define the value
    $interfaces[$int][$cat]['def'] .= rrd::def     ("var$KEY", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");

    # Invert rx fields so they show below the line (negative)
    if ($cat == "other" || preg_match('/_tx_/', $VAL['NAME'])) {
        $interfaces[$int][$cat]['def'] .= rrd::cdef     ("var_t$KEY", "var$KEY,1,*");
    } else {
        $interfaces[$int][$cat]['def'] .= rrd::cdef     ("var_t$KEY", "var$KEY,-1,*");
    }

    if ($cat == "other") {
        $interfaces[$int][$cat]['def'] .= rrd::line1("var_t$KEY", rrd::color($interfaces[$int][$cat]['num']), rrd::cut($VAL['NAME'],20) ) . 
                rrd::gprint  ("var$KEY", array("LAST","MAX","AVERAGE"), "%8.2lf");
    } else {
        $interfaces[$int][$cat]['def'] .= rrd::area("var_t$KEY", rrd::color($interfaces[$int][$cat]['num']), rrd::cut($VAL['NAME'],20) ) . 
                rrd::gprint  ("var$KEY", array("LAST","MAX","AVERAGE"), "%8.2lf");
    }
    $interfaces[$int][$cat]['num'] += 2;

}


foreach (array_keys($interfaces) as $int) {
    $opt[] = "--title 'Network Statistics $int / Bytes'";
    $ds_name[] = "Bytes";
    $def[] = $interfaces[$int]['bytes']['def'];
    $opt[] = "--title 'Network Statistics $int / Packets'";
    $ds_name[] = "Packets";
    $def[] = $interfaces[$int]['packets']['def'];
    $opt[] = "--title 'Network Statistics $int / Other'";
    $ds_name[] = "Other";
    $def[] = $interfaces[$int]['other']['def'];
}


# vim: sts=4 expandtab autoindent
?>

