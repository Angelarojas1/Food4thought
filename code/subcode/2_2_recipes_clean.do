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
   ** Last date modified: Jan 5, 2026
 

	* Drop recipes without a name
	drop if nameoftherecipe == "" // 53 recipes
	
	* Fix variable of number of ingredients 
	destring numberofingredients_raw, replace
	replace numberofingredients = numberofingredients_raw if numberofingredients == 0 
	replace numberofingredients = numberofingredients_raw if numberofingredients == 1 & inlist(country, "Chile", "Libya", "Peru")
	
	* Count ingredients for each recipe
	local len = length(",")
	gen n_ing = (length(listofingredients) - length(subinstr(listofingredients, ",", "", .))) / `len' 
	replace numberofingredients = n_ing + 1 if numberofingredients == 1 & inlist(country, "Jordan", "Latvia")
	drop n_ing
	drop if numberofingredients >= 47 & country == "Iraq" // The precode is counting wrong the ingredients, I drop 13 observations
	
	* Fix time variable  using prep time and cook time
	gen prep = preptime
	replace prep = "" if strpos(preptime,"P")>0 | strpos(preptime,"m")>0 | ///
	strpos(preptime,"M")>0 | strpos(preptime,"h")>0 | strpos(preptime,"R")>0
	destring prep , replace

	gen cook = cooktime
	replace cook = "" if strpos(cooktime,"P")>0 | strpos(cooktime,"m")>0 | ///
	strpos(cooktime,"M")>0 | strpos(cooktime,"h")>0 | strpos(cooktime,"R")>0 | ///
	strpos(cooktime,"H")>0 | strpos(cooktime,"~")>0
	destring cook , replace

	replace totaltime = prep + cook if totaltime == 0 | totaltime == .
	
	* Drop recipes with zeros in number of ingredients
	drop if numberofingredients==0 // 40 observations deleted
	
	* Drop countries with more than 65% of its recipes without ingredient or time information.
	sort country
	bysort nameoftherecipe country: gen numrecipe = _n
	
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
	
	* Drop recipes with zeros in time 
	drop if totaltime==0 | missing(totaltime) // 7001 observations deleted
	
	** drop recipes that the total time are higher than 99%
	bys country: egen p99 = pctile(totaltime), p(99)
	drop if totaltime > p99 // 553
	note: `r(N_drop)' recipes are dropped because of higher than 99%.
	
	** drop recipes that the total time are lower than 1%
	egen p1 = pctile(totaltime), p(1)
	drop if totaltime < p1 // 302
	note: `r(N_drop)' recipes are dropped because of lower than 1%.
	
	duplicates drop nameoftherecipe country, force 