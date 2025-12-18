* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: 
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Dataset creation
* **************************************************************************** *

	
	/* ***************************************************** *
	* File Details: Milla + CIAT only native versatility
	*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	*-- FLFP data
	merge 1:m country using "${codedata}/merge/lfplong2019.dta", gen(lfp_merge)
	
	keep if lfp_merge != 2
	
	gen LFP_female = LFP if fem_lfp == 1
	gen LFP_male   = LFP if fem_lfp == 0
	
	drop continent_code lfp_merge two_letter_country_code 
	encode continent_name, gen(continent_code)
	
	*-- GDP data
	merge m:1 country using "${gdp}/GDPlong2019_pc.dta", gen(gdp_merge)
	
	keep if gdp_merge != 2
	drop gdp_merge 
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*-- Population data
	merge m:1 country using "${pop}/populationlong2019.dta", gen(pop_merge)
	
	keep if pop_merge != 2
	drop pop_merge 
	
	*-- Native Versatility measure
	merge m:1 adm0 using "$versatility/final_versatility_m_c.dta", gen(final_versatility_merge)	
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
	
	*-- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
		
	foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA with standarized variables
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
	
	label var pca_index "PCA Index"
	
	*-- Create old and new world variable
	gen oldworld = inlist(continent_name, "Africa", "Asia", "Europe")
	rename continent_name continent
		
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
	label var year "LFP year" 
	label var LFP "Labor Force Participation" 
	label var fem_lfp "Is Female Labor Force Participation" 
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
	label var oldworld "Country is from Old World"
	label var population "Population"
	
	*-- Encode variables 
	encode region, gen(region_cat)
	
	save "$versatility/first_stage_native_m_c.dta", replace
	