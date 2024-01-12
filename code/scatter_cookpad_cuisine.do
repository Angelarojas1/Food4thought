   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * This dofile creates scatterplots to check relation between cuisine variables*
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_all.dta"		      		  *
   *		   "${cookpad}/Cookpad_clean.dta"							  *
   * - Output: "${outputs}/Figures/cookpad/`x'_`y'.png"	          		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:      	Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Jan 1, 2024

use "${recipes}/cuisine_complexity_all.dta", clear

preserve
do "${code}/subcode/cookpad_reg.do"
tempfile cookpad
save `cookpad', replace
restore

** merge with cookpad
merge 1:m country using `cookpad'
keep if _merge == 3

** Create scatterplots
gen logtime_median = log(time_median)

foreach x of varlist logtime_median ingredients_median {
	foreach y of varlist logtime_median ingredients_median spices_median {
	
	if "`x'" != "`y'" {
	egen clock1 = mlabvpos(`x' `y')
	
	twoway (scatter `x' `y', mlabel(country) mlabsize(small)) (lfit `x' `y')
	graph export "${outputs}/Figures/cookpad/`x'_`y'.png", replace
	
	drop clock1
	}
	}
}



