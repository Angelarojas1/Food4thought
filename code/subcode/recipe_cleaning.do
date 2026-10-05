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
	winsor4 totaltime_orig, method(winsor) outlier(tail) level(1) group(Country) newvar(totaltime)
	winsor4 numberofspices, method(winsor) outlier(tail) level(1) group(Country) newvar(w_numberofspices)
	bys Country: egen w_mean_totaltime = mean(totaltime)
	bys Country: egen w_mean_spices = mean(w_numberofspices)
	
	* Count number of recipes
	gen one = 1
	bys country : egen numrecipes = total(one)
	drop one
	
		*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA con las variables estandarizadas
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
	
		sum  pca_index 
		gen z_pca_index  = ( pca_index  - r(mean)) / r(sd)
	
	label var pca_index "PCA Index"
	
	label var z_pca_index "Cuisine complexity"
 
	label var w_mean_spices  "Average spices"

