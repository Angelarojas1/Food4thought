   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: In this code we run 1stage regressions in multiple ways
   ** Written by:  Ángela Rojas
   ** Last modified: October 16, 2024
   
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
assert inlist(adm0, "MDG") if _merge == 2 //Madagascar
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

** merge with numNative ingredients
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge


foreach z in "p0" "p10" "p33" "p25" "p50" "p60" "p66" "p70" {
preserve

** merge with imported versatility
quietly merge 1:1 adm0 using "${versatility}/imported/importbycountry_v2_`z'.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

** create factor 
encode continent_name, gen(continentFactor)
gen logtime_median = log(time_median)
egen std_import = std(importVersatility)

rename (logtime_median ingredients_median spices_median) (ltime ing spice)

	foreach var of varlist ltime ing spice {

	* 1st stage		
	reghdfe `var' std_import al_mn pt_mn cl_md [aweight=num_recipes] , absorb(continentFactor)  

	local fval = e(F)

		
	sum `var' if e(sample)

	outreg2 using "${outputs}/data_check/regressions/`var'.xls", lab dec(4) excel par(se) stats(coef se) addstat(f-value, `fval', Adjusted R-squared, `: di %10.3f e(r2_a)') ctitle("`z'") nocons title("`var'")
	}
	restore
}

erase "${outputs}/data_check/regressions/ltime.txt"	
erase "${outputs}/data_check/regressions/ing.txt"	
erase "${outputs}/data_check/regressions/spice.txt"	

