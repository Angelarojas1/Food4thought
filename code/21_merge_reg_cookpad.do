   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile merges all databases for analysis             *
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_sum.dta"		              *
   *		   "${cookpad}/Cookpad_clean.dta"							  *
   *           "${versatility}/geographical.dta"              			  *
   *           "${versatility}/cuisine_ciat.dta"         				  *
   *           "${versatility}/native/nativebycountry_`x'_`y'.dta"  	  *
   *           "${versatility}/imported/importbycountry_`z'.dta"       	  *
   * - Output: "${versatility}/reg_vbs_cookpad.dta"	    				  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 29, 2023
   
****************************************
* Get data ready for regressions
****************************************

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
assert _merge != 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
quietly count
assert `r(N)' == 139
drop _merge

** Organize native ingredients data
preserve
use "${versatility}/cuisine_ciat.dta", clear
keep adm0 numNative
quietly duplicates drop
quietly count
assert `r(N)' == 136
tempfile numNative
save `numNative', replace
restore

** organize cookpad data
preserve
do "${code}/subcode/cookpad_reg.do"
tempfile cookpad
save `cookpad', replace
restore

** merge with numNative ingredients
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with cookpad
quietly merge 1:m country using `cookpad'
drop if _merge == 2
* merge == 1 -> 21
drop _merge*

quietly unique adm0
assert `r(sum)' == 139

foreach x in "p0" "p50" {
	foreach y in "g2simple" "g3simple"{ 
		foreach z in "p0" "p50" { 
		
		if `x' == `y' {
preserve

** merge with native versatility
quietly merge m:1 adm0 using "${versatility}/native/nativebycountry_`x'_`y'.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge m:1 adm0 using "${versatility}/imported/importbycountry_`z'.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
quietly replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

	* Create log time 
	foreach v of varlist time* {
		gen l`v'=log(`v')
	}

* Create interaction between gender and IV variable
	gen fem_nat = fem*std_native
	gen fem_imp = fem*std_import
	
* Label variables
	la var fem_nat 		"Women x Native versatility"
	la var fem_imp 		"Women x Imported versatility"

	foreach v in time ingredients spices {
	foreach k in mean median p10 p25 p75 p90 {
			la var `v'_`k' "``v'' `k'"	
		}
	}

	foreach k in mean median p10 p25 p75 p90 {
 		la var ltime_`k' "Log time `k'"	
	}
	
* Save database
save "${versatility}/reg_cp_`x'`y'.dta", replace

restore
}
}
}
}