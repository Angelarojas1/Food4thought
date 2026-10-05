   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile merges country's recipes databases		  *
   *																	  *
   * - Inputs: "${precodedata}/recipes/final/`country'.csv"			      *
   * - Output: "${recipes}/recipe_all_countries.dta"	          		  *
   * ******************************************************************** *

   ** IDS VAR:               // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Nov 24, 2023

	*****************************
	*** Merge Recipes
	*****************************
clear all

	* Read in all csv file in the precode folder *******************
	* initialize an empty data file
	tempfile recipe
	save `recipe', emptyok

	* read in all csv file 
	local files: dir "${precodedata}/recipes/final" files "*.csv"
	dis `files'

	local numfiles : word count `files'
	di "`numfiles'"
	note: There are `numfiles' countries with recipes.

	foreach file in `files'{
		di _newline "PROCESS: `file'"
	
		* import data
		import delimited using "${precodedata}/recipes/final/`file'", bindquote(strict) maxquotedrows(0) varnames(1) case(lower) stringcols(_all) encoding("utf-8") clear
	
		* generate raworder
		gen raword = _n
	
		* generate source
		gen src = "`file'"
	
		* save data
		append using `recipe'
		save `recipe', replace
	}

	use `recipe', clear

	describe, full
	drop v1 unnamed01

	* convert string to numeric
	destring totaltime* numberofingredients numberofspices, replace 

	* generate country
	split src, parse(".")
	rename src1 country
	assert !missing(country)

	unique country

	replace country = proper(country)
	
	* Clean nameoftherecipe variable
	gen strL nameoftherecipe1 = nameoftherecipe
	drop nameoftherecipe 
	rename nameoftherecipe1 nameoftherecipe

	* Decode common HTML entities
	replace nameoftherecipe = subinstr(nameoftherecipe, "&amp;", "&", .)
	replace nameoftherecipe = subinstr(nameoftherecipe, "&quot;", `"""', .)
	
	* Lowercase and normalize spacing
	replace nameoftherecipe = ustrlower(nameoftherecipe)
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "\s+", " ")
	replace nameoftherecipe = strtrim(nameoftherecipe)

	* Remove leading labels like [Recipe + Video], [Recipe], [Video]
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "^\s*\[\s*(recipe\s*\+\s*video|recipe|video)\s*\]\s*", "")

	* Remove standalone words recipe/video
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "\b(recipe|video)\b", " ")

	* Remove long parenthetical descriptions
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "\([^)]{15,}\)", " ")

	* Clean punctuation but keep dash temporarily
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "[,.;:!/]+", " ")
	replace nameoftherecipe = ustrregexra(nameoftherecipe, "\s+", " ")
	replace nameoftherecipe = strtrim(nameoftherecipe)

	* Remove remaining dash punctuation from all variants
	foreach v in nameoftherecipe {
		replace `v' = ustrregexra(`v', "[-–—]", " ")
		replace `v' = ustrregexra(`v', "\s+", " ")
		replace `v' = strtrim(`v')
	}
	
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

	save "${recipes}/recipe_all_countries.dta", replace