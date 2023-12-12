*****************************
*** Merge Recipes
*****************************

* Read in alll csv file in the precode folder *******************
* initialize an empty data file
tempfile recipe
save `recipe', emptyok

* read in all csv file 
local files: dir "${precodedata}/recipes/final" files "*.csv"
dis `files'

local numfiles : word count `files'
di "`numfiles'"
note: There are `numfiles' countries with recipes.

foreach file in `files'{
	di _newline "PROCESS: `file'"
	
	* import data
	import delimited using "${precodedata}/recipes/final/`file'", bindquote(strict) maxquotedrows(0) varnames(1) case(lower) stringcols(_all) encoding("utf-8") clear
	
	* generate raworder
	gen raword = _n
	
	* generate source
	gen src = "`file'"
	
	* save data
	append using `recipe'
	save `recipe', replace
}

use `recipe', clear
save "${codedata}/recipes/recipe_working.dta", replace

* Check variables *************************************************
* import data
use "${codedata}/recipes/recipe_working.dta", clear
describe, full
drop v1 unnamed01

* convert string to numeric
destring totaltime numberofingredients numberofspices, replace 

* generate country
split src, parse(".")
rename src1 country
assert !missing(country)

unique country

replace country = proper(country)

* correct country names
replace country = "Bahamas, The" if country == "Bahamas"
replace country = "Bosnia and Herzegovina" if country == "Bosnia And Herzegovina"
replace country = "Cote d'Ivoire" if country == "Cote D'Ivoire"
replace country = "Egypt, Arab Rep." if country == "Egypt"
replace country = "Iran, Islamic Rep." if country == "Iran"
replace country = "Kyrgyz Republic" if country == "Kyrgyzstan"
replace country = "Lao PDR" if country == "Laos"
replace country = "Korea, Dem. People's Rep." if country == "North Korea"
replace country = "Russian Federation" if country == "Russia"
replace country = "Slovak Republic" if country == "Slovakia"
replace country = "Korea, Rep." if country == "South Korea"
replace country = "Syrian Arab Republic" if country == "Syria"
replace country = "Venezuela, RB" if country == "Venezuela"


** drop recipes that the total time are higher than 99%
bys country: egen p99 = pctile(totaltime), p(99)
drop if totaltime > p99
note: `r(N_drop)' recipes are dropped because of higher than 99%.

* Read data with country code information
preserve

* import FLFP dataset
import delimited "${rawdata}/flfp/FLFP.csv", encoding(UTF-8) varnames(1) case(lower) clear

** countryname cannot uniquely identify the observations, drop duplicate rows
cap noisily isid countryname
bysort countryname: gen id = _n
tab id
assert inlist(id, 1, 2)
bys countryname: egen flag = max(id == 2)
list countryname continent_name if flag == 1, sepby(countryname)
drop if flag == 1 & continent_name == "Europe"
isid countryname

** rename variables
rename countryname country
keep country continent_name continent_code two_letter_country_code three_letter_country_code

tempfile adm 
save `adm'

restore

merge m:1 country using `adm'
tab _merge
assert inlist(_merge, 1, 2, 3)

tab country if _merge == 1
assert country == "Kosovo" if _merge == 1

keep if _merge == 3 | _merge == 1
drop _merge


** collapse to country level
gen cnt = 1
collapse (p10)time_p10 = totaltime (p25)time_p25 = totaltime (median)time_median = totaltime (p75)time_p75 = totaltime  (p90)time_p90 = totaltime  (mean)time_mean = totaltime  ///
(p10)ingredients_p10 = numberofingredients (p25)ingredients_p25 = numberofingredients (median)ingredients_median = numberofingredients (p75)ingredients_p75 = numberofingredients  (p90)ingredients_p90 = numberofingredients (mean)ingredients_mean = numberofingredients ///
(p10)spices_p10 = numberofspices (p25)spices_p25 = numberofspices (median)spices_median = numberofspices (p75)spices_p75 = numberofspices  (p90)spices_p90 = numberofspices (mean)spices_mean = numberofspices ///
(sum)num_recipes = cnt (first)continent_name continent_code two_letter_country_code three_letter_country_code , by(country)

foreach var of varlist time* ing* spices*{
	assert !missing(`var')
}

*Organize identification variables
rename three_letter_country_code adm0

** save dataset
save "${codedata}/recipes/recipe_sum.dta", replace