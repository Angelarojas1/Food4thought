* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 24, 2025 						   	   *
*				Cooktime calculations for India
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
	global figures				"$projectfolder/outputs/Figures"
	
	* ***************************************************** *

	import delim using "$precodedata\recipes\final\India.csv", clear

	encode recipecategory, gen(r_category)
	gen category = .
	* Breakfast - Indian Breakfast North Indian Breakfast South Indian Breakfast World Breakfast

	* Lunch - Lunch Brunch 

	* Appetizer - Side Dish Appetizer 

	* Dessert - Dessert

	ren totaltime total_time

	gen new_category = .
	replace new_category = 1 if recipecategory == "Indian Breakfast" | recipecategory == "North Indian Breakfast" | recipecategory == "South Indian Breakfast" | recipecategory == "World Breakfast" | recipecategory == "Brunch"
	replace new_category = 2 if r_category == 6 // Lunch
	replace new_category = 3 if r_category == 4 // Dinner
	replace new_category = 4 if recipecategory == "Appetizer" | recipecategory == "Main Course" | recipecategory == "Dessert" | recipecategory == "Side Dish" | recipecategory == "One Pot Dish" | recipecategory == ""
	replace new_category = 5 if recipecategory == "Snack"


	gen meal = (new_category != 5)

	bys meal: egen mean_time = mean(total_time)

	bys meal: egen median_time = median(total_time)

	egen time = mean(total_time)
	
	gen m_time = 3*total_time if meal == 1
	replace m_time = 2*total_time if mean != 1
	
	bys meal: egen mean_a_time = mean(m_time)

	bys meal: egen median_a_time = median(m_time)
	
	
	*========================================================
	*					New calculation
	*--------------------------------------------------------
	
	* Main Course
	gen main_course = 0
	replace main_course = 1 if new_category < 4 | recipecategory == "Main Course" | recipecategory == "One Pot Dish"
	
	bys main_course: egen time_mains_mean = mean(total_time)
	bys main_course: egen time_mains_median = median(total_time)
	
	* Subcategories
	gen subcategories = 0
	replace subcategories = 1 if new_category < 4 | recipecategory == "Main Course" | recipecategory == "One Pot Dish"
	replace subcategories = 2 if recipecategory == "Appetizer"
	replace subcategories = 3 if recipecategory == "Dessert"
	replace subcategories = 4 if recipecategory == "Side Dish"
	replace subcategories = 5 if recipecategory == "Snack"
	
	bys subcategories: egen time_subcategories_mean = mean(total_time)
	bys subcategories: egen time_subcategories_median = median(total_time)
	
	
	*========================================================
	*					Regressions
	*--------------------------------------------------------
	
	preserve
	use "$versatility/first_stage_dataset.dta", replace
	keep if country == "India"
	tempfile first_stage
	save `first_stage'
	restore
