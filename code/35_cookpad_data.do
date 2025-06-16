* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Cookpad Data Exploration
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
	
	use "$cookpad\Cookpad_clean.dta", replace
	
	drop if year == 2020
	
	* keep useful variables
	* keep country three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender
	gen covid=(ym>=722)
	
	* merge with cuisine data
	rename three_letter_country_code adm0
	merge m:1 country using "$outputs/complexity_recipe.dta" 
	keep if _merge == 3
	drop _merge

	save "$outputs/cookpad_adm0.dta", replace
	
	
	*=========================================================
	* Adding cookpad indicator to versatility
	*=========================================================
	
	keep adm0
	duplicates drop
	
	merge 1:1 adm0 using "$outputs/all_versatility.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$outputs/final_versatility.dta", replace