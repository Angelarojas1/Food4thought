   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              	  This dofile cleans FLFP database 				      *
   *																	  *
   * - Inputs: "${rawdata}/flfp/FLFP.csv"							      *
   * - Output: "${codedata}/flfp/FLFPlong2019.dta"				          *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 14, 2023

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

* Organize country variable
* correct country names
replace country = "Bahamas" if country == "Bahamas, The"
replace country = "Bosnia And Herzegovina" if country == "Bosnia and Herzegovina"
replace country = "Cote D'Ivoire" if country == "Cote d'Ivoire"
replace country = "Egypt" if country == "Egypt, Arab Rep."
replace country = "Iran" if country == "Iran, Islamic Rep."
replace country = "Kyrgyzstan" if country == "Kyrgyz Republic"
replace country = "Laos" if country == "Lao PDR"
replace country = "North Korea" if country == "Korea, Dem. People's Rep."
replace country = "Russia" if country == "Russian Federation"
replace country = "Slovakia" if country == "Slovak Republic"
replace country = "South Korea" if country == "Korea, Rep."
replace country = "Syria" if country == "Syrian Arab Republic"
replace country = "Venezuela" if country == "Venezuela, RB"

** keep the most recent year
keep if year == 2019
isid country
unique country
note: There are `r(sum)' countries in FLFP data.

** save dataset
save "${codedata}/flfp/FLFPlong2019.dta", replace
note

