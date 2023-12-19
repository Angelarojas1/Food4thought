   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *            This dofile creates native versatility files        	  *
   *																	  *
   * - Inputs: "${versatility}/native/native_`x'.csv"              		  *
   *           "${versatility}/common_flavor_clean.dta"     			  *
   *           "${versatility}/common_flavor_3ing_clean.dta"  			  *
   * - Output: "${versatility}/native/nativebycountry_`x'_g2simple.dta"	  * 
   *		   "${versatility}/native/nativebycountry_`x'_g3weight.dta"   *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 17, 2023
   
****************************************
* Generate native flavor versatility by country
****************************************

*********************************************
* 2 ingredients as a group, simple average 
*********************************************

foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	
* import data
import delimited "${versatility}/native/native_`x'.csv", clear 

* keep variables
keep adm0 ingredient country

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

* drop pairs that contain same ingredients
drop if ingredient == ingredient2
drop _fillin

* get common flavors 
merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
keep if _merge == 3
drop _merge index

* calculate native flavor versatility
collapse (first)adm0 (first)country (mean)common

rename common nativeVersatility

save "${versatility}/native/nativebycountry_`x'_g2simple.dta", replace

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

	* drop pairs that contain same ingredients
	drop if ingredient == ingredient2
	drop _fillin

	* get common flavors 
	merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
	dis "`l'"
	
	if `r(N)' == 0{
		continue
	}
	
	keep if _merge == 3
	drop _merge index

	* calculate native flavor versatility
	collapse (first)adm0 (first)country (mean)common
	rename common nativeVersatility
	
	* append to original data 
	append using "${versatility}/native/nativebycountry_`x'_g2simple.dta" 
	save "${versatility}/native/nativebycountry_`x'_g2simple.dta", replace
}


* drop duplicates
duplicates drop
save "${versatility}/native/nativebycountry_`x'_g2simple.dta", replace
}

******************************************************
* 2 ingredients as a group, weighted with suitability
******************************************************

foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	
* import data
import delimited "${versatility}/native/native_`x'.csv", clear 

* keep variables
keep adm0 ingredient suitability country

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
bysort ingredient(suitability): replace suitability = suitability[_n-1] if missing(suitability)

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

* get common flavors 
merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
keep if _merge == 3
drop _merge index

* calculate native flavor versatility
gen commonSuit2 = common * suitability2

collapse (first)adm0 (first)country (mean)suitability (mean)commonSuit2, by(ingredient)
gen commonSuit2Suit = commonSuit2 * suitability

collapse (first)adm0 (first)country (mean)commonSuit2Suit
rename commonSuit2Suit nativeVersatility

save "${versatility}/native/nativebycountry_`x'_g2weight.dta", replace

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
	bysort ingredient(suitability): replace suitability = suitability[_n-1] if missing(suitability)

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

	* get common flavors 
	merge 1:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
	dis "`l'"
	
	if r(N) == 0{
		continue
	}
	
	keep if _merge == 3
	drop _merge index

	* calculate native flavor versatility
	gen commonSuit2 = common * suitability2

	collapse (first)adm0 (first)country (mean)suitability (mean)commonSuit2, by(ingredient)
	gen commonSuit2Suit = commonSuit2 * suitability

	collapse (first)adm0 (first)country (mean)commonSuit2Suit
	rename commonSuit2Suit nativeVersatility
	
	* append to original data 
	append using "${versatility}/native/nativebycountry_`x'_g2weight.dta" 
	save "${versatility}/native/nativebycountry_`x'_g2weight.dta", replace
}


* drop duplicates
duplicates drop
save "${versatility}/native/nativebycountry_`x'_g2weight.dta", replace
}

********************************************
* 3 ingredients as a group, simple average
********************************************

foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
	
* import data
import delimited "${versatility}/native/native_`x'.csv", clear 

* keep variables
keep adm0 ingredient country

tempfile all
save `all'

* initialize the output data
preserve 
keep if adm0 == "ZWE"

* generate every combination of ingredients
gen ingredient2 = ingredient
gen ingredient3 = ingredient
fillin ingredient ingredient2 ingredient3

* fill in missing values by group
foreach var of varlist adm0 country{
	bysort ingredient(`var'): replace `var' = `var'[_N]
}

* drop pairs that contain same ingredients
drop if _fillin == 0
drop _fillin

* get common flavors 
merge 1:1 ingredient ingredient2 ingredient3 using "${versatility}/common_flavor_3ing_clean.dta"
keep if _merge == 3
drop _merge index

* calculate native flavor versatility
collapse (first)adm0 (first)country (mean)common
rename common nativeVersatility

save "${versatility}/native/nativebycountry_`x'_g3simple.dta", replace

restore

