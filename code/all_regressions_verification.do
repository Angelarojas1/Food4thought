   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: In this code we run all regressions (1stage, IV, MCO, reduce form)
   ** Written by:  Ángela Rojas
   ** Last modified: October 29, 2024
   
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
merge 1:1 adm0 using "${versatility}/geographical.dta"
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
assert inlist(adm0, "MDG") if _merge == 2 //Madagascar
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

** Organiza population data
preserve
use "${pop}/populationlong2019.dta", clear
quietly unique adm0
keep adm0 population
tempfile pop
save `pop', replace
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
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with FLFP
quietly merge 1:1 adm0 using `flfp'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*

** merge with population
quietly merge 1:1 adm0 using `pop'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*


foreach z in "p0" "p10" "p25" "p33" "p50" "p60" "p66" "p70" {
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

*rename (logtime_median ingredients_median spices_median) (ltime ing spice)

*	foreach var of varlist ltime ing spice {
	foreach var of varlist time_median {
		
	* 1st stage		
	reghdfe `var' std_import al_mn pt_mn cl_md [aweight=population] , absorb(continentFactor)  

	local fval = e(F)	
	sum `var' if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	outreg2 using "${outputs}/data_check/regressions/all_`var'_wpop.xls", lab dec(4) excel par(se) stats(coef se) addstat(f-value, `fval', Adjusted R-squared, `: di %10.3f e(r2_a)') cttop("`z'") nocons title("`var'") ctitle("1st stage")
	
	
	* Reduced form
	reghdfe FLFP std_import al_mn pt_mn cl_md [aweight=population] , absorb(continentFactor) 
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	outreg2 using "${outputs}/data_check/regressions/all_`var'_wpop.xls", lab dec(4) excel par(se) stats(coef se) addstat(f-value, `fval', Adjusted R-squared, `: di %10.3f e(r2_a)') cttop("`z'") nocons title("`var'") ctitle("Reduced form")
	
	* OLS reg
	reghdfe FLFP `var' al_mn pt_mn cl_md [aweight=population] , absorb(continentFactor)  
	outreg2 using "${outputs}/data_check/regressions/all_`var'_wpop.xls", lab dec(4) excel par(se) stats(coef se) addstat(f-value, `fval', Adjusted R-squared, `: di %10.3f e(r2_a)') cttop("`z'") nocons title("`var'") ctitle("OLS")
	
	
	* IV reg
	ivreg2 FLFP al_mn pt_mn cl_md i.continentFactor (`var' = std_import)  [aweight=population]
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'

	outreg2 using "${outputs}/data_check/regressions/all_`var'_wpop.xls", lab dec(4) excel par(se) stats(coef se) addstat(f-value, `fval', Adjusted R-squared, `: di %10.3f e(r2_a)') cttop("`z'")  nocons title("`var'") ctitle("IV")
	}
	restore
}
/*
erase "${outputs}/data_check/regressions/all_ltime_wpop.txt"	
erase "${outputs}/data_check/regressions/all_ing_wpop.txt"	
erase "${outputs}/data_check/regressions/all_spice_wpop.txt"	

	* Export results
// 	esttab reg1 reg2 reg3 reg4 using "${outputs}/data_check/regressions/all_`var'_wpop.xls", ///
// 	se r2 star(* 0.1 ** 0.05 *** .01) label ///
// 	mtitles("First stage" "Reduced form" "OLS" "IV")  ///
// 	s( r2  mean N, ///
// labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
// nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
// fragment postfoot("Continent FE & Yes & Yes & Yes & Yes \\"  ///
// 		"Geographical controls & Yes & Yes & Yes & Yes \\" ///
// 		"\hline" "\end{tabular}") replace