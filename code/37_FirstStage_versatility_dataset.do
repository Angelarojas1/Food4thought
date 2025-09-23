* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Dataset creation
* **************************************************************************** *

	
	/* ***************************************************** *
		* File Details
		import Versatility Median
		native Versatility Weighted Median
		*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	merge 1:1 adm0 using "$versatility/final_versatility.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset.dta", replace
	
	/* ***************************************************** *
	* File Details: Milla + CIAT only native versatility
	*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	*-- FLFP data
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	drop continent_code flfp_merge two_letter_country_code country_name ///
	country_number flfp_merge
	encode continent_name, gen(continent_code)
	
	*-- Native Versatility measure
	merge 1:1 adm0 using "$versatility/final_native_versatility.dta", gen(final_versatility_merge)	
	keep if final_versatility_merge == 3
	
	*-- Geographical controls
	merge 1:1 adm0 using "${versatility}/geographical.dta"
	keep if _merge == 3
	
	drop final_versatility_merge _merge
	
	*-- Galor controls
	merge 1:1 adm0 using "${versatility}/galor_controls.dta"
	keep if _merge != 2 
	drop _merge
	
	*-- Staple suitability data
	merge 1:m adm0 using "${precodedata}/suitability/staple_suitability.dta"
	keep if _merge != 2 
	egen staple_suitability = mean(suitability), by(adm0)
	drop admin0_name crp extents suit_vs suit_s suit_ms suit_vms suit_ns ingredient suitability _merge
	duplicates drop
	
	*--- Label vars
	label var country "Country" 
	label var Country "Encoded country" 
	label var median_totaltime "Median total time" 
	label var median_spices "Median Spices" 
	label var median_ingredients "Median Ingredients" 
	label var mean_ingredients "Mean ingredients" 
	label var w_mean_totaltime "Winsorized mean total time" 
	label var w_mean_spices "Winsorized mean spices" 
	label var numrecipes "Number of recipes" 
	label var year "FLFP year" 
	label var FLFP "Female Labor Force Participation" 
	label var numNative "Number of Native ingredients" 
	label var numNativeCIAT "Number of Native ingredients on CIAT database" 
	label var native_versatility "Native versatility, country's ingredients" 
	label var native_versatility2 "Native versatility, all ingredients" 
	label var suit_versatility "Native versatility 2 weighted by suitability" 
	label var avg_suitability "Mean Suitability" 
	label var cookpad "Cookpad (Dummy)" 
	label var staple_suitability "Mean saple suitability"
	
	save "$versatility/first_stage_dataset_native_m_c.dta", replace
	
	/* ***************************************************** *
	* File Details: Milla + CIAT
	*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	merge 1:1 adm0 using "$versatility/final_versatility_m_c.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset_m_c.dta", replace