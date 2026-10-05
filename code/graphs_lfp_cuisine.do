/* ------------------------------------------------------------------------
        Cuisine Complexity and Female Labor Force Participation	    

Authors: Girija Borker, Margarita Gafaro, Steve Beggreen

Created on: January 26, 2026
Created by: Angela Rojas

Last modified: 

Description:
This code created line for LFP variables: Female, male and the gap vs
cuisine variables (time, ingredients, spices)
------------------------------------------------------------------------ */

*--- Identify countries used in the regressions
	use "$cookpad/cookpad_adm0.dta", replace
	
	*--- Create globals with the different controls
		
	global c1 "numrecipes"
	
	*--- Create standarized distance variables
	qui: reghdfe lfpr  w_mean_spices  $c1 if vers_distCapital_2000 != 0 & covid == 0 , absorb(region_cat cl_md ym) cluster(adm0)
	
	keep if e(sample)
	keep country
	duplicates drop
	
	tempfile sample
	save `sample'

*--- Import cuisine variables database
	
	use "$recipes/complexity_recipe.dta", clear
	
	*--. Merge with FLFP 
	merge 1:1 country using "${flfp}/FLFPlong2019.dta", nogen keep(3)
	
*--. Merge with MLFP 
	merge 1:1 country using "${mlfp}/MLFPlong2019.dta"
	drop if _merge == 2
	drop _merge
	
	rename Country country_encode
	rename *, lower
	
*--- Create gap variable
	gen gap = mlfp - flfp // 7 missings, countries we don't have both values for
	
	*- Merge with sample to keep only countries in regression exercises
	merge 1:1 country using `sample'
	
*--- Create graphs
		
	*- Time variable
	gen lmedian_time=log(median_totaltime)
	gen lmean_time=log(w_mean_totaltime)
	lab var lmean_time "Log. average cooking time"

	binscatter flfp mlfp gap lmedian_time if _merge == 3, ///
	lcolor(maroon navy gray) ///
	mcolor(maroon navy gray) ///
	xtitle("Log. Median cooking time") ///
	ytitle("Labor Force Participation") ///
	xlabel(, nogrid) ///
	ylabel(, nogrid angle(vertical)) ///
	legend(order(1 "FLFP" 2 "MLFP" 3 "Gap" ) position(6) region(lcolor(black)) col(3)) ///
	graphregion(color(white)) bgcolor(white)
	
	graph export "${figures}/lfp_time.pdf", replace
	
	*- Spices variable

	binscatter flfp mlfp gap w_mean_spices if _merge == 3, ///
	lcolor(maroon navy gray) ///
	mcolor(maroon navy gray) ///
	xtitle("Average spices") ///
	ytitle("Labor Force Participation") ///
	xlabel(, nogrid) ///
	ylabel(, nogrid angle(vertical)) ///
	legend(order(1 "FLFP" 2 "MLFP" 3 "Gap" ) position(6) region(lcolor(black)) col(3)) ///
	graphregion(color(white)) bgcolor(white)
	
	graph export "${figures}/lfp_spices.pdf", replace

	*- Ingredients variable

	binscatter flfp mlfp gap mean_ingredients if _merge == 3, ///
	lcolor(maroon navy gray) ///
	mcolor(maroon navy gray) ///
	xtitle("Average ingredients") ///
	ytitle("Labor Force Participation") ///
	xlabel(, nogrid) ///
	ylabel(, nogrid angle(vertical)) ///
	legend(order(1 "FLFP" 2 "MLFP" 3 "Gap" ) position(6) region(lcolor(black)) col(3)) ///
	graphregion(color(white)) bgcolor(white)
	
	graph export "${figures}/lfp_ing.pdf", replace
	