   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile gets regressions results to identify most     *
   *            accurate one 											  *
   *																	  *
   * - Inputs: "${codedata}/recipes/recipe_FLFP2019.dta"	              *
   *           "${codedata}/iv_versatility/geographical.dta"              *
   *           "${codedata}/iv_versatility/recipe_flfp_ciat.dta"          *
   *           "${codedata}/iv_versatility/nativebycountry_`x'_`y'.dta"   *
   *           "${codedata}/iv_versatility/importbycountry_`z'.dta"       *
   * - Output:                                                            *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 24, 2023

****************************************
* Find the best 1st stage regression
****************************************

* Note: find the highest f statistics: p60, g3simple, p60

local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${codedata}/recipes/recipe_FLFP2019.dta", clear
rename three_letter_country_code adm0

** merge with geographical data
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** merge with numNative
preserve
use "${codedata}/iv_versatility/recipe_flfp_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 135
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

quietly merge 1:1 adm0 using `numNative'
assert _merge == 3
drop _merge

quietly unique adm0
assert `r(sum)' == 135

** merge with native versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/nativebycountry_`x'_`y'.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/importbycountry_`z'.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
quietly replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logmtime = log(mTime)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"
label var mIng "average number of ingredients"
label var mSpice "average number of spices"

	* 1st stage
	quietly reghdfe logmtime std_native std_import numNative al_mn [aweight=num_recipes] , absorb(continentFactor)  
	
	if `e(F)' > `fval'{
		local fval = e(F)
		dis `fval'
		dis "`x'"
		dis "`y'"
		dis "`z'"
	}
	
		}
		}
		}

local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${codedata}/recipes/recipe_FLFP2019.dta", clear
rename three_letter_country_code adm0

** merge with geographical data
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** merge with numNative
preserve
use "${codedata}/iv_versatility/recipe_flfp_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 135
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

quietly merge 1:1 adm0 using `numNative'
assert _merge == 3
drop _merge

quietly unique adm0
assert `r(sum)' == 135

** merge with native versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/nativebycountry_`x'_`y'.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/importbycountry_`z'.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
quietly replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logmtime = log(mTime)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"
label var mIng "average number of ingredients"
label var mSpice "average number of spices"

	* 1st stage
	quietly reghdfe mIng std_native std_import numNative al_mn [aweight=num_recipes] , absorb(continentFactor)  
	
	if `e(F)' > `fval'{
		local fval = e(F)
		dis `fval'
		dis "`x'"
		dis "`y'"
		dis "`z'"
	}
	
		}
		}
		}
		
		
local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${codedata}/recipes/recipe_FLFP2019.dta", clear
rename three_letter_country_code adm0

** merge with geographical data
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** merge with numNative
preserve
use "${codedata}/iv_versatility/recipe_flfp_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 135
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

quietly merge 1:1 adm0 using `numNative'
assert _merge == 3
drop _merge

quietly unique adm0
assert `r(sum)' == 135

** merge with native versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/nativebycountry_`x'_`y'.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${codedata}/iv_versatility/importbycountry_`z'.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
quietly replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logmtime = log(mTime)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"
label var mIng "average number of ingredients"
label var mSpice "average number of spices"

	* 1st stage
	quietly reghdfe mSpice std_native std_import numNative al_mn [aweight=num_recipes] , absorb(continentFactor)  
	
	if `e(F)' > `fval'{
		local fval = e(F)
		dis `fval'
		dis "`x'"
		dis "`y'"
		dis "`z'"
	}
	
		}
		}
		}
