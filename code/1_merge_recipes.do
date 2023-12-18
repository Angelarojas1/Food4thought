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

* Read in alll csv file in the precode folder *******************
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
destring totaltime numberofingredients numberofspices, replace 

* generate country
split src, parse(".")
rename src1 country
assert !missing(country)

unique country

replace country = proper(country)

save "${recipes}/recipe_all_countries.dta", replace