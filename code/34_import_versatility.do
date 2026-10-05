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
	* 2. Load distance matrices                              *
	*-------------------------------------------------------*
	use "${versatility}/distance_capital.dta", clear
	keep adm0 nativeadm0 distance
	tempfile distances_capital
	save `distances_capital', replace

	use "${versatility}/distance_tradecosts_capitals.dta", clear
	keep adm0 nativeadm0 lc_dist_preColumb lc_dist_postColumb
	tempfile distances_columb
	save `distances_columb', replace
	
	
	*-------------------------------------------------------*
	* 2b. Generic (non-ingredient-specific) trade centrality *
	*-------------------------------------------------------*
	use `distances_capital', clear
	foreach hl_dist in 500 1000 2000 3000 {
		gen centralityCapital_`hl_dist' = 1 / (1 + distance/`hl_dist')
	}
	collapse (mean) centralityCapital_500 centralityCapital_1000 ///
		centralityCapital_2000 centralityCapital_3000, by(adm0)
	tempfile centrality_capital
	save `centrality_capital', replace

	use `distances_columb', clear
	foreach hl_dist in 500 1000 2000 3000 {
		gen centralityPreColumb_`hl_dist'  = 1 / (1 + lc_dist_preColumb/`hl_dist')
		gen centralityPostColumb_`hl_dist' = 1 / (1 + lc_dist_postColumb/`hl_dist')
	}
	collapse (mean) centralityPreColumb_500 centralityPreColumb_1000 ///
		centralityPreColumb_2000 centralityPreColumb_3000 ///
		centralityPostColumb_500 centralityPostColumb_1000 ///
		centralityPostColumb_2000 centralityPostColumb_3000, by(adm0)
	tempfile centrality_columb
	save `centrality_columb', replace
	
	*-------------------------------------------------------*
	* 2c. Population-weighted market access (Harris 1954)    *
	*-------------------------------------------------------*
	use "${codedata}/population/populationlong2019.dta", clear
	keep adm0 population
	duplicates drop adm0, force
	rename adm0 nativeadm0
	rename population pop_native
	tempfile poplookup
	save `poplookup', replace

	use `distances_capital', clear
	drop if adm0 == nativeadm0 | distance <= 0
	merge m:1 nativeadm0 using `poplookup', keep(match) nogen
	gen w_ma = pop_native / distance
	collapse (sum) w_ma, by(adm0)
	rename w_ma marketaccessCapital
	tempfile marketaccess_capital
	save `marketaccess_capital', replace

	use `distances_columb', clear
	drop if adm0 == nativeadm0
	merge m:1 nativeadm0 using `poplookup', keep(match) nogen
	gen w_maPre  = pop_native / lc_dist_preColumb
	gen w_maPost = pop_native / lc_dist_postColumb
	collapse (sum) w_maPre w_maPost, by(adm0)
	rename w_maPre  marketaccessPreColumb
	rename w_maPost marketaccessPostColumb
	tempfile marketaccess_columb
	save `marketaccess_columb', replace
	

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

		* Merge in the inter-capital distance
		merge m:1 adm0 nativeadm0 using `distances_capital', nogen keep(match)

		* Merge in pre/post-Columbian distances (fewer pairs — keep master rows regardless)
		merge m:1 adm0 nativeadm0 using `distances_columb', nogen keep(master match)

		* Compute minimum distances per adm0–ingredient
		bys adm0: egen min_distCapital = min(distance)
		bys adm0: egen min_distPreColumb = min(lc_dist_preColumb)
		bys adm0: egen min_distPostColumb = min(lc_dist_postColumb)
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
	* 7. Compute distance-weighted versatility               *
	*    (a) spice-only, as before                           *
	*    (b) NEW: full set of native ingredients              *
	*-------------------------------------------------------*
	foreach i in Capital PreColumb PostColumb {
		foreach hl_dist in 500 1000 2000 3000 {

		*----- (a) spice-only -----
		bys adm0: egen wsum`i'_`hl_dist' = total(weight`i'_`hl_dist') if spice==1
		gen w_rel`i'_`hl_dist' = weight`i'_`hl_dist'/wsum`i'_`hl_dist' if spice==1

		bys adm0: egen vers_dist`i'_`hl_dist' = mean(common*weight`i'_`hl_dist') if spice == 1
		sort adm0 native
		bys adm0 (vers_dist`i'_`hl_dist'): replace vers_dist`i'_`hl_dist' = vers_dist`i'_`hl_dist'[_n-1] if missing(vers_dist`i'_`hl_dist')

		bys adm0: egen trade_dist`i'_`hl_dist' = mean(1*weight`i'_`hl_dist') if spice == 1
		sort adm0 native
		bys adm0 (trade_dist`i'_`hl_dist'): replace trade_dist`i'_`hl_dist' = trade_dist`i'_`hl_dist'[_n-1] if missing(trade_dist`i'_`hl_dist')

		*----- (b) NEW: all native ingredients, not just spices -----
		bys adm0: egen versAll_dist`i'_`hl_dist' = mean(common*weight`i'_`hl_dist') if !missing(weight`i'_`hl_dist')
		sort adm0 native
		bys adm0 (versAll_dist`i'_`hl_dist'): replace versAll_dist`i'_`hl_dist' = versAll_dist`i'_`hl_dist'[_n-1] if missing(versAll_dist`i'_`hl_dist')

		bys adm0: egen tradeAll_dist`i'_`hl_dist' = mean(1*weight`i'_`hl_dist') if !missing(weight`i'_`hl_dist')
		sort adm0 native
		bys adm0 (tradeAll_dist`i'_`hl_dist'): replace tradeAll_dist`i'_`hl_dist' = tradeAll_dist`i'_`hl_dist'[_n-1] if missing(tradeAll_dist`i'_`hl_dist')
		}
	}

	
	* ------------------------------------------------------ *
	*  Assign 0 to adm0 without any native spices (spice-only vars)
	* ------------------------------------------------------ *
	bys adm0: egen has_native_spice = max(native == 1 & spice == 1)
	foreach var of varlist vers_dist* trade_dist* {
		replace `var' = 0 if has_native_spice == 0
	}
	drop has_native_spice

	keep adm0 vers_dist* trade_dist* versAll_dist* tradeAll_dist*
	duplicates drop

	merge 1:1 adm0 using `centrality_capital', nogen
	merge 1:1 adm0 using `centrality_columb', nogen
	merge 1:1 adm0 using `marketaccess_capital', nogen
	merge 1:1 adm0 using `marketaccess_columb', nogen

	foreach var of varlist vers_dist* trade_dist* versAll_dist* tradeAll_dist* centrality* marketaccess* {
		replace `var' = 0 if missing(`var')
	}

	*-------------------------------------------------------*
	* 8. Save output                                        *
	*-------------------------------------------------------*
	save "$versatility/native_versatility_m_c_dist_all.dta", replace
	
	