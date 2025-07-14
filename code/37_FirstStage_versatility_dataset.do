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
	
	/* ***************************************************** *
		* File Details
		import Versatility Median
		native Versatility Weighted Median
		*******************************************************/
		
	use "$recipes/complexity_recipe.dta", clear
	
	merge 1:1 country using "$flfp\FLFPlong2019.dta", gen(flfp_merge)
	
	keep if flfp_merge != 2
	encode continent_name, gen(continent)
	
	
	*===============================================================================*

	
	merge 1:1 adm0 using "$versatility/final_versatility.dta", gen(final_versatility_merge)
	
	save "$versatility/first_stage_dataset.dta", replace