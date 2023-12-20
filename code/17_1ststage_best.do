   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile gets regressions results to identify most     *
   *            accurate one 											  *
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_sum.dta"		              *
   *		   "${flfp}/FLFPlong2019.dta"								  *
   *           "${versatility}/geographical.dta"              			  *
   *           "${versatility}/cuisine_ciat.dta"         				  *
   *           "${versatility}/native/nativebycountry_`x'_`y'.dta"  	  *
   *           "${versatility}/imported/importbycountry_`z'.dta"       	  *
   * - Output: "${outputs}/Tables/iv_best/best_time.tex"                  *
   *		   "${outputs}/Tables/iv_best/best_ingredient.tex"			  *
   *		   "${outputs}/Tables/iv_best/best_spices.tex"				  *
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
eststo clear
*local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70" {
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70" { 

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
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
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with FLFP
quietly merge 1:1 adm0 using `flfp'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*

quietly unique adm0
assert `r(sum)' == 139

** merge with native versatility
quietly merge 1:1 adm0 using "${versatility}/native/nativebycountry_`x'_`y'.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${versatility}/imported/importbycountry_`z'.dta"
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

rename (logtime_median ingredients_median spices_median) (ltime ing spice)

	foreach var of varlist ltime ing spice {
	
	* 1st stage		
	quietly reghdfe `var' std_native std_import numNative al_mn pt_mn cl_md [aweight=num_recipes] , absorb(continentFactor)  

*	if `e(F)' > `fval'{
		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"
		
*		eststo `x'`y'
		sum `var' if e(sample)
		local mean = r(mean)
*		estadd scalar mean = `mean'
	*}
	
	outreg2 using "${outputs}/Tables/iv_best/best_`var'.xls", lab dec(4) excel par(se) stats(coef se) keep(std_native std_import) addstat(mean.dep.var , `mean', f-value, `fval') addtext(native_import, "`x'`y'_`z'") nocons title("Log Time")
	}
	}
	}
	}
	
	erase "${outputs}/Tables/iv_best/best_ltime.txt"
	erase "${outputs}/Tables/iv_best/best_ing.txt"
	erase "${outputs}/Tables/iv_best/best_spice.txt"
	
	/*
		esttab using "${outputs}/Tables/iv_best/best_time.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import) label ///
		mtitle ///
		s(r2 F mean N , ///
		labels( "\midrule R-squared" "F-Value" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{12}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace
		
eststo clear
		
** Ingredients
*local fval = -100
foreach x in "p0" "p10" { // "p25" "p50" "p60" "p70"
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p50" { // "p0" "p10" "p25" "p60" "p70"

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
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
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with FLFP
quietly merge 1:1 adm0 using `flfp'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*

quietly unique adm0
assert `r(sum)' == 139

** merge with native versatility
quietly merge 1:1 adm0 using "${versatility}/native/nativebycountry_`x'_`y'.dta"
drop if adm0 == "XXK" // Kosovo
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${versatility}/imported/importbycountry_`z'.dta"
drop if adm0 == "XXK" // Kosovo
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

rename (logtime_median ingredients_median spices_median) (lt_md ing_md sp_md)

	* 1st stage		
	quietly reghdfe ing_md std_native std_import numNative al_mn pt_mn cl_md [aweight=num_recipes] , absorb(continentFactor)  
	
*	if `e(F)' > `fval'{
*		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"
		
		eststo `x'`y'
		sum lt_md if e(sample)
		local mean = r(mean)
		estadd scalar mean = `mean'
	*}
	
	}
	}
	}
	
lab var ing_md "ing_md"
	
		esttab using "${outputs}/Tables/iv_best/best_ingredient.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import)label ///
				mtitle ///
		s( r2 F mean N, ///
		labels( "\midrule R-squared" "F-Value" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace
		
eststo clear

** Spices
*local fval = -100
foreach x in "p0" "p10" { // "p25" "p50" "p60" "p70"
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p50" { // "p0" "p10" "p25" "p60" "p70"

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
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
quietly merge 1:1 adm0 using `numNative'
assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 1
drop _merge

** merge with FLFP
quietly merge 1:1 adm0 using `flfp'
drop if _merge == 2
assert inlist(adm0, "XXK") if _merge == 1 //Kosovo
drop _merge*

quietly unique adm0
assert `r(sum)' == 139
** merge with native versatility
quietly merge 1:1 adm0 using "${versatility}/native/nativebycountry_`x'_`y'.dta"
drop if adm0 == "XXK" // Kosovo
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
quietly replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
quietly merge 1:1 adm0 using "${versatility}/imported/importbycountry_`z'.dta"
drop if adm0 == "XXK" // Kosovo
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

rename (logtime_median ingredients_median spices_median) (lt_md ing_md sp_md)

	* 1st stage		
	quietly reghdfe sp_md std_native std_import numNative al_mn pt_mn cl_md [aweight=num_recipes] , absorb(continentFactor)  
	
*	if `e(F)' > `fval'{
*		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"
		
		eststo `x'`y'
		sum lt_md if e(sample)
		local mean = r(mean)
		estadd scalar mean = `mean'
	*}
	
	}
	}
	}
	
lab var sp_md "sp_md"

		esttab using "${outputs}/Tables/iv_best/best_spices.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import)label ///
		mtitle ///
		s( r2 F mean N, ///
		labels( "\midrule R-squared" "F-Value" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{14}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace


		
