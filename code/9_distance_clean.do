****************************************
* Data cleaning for distance data
****************************************

* calculate distance between any two countries in the world **********************

 use "${codedata}/iv_versatility/recipe_flfp_ciat.dta", clear

 preserve
 keep adm0 country
 rename country country_r
 duplicates drop 
 isid adm0
 tempfile adm0
 save `adm0', replace
 restore
 
** import data
 use "${rawdata}/distance/geo_cepii.dta", clear

** keep capitals
 keep if cap == 1
 rename iso3 adm0
 isid adm0
 keep adm0 country lat lon
 
** keep countries that we have recipes data
 merge 1:1 adm0 using `adm0'
 tab _merge
 assert inlist(_merge, 1, 2, 3)
 drop if _merge == 1
 tab adm0 country_r if _merge == 2
 replace country = country_r if missing(country)
 drop country_r _merge
 
** fill in the lat and lon for missing countries
 replace lat = 47.17 if country == "Liechtenstein"
 replace lon = 9.51 if country == "Liechtenstein"

 replace lat = 44.44 if country == "Romania"
 replace lon = 26.10 if country == "Romania"
 
 replace lat = 44.79 if country == "Serbia"
 replace lon = 20.46 if country == "Serbia"

 assert !missing(lat) & !missing(lon)
 unique adm0
 assert `r(N)' == 135

** create every combinations of country
 gen country2 = country
 fillin country country2

** fill in missing values by group
foreach var of varlist adm0{
	bysort country(`var'): replace `var' = `var'[_N]
}

foreach var of varlist lat lon{
	bysort country(`var'): replace `var' = `var'[_n-1] if missing(`var')	
}

** drop pairs that contain same country
drop if country2 == country
drop _fillin

** generate lat and lon for country2
gen lat2 = .
gen lon2 = .
gen adm0_2 = ""

levelsof country, local(level)
foreach c of local level{
	sum lat if country == "`c'"
	local s = r(mean)
	replace lat2 =`s' if country2 == "`c'"
	
	sum lon if country == "`c'"
	local t = r(mean)
	replace lon2 =`t' if country2 == "`c'"	
	
	levelsof adm0 if country == "`c'", local(code)
	foreach a of local code{
		replace adm0_2 = "`a'" if country2 == "`c'"
	}
}

** calculate distance between countries
geodist lat lon lat2 lon2, generate(capital_distance) sphere

** keep variables
rename country2 nativecountry
rename adm0_2 nativeadm0
rename capital_distance distance

save "${codedata}/iv_versatility/distance_capital.dta", replace
