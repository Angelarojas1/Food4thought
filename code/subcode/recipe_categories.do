* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 24, 2025 						   	   *
*		Extract recipe categories for countries with high number of recipes
* **************************************************************************** *
	
	

	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	** Root folder globals 

	if "`c(username)'" == "stell" {
	global projectfolder "C:/Users/stell/Dropbox/food4thought/analysis23"
	global github "C:\Users\stell\Dropbox\food4thought\analysis23"
	}
	
	if "`c(username)'" == "wb641362" { // Varun
	global projectfolder "C:\Users\wb641362\Dropbox\food4thought\analysis23"
	global github "C:\Users\wb641362\OneDrive - WBG\Documents\GitHub\Food4thought"
	}
	
	if "c(username)" == "mgafargo" { // Margarita
	global projectfolder "C:\Users\mgafargo\Dropbox\food4thought"
	global github "C:\Users\mgafargo\Dropbox\food4thought"
	}

	** Project folder globals
	global files "$projectfolder\data\coded"
	
	* Dofile sub-folder globals
	global code					"$github/code"
	
	* Python codes folder
	global precode				"$github/precode" 
	global recipe_code          "$precode/recipes"	
	
	* Dataset sub-folder globals
	global precodedata			"$projectfolder/data/precoded"
	global rawdata				"$projectfolder/data/raw"
	global codedata				"$projectfolder/data/coded"
	
	global recipes              "$codedata/recipes"
	global flfp             	"$codedata/FLFP"
	global versatility          "$codedata/iv_versatility"
	global cookpad              "$codedata/cookpad"
	global fao_suit             "$codedata/FAO_suitability"

	
	* Output sub-folder globals
	global outputs				"$files/Outputs"
	global tables				"$projectfolder\outputs\Tables"
	
	* ***************************************************** *
	
	
	local country Australia China Japan Russia Bulgaria Croatia Iraq Philippines
	
	
	import delim using "$precodedata\recipes\final/Australia.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/Australia_category.csv", replace
	
	
	import delim using "$precodedata\recipes\final/China.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/China_category.csv", replace
	
	import delim using "$precodedata\recipes\final/Japan.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/Japan_category.csv", replace
	
	import delim using "$precodedata\recipes\final/Russia.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/Russia_category.csv", replace
	
	import delim using "$precodedata\recipes\final/Bulgaria.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/Bulgaria_category.csv", replace
	
	import delim using "$precodedata\recipes\final/Iraq.csv", clear varn(1)
	keep category
	drop if category == ""
	duplicates drop
	export delim using "$recipes/Iraq_category.csv", replace
	
	import delim using "$precodedata\recipes\final/Croatia.csv", clear varn(1)
	keep category
	cap drop if category == ""
	duplicates drop
	export delim using "$recipes/Croatia_category.csv", replace
	