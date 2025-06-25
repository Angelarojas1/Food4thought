* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Dataset creation
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
	global figures				"$projectfolder\outputs\Figures"
	
	* ***************************************************** *
	
	/* ***************************************************** *
		* File Details
		import Versatility Median
		native Versatility Weighted Median
		*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	*merge 1:1 country using "$versatility\imported\importbycountry_v2_p50.dta", gen(import_merge)
	*merge m:1 adm0 using "$versatility\native\nativebycountry_p50_g2weight.dta", gen(native_merge)
	
	*drop if importVersatility == . & nativeVersatility == . // 25 obs deleted
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	/****************** Old versions of versatility calculation********************
	merge 1:1 adm0 using "$outputs\composite_versatility_mindist.dta", gen(mindist_merge)
	lab var Versatility_mindist "Composite - Min Distance"
	merge 1:1 adm0 using "$outputs\composite_versatility.dta", gen(composite_merge)
	lab var Versatility "Composite - No Min Distance"
	merge 1:1 adm0 using "$outputs\composite_versatility_weighted.dta", gen(weighted_merge)
	lab var Versatility_weighted "Composite - Suitability Weighted"
	merge 1:1 adm0 using "$outputs\clean_versatility.dta",gen(clean_versatility_merge)
	===============================================================================*/

	
	merge 1:1 adm0 using "$versatility/final_versatility.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset.dta", replace