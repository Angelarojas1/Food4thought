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
	
	** Clean recipes information
	do "$code/subcode/2_2_recipes_clean.do"
	
	* Min Max Mean by Country
	bys Country: egen min_totaltime = min(totaltime)
	bys Country: egen max_totaltime = max(totaltime)
	bys Country: egen mean_totaltime = mean(totaltime)
	bys Country: egen median_totaltime = median(totaltime)
	bys Country: egen mean_spices = mean(numberofspices)
	bys Country: egen median_spices = median(numberofspices)
	bys Country: egen median_ingredients = median(numberofingredients)
	bys Country: egen mean_ingredients = mean(numberofingredients)
	
	* winsorize
	winsor4 totaltime, method(winsor) outlier(tail) level(1) group(Country) newvar(TotalTime)
	winsor4 numberofspices, method(winsor) outlier(tail) level(1) group(Country) newvar(w_numberofspices)
	bys Country: egen w_mean_totaltime = mean(TotalTime)
	bys Country: egen w_mean_spices = mean(w_numberofspices)
	
	* Count number of recipes
	gen one = 1
	bys country : egen numrecipes = total(one)
	drop one
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_numberofspices totaltime numberofingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA with standarized variables
	pca z_w_numberofspices z_totaltime z_numberofingredients
	
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
	
	save "${recipes}/recipe_all_countries_web.dta", replace

	preserve
	keep w_mean_totaltime w_mean_spices Country country mean_ingredients median_spices median_ingredients median_totaltime numrecipes z_pca_recipe pca_recipe adm0
	duplicates drop 
	save "$recipes/complexity_recipe.dta", replace
	
	restore
