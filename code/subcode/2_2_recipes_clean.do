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
   ** Last date modified: April 19, 2024

 * Remove duplicates
duplicates drop nameoftherecipe totaltime listofingredients listofinstructions numberofservings preptime cooktime numberofingredients_raw numberofingredients country, force // Drop 9249 observations
sort country
 bysort nameoftherecipe country: gen numrecipe = _n
 
/*
* Create table to know how many recipes we have and we lose
  tabstat totalrecipe, by(country) stats(count) 
  
* Check difference between recipes with time and no time registered.
	tabstat numrecipe if totaltime == ., by(country) stats(count) 
	tabstat numrecipe if totaltime == 0, by(country) stats(count) 

* Check difference between recipes with ingredients and no ingredients registered.
	tabstat numrecipe if numberofingredients == 0, by(country) stats(count) 

* Recipes with no time and no ingredients
	tabstat numrecipe if numberofingredients == 0 & totaltime == 0, by(country) stats(count) 
	*/
	
	* Drop countries with more than 65% of its recipes without ingredient or time information.
	bysort country: egen welose1 = count(nameoftherecipe) if totaltime == 0 | totaltime ==.
	bysort country: egen welose2 = count(nameoftherecipe) if numberofingredients == 0
	bysort country: egen totalrecipe = total(numrecipe)
	egen welose = rowtotal(welose1 welose2)
	gen percent = (welose/totalrecipe)*100
	
	levelsof country if percent >= 65 & percent != ., local(country)
	foreach c of local country {
		drop if country == "`c'"
	}
	
	drop welose* percent totalrecipe

* Fix number of ingredients variable
	destring numberofingredients_raw, replace
	replace numberofingredients = numberofingredients_raw if numberofingredients == 0 
	replace numberofingredients = numberofingredients_raw if numberofingredients == 1 & inlist(country, "Chile", "Libya", "Peru")
	
	* Count ingredients
	local len = length(",")
	gen n_ing = (length(listofingredients) - length(subinstr(listofingredients, ",", "", .))) / `len' 
	replace numberofingredients = n_ing + 1 if numberofingredients == 1 & inlist(country, "Jordan", "Latvia")
	drop n_ing
	drop if numberofingredients >= 47 & country == "Iraq" // The code is counting wrong the ingredients, I drop 13 observations
	
* Fix time variable 
	gen prep = preptime
	replace prep = "" if strpos(preptime,"P")>0 | strpos(preptime,"m")>0 | strpos(preptime,"M")>0 | strpos(preptime,"h")>0 | strpos(preptime,"R")>0
	destring prep , replace

	gen cook = cooktime
	replace cook = "" if strpos(cooktime,"P")>0 | strpos(cooktime,"m")>0 | strpos(cooktime,"M")>0 | strpos(cooktime,"h")>0 | strpos(cooktime,"R")>0 | strpos(cooktime,"H")>0 | strpos(cooktime,"~")>0
	destring cook , replace

	replace totaltime = prep + cook if totaltime == 0 | totaltime == .

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
	replace totaltime = 50 if preptime == "PT50M" & cooktime == "" 
	replace totaltime = 40 if preptime == "PT15M" & cooktime == "PT25M"
	replace totaltime = 40 if preptime == "PT60M" & cooktime == ""
	replace totaltime = 40 if preptime == "PT40M" & cooktime == "" 
	replace totaltime = 30 if preptime == "PT15M" & cooktime == "PT15M"
	replace totaltime = 30 if preptime == "PT30M" & cooktime == "" 
	replace totaltime = 20 if preptime == "PT20M" & cooktime == "" 
	replace totaltime = 10 if preptime == "PT10M" & cooktime == "" 

* Drop recipes with information as zero in time and number of ingredients
	drop if totaltime==0 | missing(totaltime) // 70 observations deleted
	drop if numberofingredients==0 // 39 observations deleted
	
* Check Mexico, Brazil and Bangladesh that are the ones with higher 

*- Mexico
	*keep if country == "Mexico" | country == "Brazil" | country == "Bangladesh"
	gen n = 1
	collapse (sum) n, by(country)
	sum totaltime if country == "Bangladesh", de
	
	gsort country -totaltime
	replace totaltime = 120 if nameoftherecipe == "Kol de pavo de monte" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Dulce de calabaza" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Lengua en pebre" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Pozole de trigo" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Pan de cazón mexicano" & country == "Mexico"
	replace totaltime = 70 if nameoftherecipe == "Poc chuc" & country == "Mexico"
	replace totaltime = 70 if nameoftherecipe == "Poc chuc" & country == "Mexico"
	replace totaltime = 140 if nameoftherecipe == "Caldo de gallina" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Ceviche de atún" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Cebadina" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Jabalí alcaparrado" & country == "Mexico"
	replace totaltime = 80 if nameoftherecipe == "Conejo relleno al horno" & country == "Mexico"
	replace totaltime = 80 if nameoftherecipe == "Conejo relleno al horno" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Chorizo de Campeche" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Burritos de chile con carne" & country == "Mexico"
	replace totaltime = 40 if nameoftherecipe == "Ceviche de sierra" & country == "Mexico"
	replace totaltime = 90 if nameoftherecipe == "Alberjones con nopalitos" & country == "Mexico"
	replace totaltime = 35 if nameoftherecipe == "Arroz con leche" & country == "Mexico"
	replace totaltime = 20 if nameoftherecipe == "Atole de cajeta" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Berenjenas capeadas" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Budín" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Caldillo en chile verde" & country == "Mexico"
	replace totaltime = 40 if nameoftherecipe == "Caldo de queso" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Caldo de langostinos" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Caldo tlalpeño" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Camarones al mojo de ajo" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Camarones en aguachile rojo" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Cazuela" & country == "Mexico"
	replace totaltime = 20 if nameoftherecipe == "Cazón frito" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Chilaquiles de rancho" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Chul de frijol verde" & country == "Mexico"
	*replace totaltime = 20 if nameoftherecipe == "" & country == "Mexico"
	
	
** drop recipes that the total time are higher than 99%
	bys country: egen p99 = pctile(totaltime), p(99)
	drop if totaltime > p99
	note: `r(N_drop)' recipes are dropped because of higher than 99%.

*replace listofingredients = ",'" if strpos(listofingredients,", '")>0
*replace listofingredients = subinstr(listofingredients, ", '", ",'", .)
*gen int number = ustrlen(ustrregexra(listofingredients, ",'", ""))

