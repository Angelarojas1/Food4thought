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

** organize cookpad data
preserve
do "${code}/subcode/cookpad_reg.do"
tempfile cookpad
save `cookpad', replace
restore

** merge with cookpad
quietly merge 1:m country using `cookpad'
drop if _merge == 2
* merge == 1 -> 21
drop _merge*

quietly unique adm0
assert `r(sum)' == 139

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

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"

	
* Save database
save "${versatility}/reg_variables_cp.dta" , replace

