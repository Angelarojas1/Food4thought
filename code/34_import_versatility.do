* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Steve Berggreen
* 				Last date modified: November 10, 2025 					 	   *
*			Distance-weighted import versatility instrument using spices only
* **************************************************************************** *

use "$versatility/native_versatility_m_c1.dta",  clear
	
	ren (ingredient1 ingredient) (ingredient ingredient2)
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean_m_c.dta"
	keep if _merge == 3
	drop _merge
	
	
	* ===================================================== *
	*  Distance-weighted native spice versatility     *
	* ===================================================== *

	* ===================================================== *
	*  Distance-weighted native spice versatility (3 distances)
	* ===================================================== *

	*drop _merge
	tempfile main
	save `main', replace

	*-------------------------------------------------------*
	* 1. Create dataset of native ingredient-country pairs  *
	*-------------------------------------------------------*
	preserve
	use `main', clear
	keep if only_native == 1
	keep ingredient2 adm0
	rename adm0 nativeadm0
	duplicates drop
	tempfile nativepairs
	save `nativepairs', replace
	restore

	*-------------------------------------------------------*
	* 2. Load distance matrix                               *
	*-------------------------------------------------------*
	*use "${versatility}/distance_tradecosts_capitals.dta", clear
	use "${versatility}/distance_capital.dta", clear
	
	* Should contain: adm0 nativeadm0 dist1 dist2 dist3
	tempfile distances
	save `distances', replace

	*-------------------------------------------------------*
	* 3. Prepare empty container for results                *
	*-------------------------------------------------------*
	clear
	gen adm0 = ""
	gen ingredient2 = ""
	gen min_dist1 = .
	gen min_dist2 = .
	gen min_dist3 = .
	tempfile results
	save `results', replace

	*-------------------------------------------------------*
	* 4. Loop over each ingredient2                         *
	*-------------------------------------------------------*
	use `main', clear
	levelsof ingredient2, local(ings)

	foreach ing of local ings {
		di as text "Processing ingredient: `ing'"

		preserve
		keep if ingredient2 == "`ing'"
		tempfile subset
		save `subset', replace

		use `nativepairs', clear
		keep if ingredient2 == "`ing'"
		if _N == 0 {
			restore
			continue
		}

		tempfile nativesub
		save `nativesub', replace

		* Cross this ingredient's countries with its native origins
		use `subset', clear
		cross using `nativesub'

		* Merge in the three distance measures
		merge m:1 adm0 nativeadm0 using `distances', nogen keep(match)		
		
		* Compute minimum distances per adm0–ingredient
		bys adm0: egen min_distCapital = min(distance)
		bys adm0: egen min_distPreColumb = min(distance)
		bys adm0: egen min_distPostColumb = min(distance)
		*bys adm0: egen min_distPreColumb = min(lc_dist_preColumb)
		*bys adm0: egen min_distPostColumb = min(lc_dist_postColumb)
		keep adm0 ingredient2 min_distCapital min_distPreColumb min_distPostColumb
		duplicates drop

		append using `results'
		save `results', replace
		restore
	}

	*-------------------------------------------------------*
	* 5. Merge distances back to main data                  *
	*-------------------------------------------------------*
	use `main', clear
	merge m:1 adm0 ingredient2 using `results', nogen

	*-------------------------------------------------------*
	* 6. Create three sets of weights                       *
	*-------------------------------------------------------*
	foreach i in Capital PreColumb PostColumb {
		foreach hl_dist in 500 1000 2000 3000 {
		gen weight`i'_`hl_dist' = 1 if only_native == 1
		replace weight`i'_`hl_dist' = 1 / (1 + min_dist`i'/`hl_dist') if only_native == 0 & min_dist`i' < .
		}
	}

	*-------------------------------------------------------*
	* 7. Compute distance-weighted native spice versatility *
	*-------------------------------------------------------*
	foreach i in Capital PreColumb PostColumb {
		foreach hl_dist in 500 1000 2000 3000 {
		bys adm0: egen wsum`i'_`hl_dist' = total(weight`i'_`hl_dist') if spice==1
		gen w_rel`i'_`hl_dist' = weight`i'_`hl_dist'/wsum`i'_`hl_dist' if spice==1

		bys adm0: egen vers_dist`i'_`hl_dist' = mean(common*weight`i'_`hl_dist') if spice == 1
		sort adm0 native
		bys adm0 (vers_dist`i'_`hl_dist'): replace vers_dist`i'_`hl_dist' = vers_dist`i'_`hl_dist'[_n-1] if missing(vers_dist`i'_`hl_dist')
		
		* create food trading factor: for all spice-producing countries, we just weight by combinations of ingredient pairs by distance
		* measure of "food richness"? not taking into account their flavor potential we can also use as a placebo?
		bys adm0: egen trade_dist`i'_`hl_dist' = mean(1*weight`i'_`hl_dist') if spice == 1
		sort adm0 native
		bys adm0 (trade_dist`i'_`hl_dist'): replace trade_dist`i'_`hl_dist' = trade_dist`i'_`hl_dist'[_n-1] if missing(trade_dist`i'_`hl_dist')

		// bys adm0: egen native_spice_vers2_dist_rel`i'_`hl_dist' = mean(common*w_rel`i'_`hl_dist') if spice == 1
		// sort adm0 native
		// bys adm0 (native_spice_vers2_dist_rel`i'_`hl_dist'): replace native_spice_vers2_dist_rel`i'_`hl_dist' = native_spice_vers2_dist_rel`i'_`hl_dist'[_n-1] if missing(native_spice_vers2_dist_rel`i'_`hl_dist')
		}
	}

	
	
	* ------------------------------------------------------ *
	*  Assign 0 to adm0 without any native spices
	* ------------------------------------------------------ *
	bys adm0: egen has_native_spice = max(native == 1 & spice == 1)
	foreach var of varlist vers_dist* trade_dist* {
		replace `var' = 0 if has_native_spice == 0
	}
	drop has_native_spice
	
	keep adm0 vers_dist* trade_dist*
	duplicates drop
	
	foreach var of varlist vers_dist* trade_dist* {
		replace `var' = 0 if missing(`var')
	}
	
	*-------------------------------------------------------*
	* 8. Save output                                        *
	*-------------------------------------------------------*
	save "$versatility/native_versatility_m_c_dist_all.dta", replace
	
	
	