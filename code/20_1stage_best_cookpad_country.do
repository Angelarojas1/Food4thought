   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *         This dofile gets regressions results to identify most        *
   *            accurate one 											  *
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_sum.dta"		              *
   *		   "${cookpad}/Cookpad_clean.dta"							  *
   *           "${versatility}/geographical.dta"              			  *
   *           "${versatility}/cuisine_ciat.dta"         				  *
   *           "${versatility}/native/nativebycountry_`x'_`y'.dta"  	  *
   *           "${versatility}/imported/importbycountry_`z'.dta"       	  *
   * - Output: "${outputs}/Tables/iv_best/cookpad/best_time.tex"          *
   *		   "${outputs}/Tables/iv_best/cookpad/best_ingredient.tex"	  *
   *		   "${outputs}/Tables/iv_best/cookpad/best_spices.tex"		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 29, 2023

****************************************
* Find the best 1st stage regression
**************************************

* Date global
global today : display %tdCYND date(c(current_date), "DMY")
mkdir "${outputs}/Tables/iv_best/cookpad/$today"

* Note: find the highest f statistics: p60, g3simple, p60
		
use "${recipes}/cuisine_complexity_all.dta", clear

** organize cookpad data
preserve
do "${code}/subcode/cookpad_reg.do"
keep country 
duplicates drop
tempfile cookpad
save `cookpad', replace
restore

** merge with cookpad
quietly merge 1:1 country using `cookpad'
keep if _merge == 3
*drop if _merge == 2
* merge == 1 -> 21
drop _merge*

quietly unique adm0
assert `r(sum)' == 117

eststo clear

foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66" "p70" {
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p33" "p25" "p50" "p60" "p66" "p70" { 
preserve

** merge with native versatility
quietly merge 1:1 adm0 using "${versatility}/native/nativebycountry_`x'_`y'.dta"
*assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${versatility}/imported/importbycountry_`z'.dta"
*assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
quietly replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logtime_median = log(time_median)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

rename (logtime_median ingredients_median spices_median) (ltime ing spice)

	foreach var of varlist ltime ing spice {

    
		local lb: variable label `var'
	
	* 1st stage		
	quietly reghdfe `var' std_native std_import , absorb(continentFactor) 
	
		local fval = e(F)

		sum `var' if e(sample)
*		local mean = r(mean)
*		estadd scalar mean = `mean'

	outreg2 using "${outputs}/Tables/iv_best/cookpad/$today/`var'_country.xls", lab dec(4) excel par(se) stats(coef se) keep(std_native std_import) addstat(f-value, `fval') ctitle("`x'`y'_`z'") nocons title("`var'")
	
	}
	
	restore
	}
	}
	}
	
	erase "${outputs}/Tables/iv_best/cookpad/$today/ltime_country.txt"
	erase "${outputs}/Tables/iv_best/cookpad/$today/ing_country.txt"
	erase "${outputs}/Tables/iv_best/cookpad/$today/spice_country.txt"