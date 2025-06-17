* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Cookpad Data Exploration
* **************************************************************************** *
	
	use "$cookpad\Cookpad_clean.dta", replace
	
	drop if year == 2020
	
	* keep useful variables
	* keep country three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender
	gen covid=(ym>=722)
	
	* merge with cuisine data
	rename three_letter_country_code adm0
	merge m:1 country using "$codedata/Outputs/complexity_recipe.dta" 
	keep if _merge == 3
	drop _merge
	
	merge m:1 adm0 using "$flfp/FLFPlong2019.dta", gen(flfp_merge)
	keep if flfp_merge == 3
	drop flfp_merge

	save "$codedata/Outputs/cookpad_adm0.dta", replace
	
	
	*=========================================================
	* Adding cookpad indicator to versatility
	*=========================================================
	
	keep adm0
	duplicates drop
	
	merge 1:1 adm0 using "$codedata/Outputs/all_versatility.dta", gen(cookpad_merge)
	
	drop if cookpad_merge == 1
	gen cookpad = (cookpad_merge == 3)
	
	save "$codedata/Outputs/final_versatility.dta", replace