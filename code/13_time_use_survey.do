   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile merges country recipe databases			  *
   *																	  *
   * - Inputs: "${rawdata}/time use/Multinational Time Use Study/         *
   *			ALL_HAF_external.dta"									  *
   *			"${codedata}/recipes/cuisine_complexity_sum.dta"		  *
   * - Output: "${outputs}/Figures/survey_recipe.png"			          *
   * ******************************************************************** *

   ** IDS VAR:          country        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 24, 2023

*================================================
* Time Use Survey vs. Recipe data
*================================================

* import survey data
use "${rawdata}/time use/Multinational Time Use Study/ALL_HAF_external.dta",clear

* get the label of country
label list country

keep country isocountry main18 survey 

rename main18 survey_avgtime
rename survey year
drop if survey_avgtime == 0

sum survey_avgtime, de
list if survey_avgtime < 0 
drop if survey_avgtime < 0 

collapse (mean)survey_avgtime, by(country isocountry)
rename isocountry two_letter_country_code

* merge with recipe data
merge 1:1 two_letter_country_code using "${codedata}/recipes/cuisine_complexity_sum.dta", force
assert inlist(_merge, 1, 2, 3)
keep if _merge == 3
drop _merge

* scatter plot
twoway (scatter survey_avgtime time_mean, mlabel(country) c(. l) ms(Oh none) legend(off) ytitle("Avg Prep Time in survey"))(lfit survey_avgtime survey_avgtime)
graph export "${outputs}/Figures/survey_recipe.png", replace
