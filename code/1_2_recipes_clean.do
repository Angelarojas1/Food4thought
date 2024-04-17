   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * This dofile checks recipe information to be sure it makes sense i.e. recipes with more number of ingredients takes longer to cook
   *																	  *
   * - Inputs: "${recipes}/recipe_all_countries.dta"		      		  *
   * - Output:   										          		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Ene 12, 2024

* import data
use "${recipes}/recipe_all_countries.dta", clear

* Fix number of ingredients variable
destring numberofingredients_raw, replace

replace numberofingredients = numberofingredients_raw if numberofingredients == 0
replace numberofingredients = numberofingredients_raw if numberofingredients == 1 & inlist(country, "Chile", "Libya", "Peru")

local len = length(",")
gen n_ing = (length(listofingredients) - length(subinstr(listofingredients, ",", "", .))) / `len' 

replace numberofingredients = n_ing + 1 if numberofingredients == 1 & inlist(country, "Jordan", "Latvia")
drop n_ing

* Organize time variable
replace totaltime = 4320 if cooktime == "~ 3-4 days"
replace totaltime = 1440 if cooktime == "~ 1 day"
replace totaltime = 255 if strpos(cooktime,"4 hrs 15")>0
replace totaltime = 210 if strpos(cooktime,"3 1/2 h")>0 | strpos(cooktime,"3 hrs 30")>0
replace totaltime = 180 if cooktime == "~ 3hrs"
replace totaltime = 150 if cooktime == "PT2H30M" | strpos(cooktime,"2 hrs 30")>0 | strpos(cooktime,"2 hours 30")>0
replace totaltime = 150 if strpos(cooktime,"2 hrs 15")>0
replace totaltime = 120 if cooktime == "~ 2 hours" | cooktime == "~ 2hrs" | cooktime == "2 hours"
replace totaltime = 105 if strpos(cooktime,"1 hr 45")>0
replace totaltime = 100 if strpos(cooktime,"1 hr 40")>0
replace totaltime = 90 if cooktime == "PT1H30M" | strpos(cooktime,"1 hr 30")>0
replace totaltime = 80 if cooktime == "PT1H20M" | cooktime == "~ 1 hour 20 minutes"
replace totaltime = 75 if strpos(cooktime,"1 hr 15")>0
replace totaltime = 70 if strpos(cooktime,"1 hr 10")>0
replace totaltime = 60 if cooktime == "~ 1 hour" | cooktime == "~ 1 hr" | cooktime == "1 hour"
replace totaltime = 155 if preptime == "PT20M" & cooktime == "PT135M"
replace totaltime = 65 if preptime == "PT45M" & cooktime == "PT20M"
replace totaltime = 50 if preptime == "PT50M" & cooktime == "" 
replace totaltime = 50 if preptime == "PT15M" & cooktime == "PT35M"
replace totaltime = 45 if preptime == "PT15M" & cooktime == "PT30M"
replace totaltime = 40 if preptime == "PT15M" & cooktime == "PT25M"
replace totaltime = 40 if preptime == "PT60M" & cooktime == ""
replace totaltime = 40 if preptime == "PT40M" & cooktime == "" 
replace totaltime = 30 if preptime == "PT15M" & cooktime == "PT15M"
replace totaltime = 30 if preptime == "PT30M" & cooktime == "" 
replace totaltime = 20 if preptime == "PT20M" & cooktime == "" 
replace totaltime = 10 if preptime == "PT10M" & cooktime == "" 

* Drop recipes with information as zero in time and number of ingredients
drop if totaltime==0 // 6,078 observations deleted
drop if numberofingredients==0 // 79 observations deleted

** drop recipes that the total time are higher than 99%
bys country: egen p99 = pctile(totaltime), p(99)
drop if totaltime > p99
note: `r(N_drop)' recipes are dropped because of higher than 99%.

sum totaltime

*replace listofingredients = ",'" if strpos(listofingredients,", '")>0
*replace listofingredients = subinstr(listofingredients, ", '", ",'", .)
*gen int number = ustrlen(ustrregexra(listofingredients, ",'", ""))

