   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile creates imported versatility files   		  *
   *																	  *
   * - Inputs: "${versatility}/imported/imported_`x'.csv"              	  *
   *           "${versatility}/common_flavor_clean.dta"      			  *
   *           "${versatility}/native/native_clean_`x'.dta"         			  *
   *           "${versatility}/distance_capital.dta"         			  *
   * - Output: "${versatility}/imported/importbycountry_`x'.dta"      	  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 17, 2023

****************************************
* Generate imported flavor versatility by country
****************************************

clear 

foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66"  "p70"{ 
	
* imported data
import delimited "${versatility}/imported/imported_`x'.csv", clear // we need to have also native ingredients, fix this in code 8

* keep variables
keep adm0 ingredient suitability country ifnative

tempfile all
save `all'

* initialize the output data
preserve
keep if adm0 == "ZWE"

* generate every combination of ingredients
gen ingredient2 = ingredient
fillin ingredient ingredient2

* fill in missing values by group
foreach var of varlist adm0 country{
	bysort ingredient(`var'): replace `var' = `var'[_N]
}

foreach var of varlist suitability ifnative{
	bysort ingredient(`var'): replace `var' = `var'[_n-1] if missing(`var')	
}

* drop pairs that contain same ingredients
drop if ingredient == ingredient2
drop _fillin

* generate suitability of ingredient2
gen suitability2 = .

levelsof ingredient, local(ing)
foreach i of local ing{
	sum suitability if ingredient == "`i'"
	local s = r(mean)
	replace suitability2 = `s' if ingredient2 == "`i'"
}

* generate ifnative of ingredient2
gen ifnative2 = .

levelsof ingredient, local(ing)
foreach i of local ing{
	sum ifnative if ingredient == "`i'"
	local s = r(mean)
	replace ifnative2 = `s' if ingredient2 == "`i'"
}

* get common flavors 
merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
count if _merge == 3
	dis "`l'"
	
	if r(N) == 0{
		continue
	}
keep if _merge == 3
drop _merge index

* generate weight
gen weight = .
replace weight = 1 if ifnative2 == 1

** calculate the distance between the country and origin of the ingredient2
rename (ingredient ingredient2) (ingredientrow ingredient)
joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

count 

if r(N) == 0{
	continue
	
}
** keep the nearest distance
sort ingredientrow ingredient distance
bysort ingredientrow ingredient: gen num = _n
keep if num == 1
drop num

replace weight = 1/distance if missing(weight)

** generate normalized weight
qui sum weight
gen norm_weight = (weight - r(min))/(r(max) - r(min))


* generate weighted average
gen weightcommon = norm_weight * common
drop common
rename (weightcommon ingredientrow ingredient) (common ingredient ingredient2)

collapse (first)adm0 (first)country (mean)common (mean)ifnative, by(ingredient)
keep if ifnative == 0
drop ifnative

* calculate the distance between the country and origin of the ingredient
joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

* calculate imported versatility
** keep the nearest distance
sort ingredient distance
bysort ingredient: gen num = _n
keep if num == 1
drop num

gen commondistance = 1/distance * common
collapse (first)adm0 (first)country (mean)commondistance
rename commondistance importVersatility

save "${versatility}/imported/importbycountry_v2_`x'.dta", replace
restore

* loop through rest of countries
levelsof adm0, local(level)
foreach l of local level{
	use `all', clear
	keep if adm0 == "`l'"
	
	* generate every combination of ingredients
	gen ingredient2 = ingredient
	fillin ingredient ingredient2

	* fill in missing values by group
	foreach var of varlist adm0 country{
		bysort ingredient(`var'): replace `var' = `var'[_N]
	}

	foreach var of varlist suitability ifnative{
		bysort ingredient(`var'): replace `var' = `var'[_n-1] if missing(`var')	
	}

	* drop pairs that contain same ingredients
	drop if ingredient == ingredient2
	drop _fillin

	* generate suitability of ingredient2
	gen suitability2 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
		sum suitability if ingredient == "`i'"
		local s = r(mean)
		replace suitability2 = `s' if ingredient2 == "`i'"
	}
	
	* generate ifnative of ingredient2
	gen ifnative2 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
	sum ifnative if ingredient == "`i'"
	local s = r(mean)
	replace ifnative2 = `s' if ingredient2 == "`i'"
	}

	merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
	if r(N) == 0{
		continue
	}
	keep if _merge == 3
	drop _merge index

	* generate weight
	gen weight = .
	replace weight = 1 if ifnative2 == 1

	** calculate the distance between the country and origin of the ingredient2
	rename (ingredient ingredient2) (ingredientrow ingredient)
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	count 

	if r(N) == 0{
	continue
	
	}

	** keep the nearest distance
	sort ingredientrow ingredient distance
	bysort ingredientrow ingredient: gen num = _n
	keep if num == 1
	drop num

	replace weight = 1/distance if missing(weight)

	** generate normalized weight
	qui sum weight
	gen norm_weight = (weight - r(min))/(r(max) - r(min))


	* generate weighted average
	gen weightcommon = norm_weight * common
	drop common
	rename (weightcommon ingredientrow ingredient) (common ingredient ingredient2)

	collapse (first)adm0 (first)country (mean)common (mean)ifnative, by(ingredient)
	count if ifnative == 0
	if r(N) == 0{
		continue
	}
	keep if ifnative == 0
	drop ifnative

	* calculate the distance between the country and origin of the ingredient
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	dis "`l'"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	* calculate imported versatility
	** keep the nearest distance
	sort ingredient distance
	bysort ingredient: gen num = _n
	keep if num == 1
	drop num

	gen commondistance = 1/distance * common
	collapse (first)adm0 (first)country (mean)commondistance
	rename commondistance importVersatility
	
	* append to original data 
	append using "${versatility}/imported/importbycountry_v2_`x'.dta" 
	save "${versatility}/imported/importbycountry_v2_`x'.dta", replace
}


* drop duplicates
duplicates drop

save "${versatility}/imported/importbycountry_`x'.dta", replace

}
