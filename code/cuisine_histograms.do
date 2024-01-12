   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *       	  *
   *																	  *
   * - Inputs: "${recipes}/recipe_all_countries.dta"		      		  *
   * - Output: "${recipes}/cuisine_complexity_all.dta"	          		  *
   *		   "${recipes}/cuisine_complexity_sum.dta"			  		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Jan 1, 2024

* Check time, ingredients and spices variables
* import data
use "${recipes}/recipe_all_countries.dta", clear

** drop recipes that the total time are higher than 99%
bys country: egen p99 = pctile(totaltime), p(99)
drop if totaltime > p99
note: `r(N_drop)' recipes are dropped because of higher than 99%.

* Organize country and continent codes
kountry country, from(other) stuck marker
rename _ISO3N_ iso3
kountry iso3, from(iso3n) to(iso3c)
kountry iso3, from(iso3n) to(iso2c)
kountry iso3, from(iso3n) geo(un) 

rename (_ISO3C_ _ISO2C_ GEO)(adm0 two_letter_country_code continent_name)

* Fill missing information
replace continent_name = "Africa" if country == "Cabo Verde"
replace continent_name = "Europe" if country == "Kosovo"
replace two_letter_country_code = "CV" if country == "Cabo Verde"
replace two_letter_country_code = "XK" if country == "Kosovo"
replace adm0 = "CPV" if country == "Cabo Verde"
replace adm0 = "XXK" if country == "Kosovo"

** organize cookpad data
preserve
use "${cookpad}/Cookpad_clean.dta", clear
collapse emp_work_hours, by(country)
tempfile cookpad
save `cookpad', replace
restore

** merge with cookpad
merge m:1 country using `cookpad'
drop if _merge==2

sort country
egen id = group(country) if _merge==3

* Create histograms

foreach var of varlist totaltime numberofingredients numberofspices {

	hist `var' if _merge == 1, by(country, note("Not in cookpad", size(vsmall))) xtitle(,size(small)) ytitle(,size(small))
	
	graph export "${outputs}/Figures/`var'_ncp.png", replace
	
	hist `var' if _merge == 3 & id<31, by(country, note("", size(vsmall))) xtitle(,size(small)) ytitle(,size(small))
	
	graph export "${outputs}/Figures/`var'_1.png", replace
	
	hist `var' if _merge == 3 & id>30 & id<61, by(country, note("", size(vsmall))) xtitle(,size(small)) ytitle(,size(small))
	
	graph export "${outputs}/Figures/`var'_2.png", replace
	
	hist `var' if _merge == 3 & id>60 & id<91, by(country, note("", size(vsmall))) xtitle(,size(small)) ytitle(,size(small))
	
	graph export "${outputs}/Figures/`var'_3.png", replace
	
	hist `var' if _merge == 3 & id>90 & id<120, by(country, note("", size(vsmall))) xtitle(,size(small)) ytitle(,size(small))
	
	graph export "${outputs}/Figures/`var'_4.png", replace
}


** Fixing time graphs
summarize totaltime, detail
