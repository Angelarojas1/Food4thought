   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *       This dofile organizes time, ingredients and spices variables	  *
   *																	  *
   * - Inputs: "${recipes}/recipe_all_countries.dta"		      		  *
   * - Output: "${recipes}/cuisine_complexity_all.dta"	          		  *
   *		   "${recipes}/cuisine_complexity_sum.dta"			  		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 13, 2023

	* Check time, ingredients and spices variables
	* import data
	use "${recipes}/recipe_all_countries.dta", clear
	
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

	encode country, gen(Country)

	** Clean recipes information
	do "$code/subcode/2_2_recipes_clean.do"
	
	duplicates drop nameoftherecipe country, force
	
	* Winsorize time variable and create dataset

	* Min Max Mean by Country
	bys Country: egen min_totaltime = min(totaltime_orig)
	bys Country: egen max_totaltime = max(totaltime_orig)
	bys Country: egen mean_totaltime = mean(totaltime_orig)
	bys Country: egen median_totaltime = median(totaltime_orig)
	bys Country: egen mean_spices = mean(numberofspices)
	bys Country: egen median_spices = median(numberofspices)
	bys Country: egen median_ingredients = median(numberofingredients)
	bys Country: egen mean_ingredients = mean(numberofingredients)
	
	* winsorize
	winsor4 totaltime_orig, method(winsor) outlier(tail) level(1) group(Country) newvar(TotalTime)
	winsor4 numberofspices, method(winsor) outlier(tail) level(1) group(Country) newvar(w_numberofspices)
	bys Country: egen w_mean_totaltime = mean(TotalTime)
	bys Country: egen w_mean_spices = mean(w_numberofspices)
	
	* Organize time variable
	sum median_totaltime, de
	bys country: gen outlier = cond(median_totaltime>=80,1,0)

	sum totaltime_orig if outlier == 1, de
	tab median_totaltime if outlier == 1
	tab country if outlier == 1
	br nameoftherecipe country if outlier == 1 & totaltime_orig >= 480
	
	* Count number of recipes
	gen one = 1
	bys country : egen numrecipes = total(one)
	drop one
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_numberofspices totaltime_orig numberofingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA with standarized variables
	pca z_w_numberofspices z_totaltime_orig z_numberofingredients
	
	predict pca if e(sample), score
	
	sum  pca
	gen z_pca  = ( pca  - r(mean)) / r(sd)

	bys Country: egen z_pca_recipe = mean(z_pca)
	bys Country: egen pca_recipe = mean(pca)
	
	levelsof Country, local(countries)
	
	foreach c of local countries {
	sum z_pca if Country == `c'
	}
	
	*hist z_pca, normal
	sum z_pca, detail
	
	preserve
	keep w_mean_totaltime w_mean_spices Country country mean_ingredients median_spices median_ingredients median_totaltime numrecipes z_pca_recipe pca_recipe
	duplicates drop 
	save "$recipes/complexity_recipe.dta", replace
	restore


	** collapse to country level, multiple percentiles
	gen cnt = 1
	collapse (p10)time_p10 = totaltime_orig (p25)time_p25 = totaltime_orig (median)time_median = totaltime_orig (p75)time_p75 = totaltime_orig  (p90)time_p90 = totaltime_orig  (mean)time_mean = totaltime_orig  ///
(p10)ingredients_p10 = numberofingredients (p25)ingredients_p25 = numberofingredients (median)ingredients_median = numberofingredients (p75)ingredients_p75 = numberofingredients  (p90)ingredients_p90 = numberofingredients (mean)ingredients_mean = numberofingredients ///
(p10)spices_p10 = numberofspices (p25)spices_p25 = numberofspices (median)spices_median = numberofspices (p75)spices_p75 = numberofspices  (p90)spices_p90 = numberofspices (mean)spices_mean = numberofspices ///
(sum)num_recipes = cnt (first)continent_name two_letter_country_code adm0 , by(country)

	foreach var of varlist time* ing* spices*{
		assert !missing(`var')
	}

	** save dataset
	save "${recipes}/cuisine_complexity_all.dta", replace

	* Keep only mean and median measures
	keep time_mean time_median ingredients_mean ingredients_median spices_mean spices_median num_recipes continent_name two_letter_country_code adm0 country

	save "${recipes}/cuisine_complexity_sum.dta", replace