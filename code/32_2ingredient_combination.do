* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				New Versatility Calculation
* **************************************************************************** *

	* ***************************************************** *
	
	local x "p50"
	
	* imported data
	import delimited "${versatility}/imported/imported_`x'_v2.csv", clear 

	* keep variables
	keep adm0 ingredient suitability country ifnative
	duplicates drop adm0 ingredient suitability, force
	
	preserve
	keep if country == "zzz"
	tempfile bycountry
	save `bycountry', emptyok
	restore
	
	
	* Generating every combination of ingredients
	levelsof adm0, local(country)
	* initialize the output data
	foreach c of local country {
		preserve
	keep if adm0 == "`c'"

	gen ingredient2 = ingredient
	fillin ingredient ingredient2
	replace adm0 = "`c'" if adm0 == ""
	append using `bycountry', force
	save `bycountry', replace
	restore
	}
	use `bycountry', replace
	save "${versatility}/2ingredient.dta", replace
	
	***************************************
	* For Milla database + CIAT only native
	***************************************
	
	use "${versatility}/common_flavor_clean_m_c.dta", clear
	keep ingredient
	duplicates drop
	tempfile ing
	save `ing'

	use "${versatility}/native/native_clean_p50_m_c.dta", clear
	rename nativecountry country
	rename nativeadm0 adm0
	
	*- Keep only ingredients in common flavor data
	merge m:1 ingredient using `ing'
	keep if _merge == 3 // we lose 13 countries
	
	* keep variables
	keep adm0 ingredient country
	
	* Create all possible combinations of ingredients 
	preserve
	keep ingredient
	duplicates drop 
	gen ingredient2 = ingredient
	fillin ingredient ingredient2
	tempfile ingredients
	save `ingredients', replace
	restore
	
	* Generating every combination 
	duplicates drop adm0 country, force
	tempfile countries
	save `countries'

	tempfile bycountry
	save `bycountry', emptyok
	
	use `countries', clear
	levelsof adm0, local(adm0s)

	* initialize the output data
	foreach c of local adm0s {
		preserve
		keep if adm0 == "`c'"
		local ctry = country[1]  
		restore
	
		preserve
		use `ingredients', clear
		gen adm0 = "`c'"
		gen country = "`ctry'"
		append using `bycountry'
		save `bycountry', replace
		restore
	}
	
	use `bycountry', replace

	save "${versatility}/2ingredient_m_c.dta", replace
