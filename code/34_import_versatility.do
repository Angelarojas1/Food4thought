* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Steve Berggreen
* 				Last date modified: November 10, 2025 					 	   *
*			Distance-weighted import versatility instrument using spices only
* **************************************************************************** *

use "$versatility/native_versatility_m_c.dta",  clear
	
	ren (ingredient1 ingredient) (ingredient ingredient2)
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean_m_c.dta"
	keep if _merge == 3
	drop _merge
	
	/*
	
	*- Paste lat and lon information
	preserve 
	use "${versatility}/distance_capital.dta", clear
	keep adm0 lat lon
	duplicates drop
	tempfile coordinates
	save `coordinates'
	restore
	
	* Calculating weights
	merge m:1 adm0 using `coordinates'
	keep if _merge == 3 // drop countries that are not in data
	
	*-----------------------------*
	*     Native versatility      *
	*-----------------------------*
	
	* native versatility
	bys adm0: egen native_versatility = mean(common) if only_native == 1
	sort adm0 native
	bys adm0 (native_versatility): replace native_versatility = native_versatility[_n-1] if missing(native_versatility)
	
	// Some countries don't have native versatility because they only have 1
	// native ingredient.
	*replace native_versatility = 0 if native_versatility == .
	
	* native versatility 2
	bys adm0: egen native_versatility2 = mean(common) 
	sort adm0 native
		
	*-----------------------------------*
	*     Native versatility - SPICES   *
	*-----------------------------------*
	
	* native versatility
	bys adm0: egen native_spice_vers = mean(common) if only_native == 1 & spice == 1
	sort adm0 native
	bys adm0 (native_spice_vers): replace native_spice_vers = native_spice_vers[_n-1] if missing(native_spice_vers)

	* native versatility 2
	bys adm0: egen native_spice_vers2 = mean(common) if spice == 1
	sort adm0 native
	bys adm0 (native_spice_vers2): replace native_spice_vers2 = native_spice_vers2[_n-1] if missing(native_spice_vers2)
	
	*/
	
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
	use "${versatility}/distance_tradecosts_capitals.dta", clear
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
		bys adm0: egen min_dist1 = min(distance)
		bys adm0: egen min_dist2 = min(lc_dist_preColumb)
		bys adm0: egen min_dist3 = min(lc_dist_postColumb)
		keep adm0 ingredient2 min_dist1 min_dist2 min_dist3
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
	forvalues i = 1/3 {
		foreach hl_dist in 500 1000 2000 3000 {
		gen weight`i'_`hl_dist' = 1 if only_native == 1
		replace weight`i'_`hl_dist' = 1 / (1 + min_dist`i'/`hl_dist') if only_native == 0 & min_dist`i' < .
		}
	}

	*-------------------------------------------------------*
	* 7. Compute distance-weighted native spice versatility *
	*-------------------------------------------------------*
	forvalues i = 1/3 {
		foreach hl_dist in 500 1000 2000 3000 {
		bys adm0: egen wsum`i'_`hl_dist' = total(weight`i'_`hl_dist') if spice==1
		gen w_rel`i'_`hl_dist' = weight`i'_`hl_dist'/wsum`i'_`hl_dist' if spice==1

		bys adm0: egen native_spice_vers2_dist`i'_`hl_dist' = mean(common*weight`i'_`hl_dist') if spice == 1
		sort adm0 native
		bys adm0 (native_spice_vers2_dist`i'_`hl_dist'): replace native_spice_vers2_dist`i'_`hl_dist' = native_spice_vers2_dist`i'_`hl_dist'[_n-1] if missing(native_spice_vers2_dist`i'_`hl_dist')
		
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

	keep adm0 native_spice_vers2*
	duplicates drop
	
	*-------------------------------------------------------*
	* 8. Save output                                        *
	*-------------------------------------------------------*
	save "$versatility/native_versatility_m_c_dist_all.dta", replace
	
	
	