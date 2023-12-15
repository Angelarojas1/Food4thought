   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *   This dofile shows raw correlations of FLFP and cuisine complexity  *
   *																	  *
   * - Inputs: "${codedata}/flfp/FLFPlong2019.dta"						  *
   *		   "${codedata}/recipes/cuisine_complexity_sum.dta"		      *
   * - Output: "${outputs}/Figures/RecipeFLFPTime.png"				      *
   *		   "${outputs}/Figures/RecipeFLFPSpi.png"					  *
   *		   "${outputs}/Figures/RecipeFLFPIng.png"					  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 13, 2023

* import FLFP dataset
use "${codedata}/flfp/FLFPlong2019.dta", clear

* Merge cuisine data with FLFP data *
merge 1:1 country using "${codedata}/recipes/cuisine_complexity_sum.dta"
tab _merge
assert inlist(_merge, 1, 2, 3)

tab country if _merge == 2
assert country == "Kosovo" if _merge == 2

tab country if _merge == 1
assert country != "Kosovo" if _merge == 1

keep if _merge == 3
drop _merge

tab country if missing(FLFP)
assert inlist(country, "Aruba", "Dominica", "Liechtenstein", "Tuvalu") if missing(FLFP)
note: No FLFP data is available for Aruba, Dominica, Liechtenstein, Kosovo, Tuvalu.

unique country if !missing(FLFP)
note: There are `r(sum)' countries both have recipes and FLFP data.

foreach var of varlist time* ingredients* spices*{
	assert !missing(`var')
}

*================================================
* Raw correlations of FLFP and cuisine complexity
*================================================

** scatter plot
foreach var of varlist time_mean{
	egen clock1 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock1)  mlabsize(small) xtitle("Avge Recipe Prep Time"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPTime.png", replace
	
}

foreach var of varlist ingredients_mean{
	egen clock2 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock2)  mlabsize(small) xtitle("Number of Ingredients"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPIng.png", replace
	
}

foreach var of varlist spices_mean{
	egen clock3 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock3)  mlabsize(small) xtitle("Number of Spices"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPSpi.png", replace
	
}

** regressions
foreach var of varlist time_mean ingredients_mean spices_mean{
	
	reg FLFP `var'
}