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
	
	*********************
	* For Milla database
	*********************
{
/*	
local x "p50"
	
	* imported data
	import delimited "${versatility}/imported/imported_`x'_v2_m.csv", clear 
	gen imported = 1
	
	append using "${versatility}/native/native_clean_p50_m.dta"
	replace imported = 0 if imported == .
	replace country = nativecountry if country == ""
	replace adm0 = nativeadm0 if adm0== ""
	
	* keep variables
	keep adm0 ingredient suitability country imported
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
	
	bys adm0 ingredient (suitability): replace suitability = suitability[_n-1] if missing(suitability)
	bys adm0 ingredient (imported): replace imported = imported[_n-1] if missing(imported)
	gen imported2 = 0 if ingredient == ingredient2 & imported == 0
	bys adm0 ingredient2 (imported2): replace imported2 = imported2[_n-1] if missing(imported2)
	replace imported2 = 1 if imported2 == .
	bys adm0 (country): replace country = country[_N] if missing(country)

	save "${versatility}/2ingredient_m.dta", replace
*/
}
	***************************
	* For Milla database + CIAT
	***************************
	
local x "p50"
	
	* imported data
	import delimited "${versatility}/imported/imported_`x'_v2_m_c.csv", clear 
	gen imported = 1
	
	append using "${versatility}/native/native_clean_p50_m_c.dta"
	replace imported = 0 if imported == .
	replace country = nativecountry if country == ""
	replace adm0 = nativeadm0 if adm0== ""
	
	* keep variables
	keep adm0 ingredient suitability country imported
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

	bys adm0 ingredient (suitability): replace suitability = suitability[_n-1] if missing(suitability)
	bys adm0 ingredient (imported): replace imported = imported[_n-1] if missing(imported)
	gen imported2 = 0 if ingredient == ingredient2 & imported == 0
	bys adm0 ingredient2 (imported2): replace imported2 = imported2[_n-1] if missing(imported2)
	replace imported2 = 1 if imported2 == .
	bys adm0 (country): replace country = country[_N] if missing(country)

	save "${versatility}/2ingredient_m_c.dta", replace