* loop through rest of countries
levelsof adm0, local(level)
foreach l of local level{
	use `all', clear
	
	keep if adm0 == "`l'"
	
	* generate every combination of ingredients
	gen ingredient2 = ingredient
	gen ingredient3 = ingredient
	fillin ingredient ingredient2 ingredient3

	* fill in missing values by group
	foreach var of varlist adm0 country{
		bysort ingredient(`var'): replace `var' = `var'[_N]
	}

	* drop pairs that contain same ingredients
	drop if _fillin == 0
	drop _fillin

	* get common flavors 
	merge 1:1 ingredient ingredient2 ingredient3 using "${versatility}/common_flavor_3ing_clean.dta"
	count if _merge == 3
	dis "`l'"
	
	if r(N) == 0{
		continue
	}
	
	keep if _merge == 3
	drop _merge index

	* calculate native flavor versatility
	collapse (first)adm0 (first)country (mean)common, by(ingredient)
	collapse (first)adm0 (first)country (mean)common
	rename common nativeVersatility
	
	* append to original data 
	append using "${versatility}/native/nativebycountry_`x'_g3simple.dta" 
	save "${versatility}/native/nativebycountry_`x'_g3simple.dta", replace
}


* drop duplicates
duplicates drop
save "${versatility}/native/nativebycountry_`x'_g3simple.dta", replace
}

********************************************
* 3 ingredients as a group, weighted average
********************************************

foreach x in "p0" "p10" "p25" "p50" "p60" "p70"{
* import data
import delimited "${versatility}/native/native_`x'.csv", clear 

* keep variables
keep adm0 ingredient country suitability

tempfile all
save `all'

* initialize the output data
preserve 
keep if adm0 == "ZWE"

* generate every combination of ingredients
gen ingredient2 = ingredient
gen ingredient3 = ingredient
fillin ingredient ingredient2 ingredient3

* fill in missing values by group
foreach var of varlist adm0 country{
	bysort ingredient(`var'): replace `var' = `var'[_N]
}

bysort ingredient(suitability): replace suitability = suitability[_n-1] if missing(suitability)


* drop pairs that contain same ingredients
drop if _fillin == 0
drop _fillin

* generate suitability of ingredient2 and ingredient3
gen suitability2 = .

levelsof ingredient, local(ing)
foreach i of local ing{
	sum suitability if ingredient == "`i'"
	local s = r(mean)
	replace suitability2 = `s' if ingredient2 == "`i'"
}

gen suitability3 = .

levelsof ingredient, local(ing)
foreach i of local ing{
	sum suitability if ingredient == "`i'"
	local s = r(mean)
	replace suitability3 = `s' if ingredient3 == "`i'"
}


* get common flavors 
merge 1:1 ingredient ingredient2 ingredient3 using "${versatility}/common_flavor_3ing_clean.dta"
keep if _merge == 3
drop _merge index

* calculate native flavor versatility
gen weight = suitability * suitability2 * suitability3

sum weight
gen stdweight = weight/r(sum)

gen weightcommon = stdweight * common

collapse (first)adm0 (first)country (mean)weightcommon
rename weightcommon nativeVersatility

save "${versatility}/native/nativebycountry_`x'_g3weight.dta", replace

restore

* loop through rest of countries
levelsof adm0, local(level)
foreach l of local level{
	use `all', clear
	
	keep if adm0 == "`l'"
	
	* generate every combination of ingredients
	gen ingredient2 = ingredient
	gen ingredient3 = ingredient
	fillin ingredient ingredient2 ingredient3

	* fill in missing values by group
	foreach var of varlist adm0 country{
		bysort ingredient(`var'): replace `var' = `var'[_N]
	}
	bysort ingredient(suitability): replace suitability = suitability[_n-1] if missing(suitability)


	* drop pairs that contain same ingredients
	drop if _fillin == 0
	drop _fillin
	
	* generate suitability of ingredient2 and ingredient3
	gen suitability2 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
	sum suitability if ingredient == "`i'"
	local s = r(mean)
	replace suitability2 = `s' if ingredient2 == "`i'"
	}

	gen suitability3 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
	sum suitability if ingredient == "`i'"
	local s = r(mean)
	replace suitability3 = `s' if ingredient3 == "`i'"
	}


	* get common flavors 
	merge 1:1 ingredient ingredient2 ingredient3 using "${versatility}/common_flavor_3ing_clean.dta"
	count if _merge == 3
	dis "`l'"
	
	if r(N) == 0{
		continue
	}
	
	keep if _merge == 3
	drop _merge index

	* calculate native flavor versatility
	gen weight = suitability * suitability2 * suitability3

	sum weight
	gen stdweight = weight/r(sum)

	gen weightcommon = stdweight * common
	
	collapse (first)adm0 (first)country (mean)weightcommon
	rename weightcommon nativeVersatility

	
	* append to original data 
	append using "${versatility}/native/nativebycountry_`x'_g3weight.dta" 
	save "${versatility}/native/nativebycountry_`x'_g3weight.dta", replace
}


* drop duplicates
duplicates drop
save "${versatility}/native/nativebycountry_`x'_g3weight.dta", replace


}

