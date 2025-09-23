* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: April 14, 2025 						   	   *
*			New (composite) versatility calculation using relative weights
* **************************************************************************** *
	
	* ***************************************************** *
	*				Milla database							*
	* ***************************************************** *

	use "${versatility}/native/native_clean_p50_m_c.dta", replace
	
	ren nativeadm0 adm0
	ren nativecountry country
	
	gen native = 1
	gen source = "native"
	
	merge 1:m ingredient adm0 using "${versatility}/2ingredient_m_c.dta", gen(native_merge)
	keep if native_merge == 3
	drop if _fillin == 0 | _fillin == . // drop the same ingredient
	*keep if imported2 == 0 // combinations native native
	
	ren ingredient ingredient1 // native 
	ren ingredient2 ingredient // other ing in the database
	
	joinby ingredient using "${versatility}/native/native_clean_p50_m_c.dta" // identify native country of ingredient 2
	gen only_native = (country == nativecountry) // identify combinations between only native ingredients

	*ren nativecountry country1
	*ren nativeadm0 adm1

	drop _fillin native_merge native_merge nativeadm0 nativecountry
	duplicates drop 
	
	* If we have duplicates, keep native one
	bysort adm0 country ingredient1 ingredient (only_native): gen keep = (_n == _N)
	drop if keep == 0 
	drop keep

	*- Organize abovecutoff
	save "$versatility/native_versatility_m_c.dta", replace
	
	use "$versatility/native_versatility_m_c.dta",  clear
	
	ren (ingredient1 ingredient) (ingredient ingredient2)
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean_m_c.dta"
	keep if _merge == 3
	drop _merge
	
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
	keep if _merge == 3 // drop countries that are not in recipe database
	
	* native versatility
	bys adm0: egen native_versatility = mean(common) if only_native == 1
	sort adm0 native
	bys adm0 (native_versatility): replace native_versatility = native_versatility[_n-1] if missing(native_versatility)
	
	// Some countries don't have native versatility because they only have 1
	// native ingredient.
	replace native_versatility = 0 if native_versatility == .
	
	* native versatility 2
	bys adm0: egen native_versatility2 = mean(common) 
	sort adm0 native
	
	* Suitability measure
	merge m:1 adm0 ingredient using "${versatility}/cuisine_suit_m_c.dta", gen(suit_merge)
	drop if suit_merge == 2
		
	* Get suitability just once
	bys adm0 ingredient (suitability): gen suitability_unique = suitability[_n==1]
	replace suitability_unique = 0 if suitability_unique == .

	* Total suitability country
	egen sum_suitability = total(suitability_unique), by(adm0)
	
	* Create weighted
	gen weight = suitability/sum_suitability
	
	gen weighted_versatility = native_versatility2 * weight	
	bys adm0: egen suit_versatility = mean(weighted_versatility)
	
	bys adm0: egen avg_suitability = mean(suitability)
	
	keep adm0 country region continent numNative numNativeCIAT lat lon native_versatility native_versatility2 avg_suitability suit_versatility
	duplicates drop 
	save "$versatility/native_versatility_m_c.dta", replace