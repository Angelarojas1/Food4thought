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
	
	*-- Rename employment variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours wp1220) (ft p2p lfpr hours age)
	
	* merge with cuisine data
	rename three_letter_country_code adm0
	merge m:1 country using "$recipes/complexity_recipe.dta" 
	keep if _merge == 3
	drop _merge
	
	*-- GDP data
	merge m:1 country using "${gdp}/GDPlong2019_pc.dta", gen(gdp_merge)
	
	keep if gdp_merge != 2
	drop gdp_merge 
	
	*-  Create the log of GDP
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*-- Native Versatility measure
	merge m:1 adm0 using "$versatility/native_versatility_m_c.dta", gen(final_versatility_merge)	
	keep if final_versatility_merge == 3
	
	*-- Versatily measures that include distance
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta",  ///
				keep(3) nogen
		
	foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
		
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
	
	drop _merge
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA with standarized variables
	pca z_w_mean_spices z_median_totaltime z_median_ingredients
	
	predict pca_index if e(sample), score
	
	sum  pca_index 
	gen z_pca_index  = ( pca_index  - r(mean)) / r(sd)
	
	encode region, gen(region_cat)
	
	label var country "Country" 
	label var Country "Encoded country" 
	label var median_totaltime "Median total time" 
	label var median_spices "Median Spices" 
	label var median_ingredients "Median Ingredients" 
	label var mean_ingredients "Mean ingredients" 
	label var w_mean_totaltime "Winsorized mean total time" 
	label var w_mean_spices "Average spices" 
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
	label var staple_suitability "Mean saple suitability"
	label var pca_index "PCA Index"
	label var z_pca_index "Cuisine complexity"
	label var pca_recipe "PCA Index - recipe"
	label var z_pca_recipe "Cuisine complexity"

	
	*-- Create other outcomes for regressions
	egen precip_bin = cut(precip), at(0(50)250)
	egen meals=rowtotal(numDinCook numLunCook)
	gen partjob=cond(hours==1 | hours==2,1,0) if hours!=0. & hours!=98
	gen spousecook=cond(wp19962==1 | wp19970==1,1,cond(wp19962==2 | wp19970==2,0,.)) 
	gen nonsingle=cond(wp1223==2|wp1223==8,1,0) if (wp1223!=6 & wp1223!=7 & wp1223!=.)  
	
	// other employment outcomes 
	// fulltime work condition on lfp 
	gen fullemployee=cond(emp_2010==1,1,0) if emp_2010!=. & emp_2010!=6 
	gen fulltime=cond(emp_2010<=2,1,0) if emp_2010!=. & emp_2010!=6 
	
	// share lunches and 
	gen pmeals=(numLunCook+numDinCook)/(numLunEat+numDinEat)
	replace pmeals=1 if pmeals>1 & pmeals!=.
	
	egen cont_cat=group(continent)
	gen lmedian_time=log(median_totaltime)
	gen lmean_time=log(w_mean_totaltime)
	lab var lmedian_time "Log. median cooking time"
	lab var lmean_time "Log. average cooking time"
	lab var staple_suitability  "Mean Staple Suitability"
	
	save "$cookpad/cookpad_adm0.dta", replace
	
	*=========================================================
	* Fix migrants data 
	*=========================================================
	use "$cookpad\Cookpad_clean.dta", replace
	
	* keep useful variables
	* keep country three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender
	gen covid=(ym>=722)
	
	* merge with cuisine data
	rename three_letter_country_code adm0
	
	*-- Change adm0 if person was born in another country
	decode wp9048, gen(born_country)
	tab born_country if wp4657 == 2
	
	gen country2 = ""
	replace country2 = born_country if wp4657 == 2 																	
	preserve
	keep country adm0
	rename (country adm0) (country2 adm02)
	duplicates drop
	tempfile adm
	save `adm'
	restore
	
	merge m:1 country2 using `adm' // , keep(3) no gen
	
	gen country_fe = country
	gen adm0_fe = adm0
	replace country = country2 if _merge == 3
	replace adm0 = adm02 if _merge == 3
	
	drop country2 adm02 _merge
	
	drop if year == 2020
	
	merge m:1 country using "$recipes/complexity_recipe.dta" 
	keep if _merge == 3
	drop _merge
	
	*-- GDP data
	merge m:1 country using "${gdp}/GDPlong2019_pc.dta", gen(gdp_merge)
	
	keep if gdp_merge != 2
	drop gdp_merge 
	
	*-- Native Versatility measure
	merge m:1 adm0 using "$versatility/native_versatility_m_c.dta", gen(final_versatility_merge)	
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
	
	drop _merge
	
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
	label var staple_suitability "Mean saple suitability"

	save "$cookpad/cookpad_adm0_m.dta", replace
	
	
	*=========================================================
	* Adding cookpad indicator to versatility
	*=========================================================
	
	use "$cookpad\Cookpad_clean.dta", replace
	
	rename three_letter_country_code adm0
	drop if year == 2020
	
	keep adm0
	duplicates drop
	
	merge 1:1 adm0 using "$versatility/native_versatility_m_c.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$versatility/final_versatility_m_c.dta", replace
