* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: April 14, 2025 						   	   *
*			New (composite) versatility calculation using relative weights
* **************************************************************************** *
	
	* ***************************************************** *
	
	import delim "${versatility}/imported/imported_p50_v2.csv", clear
	drop if ifnative == 1
	keep adm0 country ingredient
	duplicates drop adm0 country ingredient, force
	gen native = 0
	gen source = "imported"
	merge 1:m ingredient adm0 using "$recipes/2ingredient.dta", gen(imported_merge)
	keep if imported_merge == 3
	
	tempfile imported
	save `imported'
	
	use "${versatility}/native/native_clean_p50.dta", replace
	
	ren nativeadm0 adm0
	ren nativecountry country
	
	gen native = 1
	gen source = "native"
	
	merge 1:m ingredient adm0 using "$recipes/2ingredient.dta", gen(native_merge)
	keep if native_merge == 3
	
	append using `imported'
	
	
	
	ren ingredient ingredient1
	ren ingredient2 ingredient
	
	joinby ingredient using "${versatility}/native/native_clean_p50.dta"
	
	gen native2 = 1
	gen source2 = "native"
	
	drop if ingredient == ingredient1
	
	ren adm0 adm1 
	ren country country1
	ren nativeadm0 adm0
	
	tempfile  native
	save `native'
	
	use `imported', replace
	drop suitability ifnative ingredient2 _fillin imported_merge
	duplicates drop ingredient adm0, force
	
	save `imported', replace
	
	use `native', replace
	
	duplicates drop adm0 ingredient ingredient1, force
	
	merge m:1 adm0 ingredient using `imported', gen(imported2_merge)
	replace native2 = 0 if imported2_merge == 3
	replace source2 = "imported"
	
	drop if ingredient == ingredient1
	drop *_merge _fillin ifnative suitability
	
	save "$versatility/interim_all_versatility.dta", replace
	
	ren adm0 nativeadm0
	ren adm1 adm0
	ren (ingredient1 ingredient) (ingredient ingredient2)
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	keep if _merge == 3
	drop _merge
	**** Nothing missing here
	
	
	* Calculating weights
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"
	
	* generate weight
	gen weight = .
	
	** Calculate distance weight
	bys country ingredient: egen total_distance = total(distance)
	
	gen relative_distance = distance/total_distance
	replace weight = 1 - relative_distance
	
	gen ingredient_versatility = weight * common
	
	summ weight
	bys adm0: egen versatility = mean(ingredient_versatility)
	
	*Suitability
	gen native_suitability_factor = .
	replace native_suitability_factor = 2 if native == 1 & native2 == 1
	replace native_suitability_factor = 1 if native == 1 | native2 == 1
	
	tempfile 2ing_ni
	save `2ing_ni'
	
	use "$fao_suit\suitability_FAO.dta"
	
	preserve
	keep adm0 suitability ingredient
	drop if suitability == 0
	replace ingredient = strlower(ingredient)
	tempfile suitability1
	save `suitability1'
	restore
	
	preserve
	ren adm0 nativeadm0
	ren ingredient ingredient2
	keep nativeadm0 suitability ingredient2
	drop if suitability == 0
	ren suitability suitability2
	replace ingredient2 = strlower(ingredient2)
	tempfile suitability2
	save `suitability2'
	restore
	
	use `2ing_ni', replace
	
	merge m:1 adm0 ingredient using `suitability1', gen(suit1_merge)
	drop if suit1_merge == 2
	merge m:1 nativeadm0 ingredient2 using `suitability2', gen(suit2_merge)
	drop if suit2_merge == 2
	
	replace suitability = 0 if suitability == .
	replace suitability2 = 0 if suitability2 == .
	
	gen suitability_weight = suitability + suitability2
	replace suitability_weight = suitability_weight/2 if suitability != 0 & suitability2 != 0
	replace suitability_weight = 1 if native == 0 & native2 == 0
	
	gen weighted_versatility = ingredient_versatility * suitability_weight
	replace weighted_versatility = ingredient_versatility if weighted_versatility == .
	
	bys adm0: egen suit_versatility = mean(weighted_versatility)
	
	keep adm0 versatility suit_versatility
	duplicates drop adm0, force
	save "$versatility/all_versatility.dta", replace