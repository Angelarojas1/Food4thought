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
	
	* ***************************************************** 
	
	*======================================================
	*				Cookpad Analysis
	*------------------------------------------------------
	
	
	use "$outputs/cookpad_adm0.dta", replace
	
	*** regressions
	/*
	i.	FLFP = average cooking time + average cooking time*number of meals
	ii.	FLFP = average cooking time*number of meals
	iii.FLFP = log (average cooking time) + log (average cooking time*number of meals)
	iv.	FLFP = log (average cooking time* number of meals)

	*/
	
	local outcomes FLFP emp_lfpr emp_work_hours
	est clear
	foreach o of local outcomes {
	eststo r1_`o': reg `o' time_median  income_2 pctTotalCook i.continentFactor
	}
	esttab r1_* using "$tables/cookpad_reg.csv", replace
	
	
	
	/*
	Cookpad regression at the individual/ household level
	Male/Female*lfp
	Likelihood that a person works depending on the food complexity of the country
	Recipes data
	Interact with dummy for M/F
	First Stage
	Repeat the analysis
	*/
	 
	ren (median_ingredients median_spices median_totaltime) (ingredients spices time)
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_time = log(time)
	gen femx = fem * time
	gen fem_logx = fem*log_time
	
	est clear
	foreach o of varlist p2p lfpr hours {
		eststo f1_`o': reghdfe `o' fem fem_logx if covid == 0, absorb(adm0 ym) cluster(adm0)
	}
	esttab f1_* using "$tables/cookpad_regressions.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label