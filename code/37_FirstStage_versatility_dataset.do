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
		
	use "$codedata/Outputs/complexity_recipe.dta", clear
	
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

	
	merge 1:1 adm0 using "$codedata/Outputs/final_versatility.dta",gen(final_versatility_merge)
	
	save "$codedata/Outputs/first_stage_dataset.dta", replace