   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              	  This dofile cleans MLFP database 				      *
   *																	  *
   * - Inputs: "${rawdata}/mlfp/MLFP.csv"							      *
   * - Output: "${flfp}/MLFPlong2019.dta"				          *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Septembre 26,2025

* import FLFP dataset
import delimited "${rawdata}/mlfp/MLFP.csv", encoding(UTF-8) varnames(1) case(lower) clear

** rename variables with label values
foreach v of varlist v5-v69{
	local x: variable label `v'
	rename `v' year`x'
}
describe, full

** countryname cannot uniquely identify the observations, drop duplicate rows
cap noisily isid countryname
bysort countryname: gen id = _n
tab id
assert inlist(id, 1, 2,3)
bys countryname: egen flag = max(id == 2| id==3)
list countryname if flag == 1, sepby(countryname)
*br if flag == 1

** Fix country name
drop if flag == 1 & countryname == "Middle East" // contains combinations of countries
replace countryname = "Democratic Republic of the Congo" if indicatorname == "COD"
replace countryname = "Republic of the Congo" if indicatorname == "COG"
replace countryname = "North Korea" if indicatorname == "PRK"

isid countryname

** Fix year 1960
replace year1960 = "" 
destring year1960 year1961, replace

** reshape dataset from wide format to long format
reshape long year, i(countryname indicatorname) j(y)

** rename variables
rename year MLFP
rename y year
rename countryname country
rename countrycode adm0

** drop variables
drop v70 v71 id flag indicatorcode

* Organize country variable
* correct country names
replace country = "Bosnia And Herzegovina" if country == "Bosnia and Herzegovina"
replace country = "Cote D'Ivoire" if country == "Cote d'Ivoire"
replace country = "Kyrgyzstan" if country == "Kyrgyz Republic"
replace country = "Laos" if country == "Lao PDR"
replace country = "Russia" if country == "Russian Federation"
replace country = "Slovakia" if country == "Slovak Republic"
replace country = "South Korea" if country == "Korea"
replace country = "Syria" if country == "Syrian Arab Republic"

*- Drop if they are not countries
drop if strpos(country, "Africa ") > 0
drop if strpos(country, "Europe") > 0
drop if strpos(country, "Caribbean s") > 0
drop if strpos(country, "East Asia") > 0
drop if strpos(country, "Early") > 0
drop if strpos(country, "Fragile") > 0
drop if strpos(country, "HIPC") > 0
drop if strpos(country, "IBRD") > 0
drop if strpos(country, "IDA") > 0
drop if strpos(country, "demographic") > 0
drop if strpos(country, "countries") > 0
drop if strpos(country, "income") > 0
drop if strpos(country, "Latin America") > 0
drop if strpos(country, "Not ") > 0
drop if strpos(country, "OECD") > 0
drop if strpos(country, "small states") > 0
drop if strpos(country, "Sub-") > 0
drop if strpos(country, "World") > 0

*-- Organize code
replace adm0 = indicatorname if length(adm0) > 3 
replace adm0 = indicatorname  if adm0 == " RB"

save "${mlfp}/MLFPlong.dta", replace

** keep the most recent year
keep if year == 2019
isid country
unique country
note: There are `r(sum)' countries in MLFP data.

** save dataset
save "${mlfp}/MLFPlong2019.dta", replace
note

