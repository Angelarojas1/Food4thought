* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Dataset creation
* **************************************************************************** *

	
	/* ***************************************************** *
		* File Details
		import Versatility Median
		native Versatility Weighted Median
		*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	merge 1:1 adm0 using "$versatility/final_versatility.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset.dta", replace
	
	/* ***************************************************** *
	* File Details: Milla + CIAT only native versatility
	*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	drop continent_code flfp_merge two_letter_country_code country_name ///
	country_number flfp_merge
	encode continent_name, gen(continent_code)
	
	merge 1:1 adm0 using "$versatility/final_native_versatility.dta", gen(final_versatility_merge)	
	keep if final_versatility_merge == 3
	
	merge 1:1 adm0 using "${versatility}/geographical.dta"
	keep if _merge == 3
	
	drop final_versatility_merge _merge
	
	save "$versatility/first_stage_dataset_native_m_c.dta", replace
	
	/* ***************************************************** *
	* File Details: Milla + CIAT
	*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	merge 1:1 adm0 using "$versatility/final_versatility_m_c.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset_m_c.dta", replace