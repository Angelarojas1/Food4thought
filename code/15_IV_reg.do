
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile merges all databases for analysis             *
   *																	  *
   * - Inputs: "${codedata}/merge/`val'.dta"	                          *
   * - Output: "${outputs}/Tables/ivreg_`val'_`var'.tex"     			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 11, 2023

   
local perc "p60 p50"
foreach val of local perc {


* Import dataset
use "${codedata}/merge/`val'.dta", clear

foreach var of varlist logmtime mIng mSpice{
	
	* 1st stage
	reghdfe `var' std_native std_import numNative al_mn cl_md pt_mn [aweight=num_recipes] , absorb(continentFactor)  
	eststo reg1
	sum `var' if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	* iv
	ivreg2 FLFP numNative al_mn cl_md pt_mn i.continentFactor (`var' = std_native std_import)[aweight=num_recipes]
	eststo reg2
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	* OLS form
	reghdfe FLFP `var' numNative al_mn cl_md pt_mn [aweight=num_recipes], absorb(continentFactor)  
	eststo reg3
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	*reduced form
	reghdfe FLFP std_native std_import numNative al_mn cl_md pt_mn [aweight=num_recipes], absorb(continentFactor) 
	eststo reg4
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	
	esttab reg1 reg2 reg3 reg4 using "${outputs}/Tables/ivreg_`val'_`var'.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import `var')label ///
mtitles("First stage" "IV" "OLS" "Reduced form")  ///
s( r2  mean N, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace
	
}
}