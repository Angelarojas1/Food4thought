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
	save "$outputs/2ingredient.dta", replace
