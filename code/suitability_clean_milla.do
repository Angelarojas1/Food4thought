   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *        This dofile merges recipe, region, country dataset      	  *
   *
   * Input: https://github.com/rubenmilla/Crop_Origins_Phylo?tab=readme-ov-file
   * ******************************************************************** *

	************************************
	**** Milla + CIAT + Suitability ****
	************************************
	
	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
	keep adm0 country
	duplicates drop
	tempfile adm0
	save `adm0'
	
	use "${versatility}/suitability.dta", clear
	
	replace country = "United States" if country == "United States of America"
	replace country = "Bolivia" if country == "Bolivia (Plurinational State of)"
	replace country = "Bosnia And Herzegovina" if country == "Bosnia and Herzegovina"
	replace country = "Cote D'Ivoire" if country == "Côte d'Ivoire"
	replace country = "United Kingdom" if country == "United Kingdom and N. Ireland"
	replace country = "Guam" if country == "Guam (USA)"
	replace country = "Iran" if country == "Iran  (Islamic Republic of)"
	replace country = "Moldova" if country == "Moldova, Republic of"
	replace country = "Palestine" if country == "Palestine, State of"
	replace country = "Russia" if country == "Russian Federation"
	replace country = "Syria" if country == "Syrian Arab Republic"
	
	merge m:1 adm0 country using `adm0'
	bys adm0 (country): replace country = country[_N] 
	drop if _merge == 2
	
	keep adm0 ingredient suitability country
	
	tempfile suit
	save `suit', replace
	
	preserve
	keep if country == "Rest of World"
	isid ingredient
	rename suitability suitability_rest
	tempfile rest
	save `rest', replace
	restore
	
	merge 1:1 adm0 ingredient using "${versatility}/Milla_CIAT_ing_origin.dta"
	
	drop if _merge == 1
	rename _merge _merge1
	
	* if missing suitability, use the suitability from the rest of the world
	merge m:1 ingredient using `rest'
	drop if _merge == 2 
	tab _merge1 _merge
	assert !missing(suitability_rest) if _merge1 == 2 & _merge == 3
	assert missing(suitability_rest) if _merge1 == 2 & _merge == 1 //For these ing we definetly don't have information
	replace suitability = suitability_rest if _merge1 == 2 & _merge == 3 
	drop _merge1 _merge suitability_rest
	
	sort adm0 ingredient
	isid adm0 ingredient
	
	** drop ingredients that we don't have suitability data at all
	gen flag = 0
	bys ingredient(suitability adm0): replace flag = 1 if suitability[1] == suitability[_N] & suitability[1] == .
	assert missing(suitability) if flag == 1
	
	tab ingredient if flag == 1 //identify ingredients without suitability information
	label var flag "ingredient without suitability information"
	
	unique adm0
	unique country
			
	assert `r(sum)' == 184 
	// we have 159 countries with suitability information
	
	save "${versatility}/milla_ciat_ing_suit.dta", replace 
	
*** Find median of suitability for native ingredients  ***

	drop flag
	
	drop if suitability == . | suitability == 0

	collapse (p10) p10 = suitability (p25) p25 = suitability (p33) p33 = suitability (median) p50 = suitability (p60) p60 = suitability (p66) p66 = suitability (p70) p70 = suitability, by(ingredient)
 isid ingredient // there's information for 64 ingredients
	save "${versatility}/median_suitability_m_c.dta", replace
		
	*** limit to suitability data of all ingredients that are from Milla data  ***
	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
	
	* Keep country names information
	preserve
	keep adm0 country region continent
	duplicates drop 
	isid adm0
	tempfile adm0
	save `adm0', replace
	restore
	
	* Keep only ingredients in recipe data
	preserve
	keep ingredient
	duplicates drop
	isid ingredient
	tempfile ing
	save `ing', replace
	restore
 
	use `rest', clear
	merge 1:1 ingredient using `ing'
	keep if _merge == 3 // 34 ingredients
	drop _merge
	rename suitability_rest suitability
	tempfile rest_suit
	save `rest_suit', replace
 
	use `suit', clear
	merge m:1 adm0 using `adm0'
	assert inlist(_merge, 1, 2, 3)
	drop if _merge == 1
	rename _merge _merge1
 
	merge m:1 ingredient using `ing'
	assert inlist(_merge, 1, 2, 3)
	drop if _merge1 == 3 & _merge == 1
	list if _merge == 2
	drop if _merge == 2
	tab adm0 if _merge1 == 2 & _merge == 1
		
	assert inlist(adm0, "GIB", "IMY", "SGP", "ABW", "MDV", "MLT", "XXK") if _merge1 == 2 & _merge == 1
	tab country if _merge1 == 2 & _merge == 1
	assert inlist(country, "Gibraltar", "Isle of Man", "Singapore", "Aruba", "Maldives", "Malta", "Kosovo") if _merge1 == 2 & _merge == 1
	
	 drop if _merge1 == 2 & _merge == 1
	assert _merge1 == 3 & _merge == 3
	drop _merge1 _merge

	append using `rest_suit'
	replace country = "Gibraltar" if missing(adm0)
	replace adm0 = "GIB" if missing(adm0)
 
	append using `rest_suit'
	replace country = "Isle of Man" if missing(adm0)
	replace adm0 = "IMY" if missing(adm0)
 
	append using `rest_suit'
	replace country = "Singapore" if missing(adm0)
	replace adm0 = "SGP" if missing(adm0)
	
	append using `rest_suit'
	replace country = "Aruba" if missing(adm0)
	replace adm0 = "ABW" if missing(adm0)
 
	append using `rest_suit'
	replace country = "Kosovo" if missing(adm0)
	replace adm0 = "XXK" if missing(adm0)
 
	append using `rest_suit'
	replace country = "Maldives" if missing(adm0)
	replace adm0 = "MDV" if missing(adm0)
 
	append using `rest_suit'
	replace country = "Malta" if missing(adm0)
	replace adm0 = "MLT" if missing(adm0)
		
	sort adm0 ingredient
	isid adm0 ingredient
 
	save "${versatility}/cuisine_suit_m_c.dta", replace
	