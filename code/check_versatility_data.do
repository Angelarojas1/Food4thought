* Import database
foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66"  "p70"{ 
	
use "${versatility}/imported/importbycountry_v3_`x'.dta", clear
sum importVersatility, de

}

/*
Versatility measure goes from 0.0005 to 0.0707
*/