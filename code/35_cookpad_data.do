* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Cookpad Data Exploration
* **************************************************************************** *

	use "$cookpad\Cookpad_clean.dta", replace
	
	drop if year == 2020
	
	* keep useful variables
	* keep country three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender
	gen covid=(ym>=722)
	
	* merge with cuisine data
	rename three_letter_country_code adm0
	merge m:1 country using "$recipes/complexity_recipe.dta" 
	keep if _merge == 3
	drop _merge
	
	*-- GDP data
	merge m:1 country using "${gdp}/GDPlong2019_pc.dta", gen(gdp_merge)
	
	keep if gdp_merge != 2
	drop gdp_merge 
	
	*-- Native Versatility measure
	merge m:1 adm0 using "$versatility/final_native_versatility.dta", gen(final_versatility_merge)	
	keep if final_versatility_merge == 3
	
	*-- Geographical controls
	merge m:1 adm0 using "${versatility}/geographical.dta"
	keep if _merge == 3
	
	drop final_versatility_merge _merge
	
	*-- Galor controls
	merge m:1 adm0 using "${versatility}/galor_controls.dta"
	keep if _merge != 2 
	drop _merge
	
	*-- Staple suitability data
	preserve
	use "${precodedata}/suitability/staple_suitability.dta", clear
	egen staple_suitability = mean(suitability), by(adm0)
	keep adm0 staple_suitability
	duplicates drop
	tempfile staple_suitability
	save `staple_suitability'
	restore
	
	merge m:1 adm0 using `staple_suitability'
	keep if _merge != 2 
	
	drop continent _merge
	
	label var country "Country" 
	label var Country "Encoded country" 
	label var median_totaltime "Median total time" 
	label var median_spices "Median Spices" 
	label var median_ingredients "Median Ingredients" 
	label var mean_ingredients "Mean ingredients" 
	label var w_mean_totaltime "Winsorized mean total time" 
	label var w_mean_spices "Winsorized mean spices" 
	label var numrecipes "Number of recipes" 
	label var year "LFP year" 
	label var GDP "Gross Domestic Product"
	label var numNative "Number of Native ingredients" 
	label var numNativeCIAT "Number of Native ingredients on CIAT database" 
	label var native_versatility "Native versatility, country's ingredients" 
	label var native_versatility2 "Native versatility, all ingredients" 
	label var native_spice_vers "Native spices versatility, country's ingredients" 
	label var native_spice_vers2 "Native spices versatility, all ingredients" 
	label var suit_versatility "Native versatility 2 weighted by suitability" 
	label var suit_spice_vers "Native spice versatility 2 weighted by suitability" 
	label var avg_suitability "Mean Suitability" 
	label var cookpad "Cookpad (Dummy)" 
	label var staple_suitability "Mean saple suitability"

	save "$cookpad/cookpad_adm0.dta", replace
	
	
	*=========================================================
	* Adding cookpad indicator to versatility
	*=========================================================
	
	keep adm0
	duplicates drop
	
	preserve
	merge 1:1 adm0 using "$versatility/all_versatility.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$versatility/final_versatility.dta", replace
	restore

	preserve
	merge 1:1 adm0 using "$versatility/native_versatility_m_c.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	drop cookpad_merge
	
	save "$versatility/final_native_versatility.dta", replace
	restore
	
	preserve
	merge 1:1 adm0 using "$versatility/all_versatility_m.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$versatility/final_versatility_m.dta", replace
	restore
	
	merge 1:1 adm0 using "$versatility/all_versatility_m_c.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$versatility/final_versatility_m_c.dta", replace