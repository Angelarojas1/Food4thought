
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile merges all databases for analysis             *
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_all.dta"		              *
   *		   "${flfp}/FLFPlong2019.dta"								  *
   *           "${versatility}/geographical.dta"              			  *
   *           "${versatility}/cuisine_ciat.dta"         				  *
   *           "${versatility}/native/nativebycountry_`x'_`y'.dta"  	  *
   *           "${versatility}/imported/importbycountry_`z'.dta"       	  *
   * - Output: "${versatility}/reg_variables.dta"         				  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 15, 2023

****************************************
* Get data ready for regressions
****************************************

use "${recipes}/cuisine_complexity_all.dta", clear

** merge with geographical data
merge 1:1 adm0 using "${versatility}/geographical.dta"
assert _merge != 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
quietly count
assert `r(N)' == 139
drop _merge

** organize FLFP data
preserve
use "${flfp}/FLFPlong2019.dta", clear
quietly unique adm0
keep adm0 FLFP
tempfile flfp
save `flfp', replace
restore

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

** merge with numNative ingredients
merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with FLFP
merge 1:1 adm0 using `flfp'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*

quietly unique adm0
assert `r(sum)' == 139


** 	MERGE WITH IV INFORMATION
*local perc "p60"
*foreach val of local perc {
*preserve

** merge with native versatility
merge 1:1 adm0 using "${versatility}/native/nativebycountry_p60_g3simple.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
merge 1:1 adm0 using "${versatility}/imported/importbycountry_p60.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logtime_median = log(time_median)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"

* Save database
save "${versatility}/reg_variables.dta", replace
*restore
*} 