   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *This dofile runs regressions using Cookpad, FLFP and cuisine variables*
   *																	  *
   * - Inputs: "${cookpad}/Cookpad_clean.dta"				      		  *
   *		   "${recipes}/cuisine_complexity_sum.dta"					  *
   *		   "${flfp}/FLFPlong2019.dta"						  		  *
   * - Output: "${outputs}/Tables/cookpad/olsr1.tex"				      *
   *		   "${outputs}/Tables/cookpad/olsr2.tex"					  *
   *		   "${outputs}/Tables/cookpad/olsr3.tex"					  *
   *		   "${outputs}/Tables/cookpad/olsr4.tex"					  *
   *		   "${outputs}/Figures/cookpad/`y'_`x'.png"					  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 13, 2023

***********************************************
* Merge cookpad data with cuisine and FLFP data
***********************************************

*import data
use "${cookpad}/Cookpad_clean.dta", clear

* keep useful variables
keep country three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender

* generate new variables
egen numTotalCook = rowtotal(numLunCook numLunCook)
egen numTotalEat = rowtotal(numLunEat numDinEat)

gen pctLunCook = numLunCook/numLunEat
gen pctDinCook = numDinCook/numDinEat

egen pctTotalCook = rowmean(pctLunCook pctDinCook)

* collapse
collapse numLunCook numDinCook numLunEat numDinEat numTotalCook numTotalEat, by(three_letter_country_code country)

* generate summary statistics for each variable
foreach var of varlist numLunCook numLunEat numDinCook numDinEat numTotalCook numTotalEat{
	sum `var', de
}

* merge with cuisine data
rename three_letter_country_code adm0
merge 1:1 adm0 using "${recipes}/cuisine_complexity_sum.dta" 
keep if _merge == 3
drop _merge

* merge with FLFP data
merge 1:1 adm0 using "${flfp}/FLFPlong2019.dta"
keep if _merge == 3
drop _merge

* reduced form
** generate variables
encode continent_name, gen(continentFactor)
gen logtime_mean = log(time_mean)

foreach var of varlist numLunCook numLunEat numDinCook numDinEat numTotalCook numTotalEat{
	gen time_`var' = time_mean*`var'
	gen logtime_`var' = log(time_mean*`var')
}

** label variables
label var logtime_numLunCook "log(avg time*avg lunch cook)"
label var logtime_numDinCook "log(avg time*avg dinner cook)"
label var logtime_numTotalCook "log(avg time*avg total cook)"
label var logtime_numLunEat "log(avg time*avg lunch eat)"
label var logtime_numDinEat "log(avg time*avg dinner eat)"
label var logtime_numTotalEat "log(avg time*avg total eat)"

label var time_numLunCook "avg time*avg lunch cook"
label var time_numDinCook "avg time*avg dinner cook"
label var time_numTotalCook "avg time*avg total cook"
label var time_numLunEat "avg time*avg lunch eat"
label var time_numDinEat "avg time*avg dinner eat"
label var time_numTotalEat "avg time*avg total eat"

label var time_mean "avg cooking time"
label var logtime_mean "log avg cooking time"

** regressions
/*
i.	FLFP = average cooking time + average cooking time*number of meals
ii.	FLFP = average cooking time*number of meals
iii.FLFP = log (average cooking time) + log (average cooking time*number of meals)
iv.	FLFP = log (average cooking time* number of meals)

*/
foreach var of varlist time_numLunCook time_numDinCook time_numTotalCook time_numLunEat time_numDinEat time_numTotalEat{
	reg FLFP time_mean `var' [aweight=num_recipes], absorb(continentFactor)
	eststo r1`var'
	sum	FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	
	reg FLFP `var' [aweight=num_recipes], absorb(continentFactor)
	eststo r2`var'
	sum	FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	
	reg FLFP logtime_mean log`var'[aweight=num_recipes], absorb(continentFactor)
	eststo r3`var'
	sum	FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	
	reg FLFP log`var'[aweight=num_recipes], absorb(continentFactor)
	eststo r4`var'
	sum	FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
}


esttab r1time_numLunCook r1time_numDinCook r1time_numTotalCook r1time_numLunEat r1time_numDinEat r1time_numTotalEat using "${outputs}/Tables/cookpad/olsr1.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) label ///
s( r2  mean N continent, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs." "Continent") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{7}{c}} \hline\hline") ///
fragment postfoot("\hline" "\end{tabular}")replace

esttab r2time_numLunCook r2time_numDinCook r2time_numTotalCook r2time_numLunEat r2time_numDinEat r2time_numTotalEat using "${outputs}/Tables/cookpad/olsr2.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) label ///
s( r2  mean N continent, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs." "Continent") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{7}{c}} \hline\hline") ///
fragment postfoot("\hline" "\end{tabular}")replace

esttab r3time_numLunCook r3time_numDinCook r3time_numTotalCook r3time_numLunEat r3time_numDinEat r3time_numTotalEat using "${outputs}/Tables/cookpad/olsr3.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) label ///
s( r2  mean N continent, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs." "Continent") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{7}{c}} \hline\hline") ///
fragment postfoot("\hline" "\end{tabular}")replace

esttab r4time_numLunCook r4time_numDinCook r4time_numTotalCook r4time_numLunEat r4time_numDinEat r4time_numTotalEat using "${outputs}/Tables/cookpad/olsr4.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) label ///
s( r2  mean N continent, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs." "Continent") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{7}{c}} \hline\hline") ///
fragment postfoot("\hline" "\end{tabular}")replace

* scatter plot
foreach y of varlist FLFP time_mean ingredients_mean spices_mean{
	foreach x of varlist numLunCook numDinCook numTotalCook numLunEat numDinEat numTotalEat{
		qui reg `y' `x'
		loc p = r(table)[4,1]
		aaplot `y' `x',lopts() mlabel(country) mlabsize(small) note("p'-value: `p'")
		graph export "${outputs}/Figures/cookpad/`y'_`x'.png", replace
	}
}