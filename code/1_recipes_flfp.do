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

* Read in FLFP data *************************************************
preserve

* import FLFP dataset
import delimited "${rawdata}/flfp/FLFP.csv", encoding(UTF-8) varnames(1) case(lower) clear

** rename variables with label values
foreach v of varlist v2-v32{
	local x: variable label `v'
	rename `v' year`x'
}
describe, full

** countryname cannot uniquely identify the observations, drop duplicate rows
cap noisily isid countryname
bysort countryname: gen id = _n
tab id
assert inlist(id, 1, 2)
bys countryname: egen flag = max(id == 2)
list countryname continent_name if flag == 1, sepby(countryname)
drop if flag == 1 & continent_name == "Europe"
isid countryname

** reshape dataset from wide format to long format
reshape long year, i(countryname continent_name continent_code two_letter_country_code three_letter_country_code) j(y)

** rename variables
rename year FLFP
rename y year
rename countryname country

** drop variables
drop id flag

** keep the most recent year
keep if year == 2019
isid country
unique country
note: There are `r(sum)' countries in FLFP data.

** save dataset
save "${codedata}/flfp/FLFPlong2019.dta", replace
note

restore

* Merge recipe data with FLFP data *************************************************
merge m:1 country using "${codedata}/flfp/FLFPlong2019.dta"
tab _merge
assert inlist(_merge, 1, 2, 3)

tab country if _merge == 1
assert country == "Kosovo" if _merge == 1

tab country if _merge == 2
assert country != "Kosovo" if _merge == 2

keep if _merge == 3
drop _merge

* Collapse to country level *******************************************************

** drop recipes that the total time are higher than 99%
bys country: egen p99 = pctile(totaltime), p(99)
drop if totaltime > p99
note: `r(N_drop)' recipes are dropped because of higher than 99%.

** collapse to country level
gen cnt = 1
collapse (sum)num_recipes = cnt (mean)mTime = totaltime (mean)mIng = numberofingredients (mean)mSpice = numberofspices (first)continent_name continent_code two_letter_country_code three_letter_country_code year FLFP, by(country)

tab country if missing(FLFP)
assert inlist(country, "Aruba", "Dominica", "Liechtenstein", "Tuvalu") if missing(FLFP)
note: No FLFP data is available for Aruba, Dominica, Liechtenstein, Kosovo, Tuvalu.

unique country if !missing(FLFP)
note: There are `r(sum)' countries both have recipes and FLFP data.

foreach var of varlist mTime mIng mSpice{
	assert !missing(`var')
}

** save dataset
save "${codedata}/recipes/recipe_FLFP2019.dta", replace
