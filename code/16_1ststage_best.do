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
local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** organize FLFP data
preserve
use "${flfp}/FLFPlong2019.dta", clear
quietly unique country
keep country FLFP
tempfile flfp
save `flfp', replace
restore

** Organize native ingredients data
preserve
use "${versatility}/cuisine_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 136
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

** merge with numNative ingredients
quietly merge 1:1 adm0 using `numNative'
rename _merge _merge1

** merge with FLFP
quietly merge 1:1 country using `flfp'
drop if _merge == 2
drop if adm0 == "XXK" // Kosovo
assert _merge == 3
assert _merge1 == 3
drop _merge*

quietly unique adm0
assert `r(sum)' == 135

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
	quietly reghdfe lt_md std_native std_import numNative al_mn pt_mn cl_md [aweight=num_recipes] , absorb(continentFactor)  
	
	if `e(F)' > `fval'{
		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"

		eststo t`x'`y'`z'
		sum lt_md if e(sample)
		local mean = r(mean)
		estadd scalar mean = `mean'
	}
	
	}
	}
	}
	
		esttab t* using "${outputs}/Tables/iv_best/best_time.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import) label ///
		mtitle ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{12}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace
eststo clear
		
** Ingredients
local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** organize FLFP data
preserve
use "${flfp}/FLFPlong2019.dta", clear
quietly unique country
keep country FLFP
tempfile flfp
save `flfp', replace
restore

** Organize native ingredients data
preserve
use "${versatility}/cuisine_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 136
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

** merge with numNative ingredients
quietly merge 1:1 adm0 using `numNative'
rename _merge _merge1

** merge with FLFP
quietly merge 1:1 country using `flfp'
drop if _merge == 2
drop if adm0 == "XXK" // Kosovo
assert _merge == 3
assert _merge1 == 3
drop _merge*

quietly unique adm0
assert `r(sum)' == 135

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
	
	if `e(F)' > `fval'{
		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"

		eststo i`x'`y'`z'
		sum ing_md if e(sample)
		local mean = r(mean)
		estadd scalar mean = `mean'
	}
	
	}
	}
	}
	
lab var ing_md "ing_md"
	
		esttab i* using "${outputs}/Tables/iv_best/best_ingredient.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import)label ///
				mtitle ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace
eststo clear

** Spices
local fval = -100
foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	foreach y in "g2simple" "g2weight" "g3simple" "g3weight"{ 
		foreach z in "p0" "p10" "p25" "p50" "p60" "p70"{

		
use "${recipes}/cuisine_complexity_sum.dta", clear

** merge with geographical data
quietly merge 1:1 adm0 using "${versatility}/geographical.dta"
assert _merge != 2
quietly keep if _merge == 3
quietly count
assert `r(N)' == 135
drop _merge

** organize FLFP data
preserve
use "${flfp}/FLFPlong2019.dta", clear
quietly unique country
keep country FLFP
tempfile flfp
save `flfp', replace
restore

** Organize native ingredients data
preserve
use "${versatility}/cuisine_ciat.dta", clear
quietly unique adm0
assert `r(sum)' == 136
keep adm0 numNative
quietly duplicates drop
tempfile numNative
save `numNative', replace
restore

** merge with numNative ingredients
quietly merge 1:1 adm0 using `numNative'
rename _merge _merge1

** merge with FLFP
quietly merge 1:1 country using `flfp'
drop if _merge == 2
drop if adm0 == "XXK" // Kosovo
assert _merge == 3
assert _merge1 == 3
drop _merge*

quietly unique adm0
assert `r(sum)' == 135

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
	
	if `e(F)' > `fval'{
		local fval = e(F)
*		dis `fval'
*		dis "`x'"
*		dis "`y'"
*		dis "`z'"

		eststo s`x'`y'`z'
		sum sp_md if e(sample)
		local mean = r(mean)
		estadd scalar mean = `mean'
	}
	
	}
	}
	}
	
lab var sp_md "sp_md"

		esttab s* using "${outputs}/Tables/iv_best/best_spices.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import)label ///
		mtitle ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{14}{c}} \hline\hline") ///
		fragment postfoot("Continent & Yes & & & \\"  ///
		"Geographical & Yes & & & \\" ///
		"\hline" "\end{tabular}") replace


		
