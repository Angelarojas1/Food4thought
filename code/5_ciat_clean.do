   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *        This dofile merges recipe, region, country dataset      	  *
   *																	  *
   * - Inputs: "${rawdata}/CIAT/food_supplies_countries_regions_all_merge.csv"
   *           "${recipes}/cuisine_complexity_sum.dta"		      *
   *		   "${rawdata}/CIAT/ingredients_category.xlsx"				  *
   *		   "${rawdata}/CIAT/region_ingredients.xlsx"				  *
   * - Output: "${versatility}/cuisine_ciat.dta"         	  			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 14, 2023

****************************************
* Data cleaning for CIAT data
****************************************

* get country-region data from CIAT map *

* import data
import delimited using "${rawdata}/CIAT/food_supplies_countries_regions_all_merge.csv", varnames(1) case(lower) stringcols(_all) encoding("utf-8") clear
describe, full

keep country region_nice
duplicates drop

* correct country names
 replace country = "Bosnia And Herzegovina" if country == "Bosnia and Herzegovina"
 replace country = "China" if country == "China, mainland"
 replace country = "Bolivia" if country == "Bolivia (Plurinational State of)"
 replace country = "Cote D'Ivoire" if country == "Cte d'Ivoire"
 replace country = "Iran" if country == "Iran (Islamic Republic of)"
 replace country = "North Korea" if country == "Democratic People's Republic of Korea"
 replace country = "South Korea" if country == "Republic of Korea"
 replace country = "Syria" if country == "Syrian Arab Republic"
 replace country = "Laos" if country == "Lao People's Democratic Republic"
 replace country = "Moldova" if country == "Republic of Moldova"
 replace country = "Russia" if country == "Russian Federation"
 replace country = "Sudan" if country == "Sudan (former)"
 replace country = "United States" if country == "United States of America"
 replace country = "Venezuela" if country == "Venezuela (Bolivarian Republic of)"
 replace country = "Vietnam" if country == "Viet Nam"

preserve
merge m:1 country using "${recipes}/cuisine_complexity_sum.dta"
tab _merge
assert inlist(_merge, 1, 2, 3)

tab country if _merge == 1
assert inlist(country, "Aruba", "Comoros", "Eritrea", "Liechtenstein", "Kosovo", "Singapore", "Tonga", "Tuvalu") if _merge == 2
restore

* add region to missing countries
tab region_nice

set obs `=_N+1'
replace country = "Aruba" if _n == _N
replace region_nice = "Trop. S. America" if _n == _N

set obs `=_N+1'
replace country = "Comoros" if _n == _N
replace region_nice = "IOI" if _n == _N

set obs `=_N+1'
replace country = "Eritrea" if _n == _N
replace region_nice = "East Africa" if _n == _N

set obs `=_N+1'
replace country = "Kosovo" if _n == _N
replace region_nice = "SE Europe" if _n == _N

set obs `=_N+1'
replace country = "Liechtenstein" if _n == _N
replace region_nice = "SW Europe" if _n == _N

set obs `=_N+1'
replace country = "Singapore" if _n == _N
replace region_nice = "Southeast Asia" if _n == _N

set obs `=_N+1'
replace country = "Tonga" if _n == _N
replace region_nice = "Australia New Zealand" if _n == _N

set obs `=_N+1'
replace country = "Tuvalu" if _n == _N
replace region_nice = "Australia New Zealand" if _n == _N

preserve
merge m:1 country using "${recipes}/cuisine_complexity_sum.dta"
tab _merge
assert _merge != 2
restore

* save data
tempfile country_region
save `country_region', replace

* get ingredient-category data from CIAT map **************************
import excel "${rawdata}/CIAT/ingredients_category.xlsx", sheet("Sheet1") firstrow case(lower) clear
isid ingredients
tempfile category
save `category', replace

* get ingredient-region data from CIAT map **************************
import excel "${rawdata}/CIAT/region_ingredients.xlsx", sheet("Sheet1") firstrow case(lower) clear

** check
 cap noisily assert _N == 339
 cap noisily assert !missing(region_nice)
 
 drop if missing(region_nice)
 cap noisily isid region_nice ingredients
 list region_nice ingredients if missing(ingredients)
 drop if missing(ingredients)
 
 isid region_nice ingredients

** merge with ingredient-category
 merge m:1 ingredients using `category'
 assert _merge == 3
 drop _merge
 
 keep if fruit == 0
 drop fruit

** merge with country_region
 joinby region_nice using `country_region'
 rename ingredients nativeIng
 
 sort country nativeIng
 cap noisily isid country nativeIng
 
 duplicates tag country nativeIng, gen(tag)
 tab tag
 assert inlist(tag, 0, 1, 2)
 list if tag > 0
 drop tag
 duplicates drop country nativeIng, force
 isid country nativeIng
 
 tempfile working
 save `working', replace
 
** generate controls: number of ingredients
 gen one = 1
 collapse (sum)numNative = one, by(country)
 
 isid country
 unique country
 note: There are `r(sum)' countries having numNative/native ingredients.
 
** merge back 
 merge 1:m country using `working'
 assert _merge == 3
 drop _merge
 
** merge with recipe and limit to countries that we have recipes
 merge m:1 country using "${recipes}/cuisine_complexity_sum.dta"
 tab _merge
 assert inlist(_merge, 1, 2, 3)
 
 list country if _merge == 2
 assert inlist(country, "Comoros", "Madagascar", "Mauritius") if _merge == 2
 
 keep if _merge == 3
 drop _merge
 
 unique country
 note: There are `r(sum)' countries with native ingredients from CIAT map and cuisine data. We don't have native ingredients for IOI region. Thus missing 3 countries here ("Comoros", "Madagascar", "Mauritius").
 
 rename nativeIng ingredient
 isid adm0 ingredient
 
 unique adm0
 assert `r(sum)' == 136
 
** save dataset
save "${versatility}/cuisine_ciat.dta", replace
 
note
 
 


