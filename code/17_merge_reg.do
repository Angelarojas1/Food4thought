
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile merges all databases for analysis             *
   *																	  *
   * - Inputs: "${codedata}/recipes/recipe_FLFP2019.dta"	              *
   *           "${codedata}/iv_versatility/geographical.dta"              *
   *           "${codedata}/iv_versatility/recipe_flfp_ciat.dta"          *
   *           "${codedata}/iv_versatility/nativebycountry_pxx_gxsimple.dta" *
   *           "${codedata}/iv_versatility/importbycountry_pxx.dta"       *
   * - Output: "${codedata}/merge/`val'.dta"               *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 11, 2023

****************************************
* Get data ready for regressions
****************************************

use "${codedata}/recipes/recipe_FLFP2019.dta", clear

** merge with geographical data
merge 1:1 adm0 using "${codedata}/iv_versatility/geographical.dta"
assert _merge != 2
keep if _merge == 3
count
assert `r(N)' == 135
drop _merge

** merge with numNative
preserve
use "${codedata}/iv_versatility/recipe_ciat.dta", clear
unique adm0
assert `r(sum)' == 136
keep adm0 numNative region_nice
duplicates drop adm0 numNative, force
tempfile numNative
save `numNative', replace
restore

merge 1:1 adm0 using `numNative'
drop if adm0 == "XXK" // Kosovo
assert _merge == 3
drop _merge

unique adm0
assert `r(sum)' == 135

** 	MERGE WITH IV INFORMATION
local perc "p60 p50"
foreach val of local perc {
preserve
** merge with native versatility
merge 1:1 adm0 using "${codedata}/iv_versatility/nativebycountry_`val'_g3simple.dta"
drop if adm0 == "XXK" // Kosovo
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
merge 1:1 adm0 using "${codedata}/iv_versatility/importbycountry_`val'.dta"
drop if adm0 == "XXK" // Kosovo
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
encode region_nice, gen(regionFactor)
gen logtime_mean = log(time_mean)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"
label var ingredients_mean "avg number of ingredients"
label var spices_mean "avg number of spices"

* Save database
save "${codedata}/merge/`val'.dta", replace
restore
} 