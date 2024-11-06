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
*local today : display %tdCYND date(c(current_date), "DMY")

* Note: find the highest f statistics: p60, g3simple, p60
		
use "${recipes}/cuisine_complexity_all.dta", clear

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
assert `r(sum)' == 138

eststo clear

foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66" "p70" {
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p33" "p25" "p50" "p60" "p66" "p70" { 
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
quietly merge m:1 adm0 using "${versatility}/imported/importbycountry_v4_`x'.dta"
assert _merge !=2
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

* Create interaction between gender and IV variable
	gen fem_nat = fem*std_native
	gen fem_imp = fem*std_import
	
* Label variables
	la var fem_nat 		"Women x Native versatility"
	la var fem_imp 		"Women x Imported versatility"

rename (logtime_median ingredients_median spices_median) (ltime ing spice)

	foreach var of varlist ltime ing spice {
	
		gen comp = fem*`var'	
		la var comp "Women x Complexity"
    
		local lb: variable label `var'
	
	* 1st stage		
	quietly reghdfe comp fem fem_nat fem_imp hhsize if covid==0, absorb(niso ym) cluster(niso)
	
		local fval = e(F)

		sum `var' if e(sample)
*		local mean = r(mean)
*		estadd scalar mean = `mean'

	outreg2 using "${outputs}/Tables/iv_best/cookpad/`var'_v4.xls", lab dec(4) excel par(se) stats(coef se) keep(fem_nat fem_imp) addstat(f-value, `fval') ctitle("`x'`y'_`z'") nocons title("`var'")
	
	drop comp
	}
	
	restore
	}
	}
	}
	
	erase "${outputs}/Tables/iv_best/cookpad/ltime_v4.txt"
	erase "${outputs}/Tables/iv_best/cookpad/ing_v4.txt"
	erase "${outputs}/Tables/iv_best/cookpad/spice_v4.txt"