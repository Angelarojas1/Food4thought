* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: 5 May, 2025 						   	   *
*				First stage results
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
	global github "C:\Users\wb641362\Dropbox\food4thought\analysis23"
	global files "C:\Users\wb641362\OneDrive - WBG\Documents\Food4Thought"
	
	* Creating the World Map Shape File
	* cd "C:\Users\wb641362\OneDrive - WBG\Documents\WB_countries_Admin0_10m"
	* spshape2dta WB_countries_Admin0_10m, replace saving(world)
	}

	** Project folder globals
	
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
	
	/* ***************************************************** *
		* File Details
		import Versatility Median
		native Versatility Weighted Median
		*******************************************************/
		
	use "$files/Outputs/complexity_recipe.dta", clear
	merge 1:1 country using "$versatility\imported\importbycountry_v2_p50.dta", gen(import_merge)
	
	
	merge m:1 adm0 using "$versatility\native\nativebycountry_p50_g2weight.dta", gen(native_merge)
	
	drop if importVersatility == . & nativeVersatility == . // 25 obs deleted
	
	merge 1:1 adm0 using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	keep if flfp_merge == 3
	encode continent_name, gen(continent)
	
	merge 1:1 adm0 using "$outputs\composite_versatility_mindist.dta", gen(mindist_merge)
	lab var Versatility_mindist "Composite - Min Distance"
	merge 1:1 adm0 using "$outputs\composite_versatility.dta", gen(composite_merge)
	lab var Versatility "Composite - No Min Distance"
	merge 1:1 adm0 using "$outputs\composite_versatility_weighted.dta", gen(weighted_merge)
	lab var Versatility_weighted "Composite - Suitability Weighted"
	merge 1:1 adm0 using "$outputs\clean_versatility.dta",gen(clean_versatility_merge)
	
	*twoway scatter w_mean_totaltime FLFP, mlabel(country) mlabs(tiny) mlw(none) legend(label(1 "FLFP"))
	*graph export "$files/Outputs/flfp_country.png", replace
	
	**********************************************************
	*			First Stage
	**********************************************************
	
	local outcome median_spices median_totaltime median_ingredients w_mean_totaltime
	
	est clear
	foreach o of local outcome {
		*********************************************
		* Newest Cleanest Versatility
		*********************************************
	eststo c1_`o': reg `o' versatility
	eststo c2_`o': reghdfe `o' versatility i.continent
	testparm `o' versatility
	ivregress 2sls FLFP ( `o' = versatility)
	
	}
	
	
	esttab c1* c2* using "$outputs/FirstStage_clean_versatility.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label
	
	
	
	
	if $run == 0{
		est clear
	foreach o of local outcome {
		*********************************************
		* Native Versatility
		*********************************************
	eststo s1_`o': reg `o' nativeVersatility
	eststo s2_`o': reghdfe `o' nativeVersatility i.continent
	testparm `o' nativeVersatility
	ivregress 2sls FLFP ( `o' = nativeVersatility)
	
	}
	
	
	esttab s1* s2* using "$outputs/FirstStage_nativeVersatility.csv", replace
	
	
	
	est clear
	foreach o of local outcome {
		*********************************************
		* Import Versatility
		*********************************************
	
	eststo s1_`o': reg `o' importVersatility
	eststo s2_`o': reghdfe `o' importVersatility i.continent
	testparm `o' importVersatility
	ivregress 2sls FLFP ( `o' = importVersatility)
	
	}
	
	
	esttab s1* s2* using "$outputs/FirstStage_importVersatility.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite Min Distance
		*********************************************
	eststo s1_`o': reg `o' Versatility_mindist
	eststo s2_`o': reghdfe `o' Versatility_mindist i.continent
	testparm `o' Versatility_mindist
	ivregress 2sls FLFP ( `o' = Versatility_mindist)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$outputs/FirstStage_versatility_mindist.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite
		*********************************************
	eststo s1_`o': reg `o' Versatility
	eststo s2_`o': reghdfe `o' Versatility i.continent
	testparm `o' Versatility
	ivregress 2sls FLFP ( `o' = Versatility)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$outputs/FirstStage_versatility.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite Weighted
		*********************************************
	eststo s1_`o': reg `o' Versatility_weighted
	eststo s2_`o': reghdfe `o' Versatility_weighted i.continent
	testparm `o' Versatility_weighted
	ivregress 2sls FLFP ( `o' = Versatility_weighted)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$outputs/FirstStage_versatility_weighted.csv", replace
	
	}
	