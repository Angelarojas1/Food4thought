   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *      This dofile creates files to generate versatility variables 	  *
   *																	  *
   * - Inputs: "${versatility}/cuisine_ciat_suit.dta"	  	 			  *
   *           "${versatility}/median_suitability.dta"        			  *
   *		   "${versatility}/cuisine_suit.dta"			  			  *
   * - Output: "${versatility}/native/native_clean_`var'.dta"			  *
   *		   "${versatility}/imported/imported_`var'.dta"	  			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Nov 28, 2023

****************************************
* Data cleaning for versatility data
****************************************

// Limit ingredients to only suitable ingredients: = 1 if >= p0/p10/p25/... of suitability for region that's native for the ingredient

***** prep for imported versatility *****

 use "${versatility}/cuisine_ciat_suit.dta", clear
 keep adm0 ingredient
 rename ingredient nativeIng
 duplicates drop
 tempfile native
 save `native', replace
 
 use  "${versatility}/cuisine_suit.dta", clear
 merge m:1 ingredient using "${versatility}/median_suitability.dta"
 assert _merge == 3 | _merge == 1
 keep if _merge == 3
 drop _merge
 
 *gen p0 = 0
 *foreach var of varlist p0 p10 p25 p33 p50 p60 p66 p70{
 
 *preserve
 *gen aboveCutoff = (suitability = p50) & (!missing(suitability))
 joinby adm0 using `native'
 
 *keep if aboveCutoff == 1
 gen ifnative = (nativeIng == ingredient)

 * Drop info for native ingredients and keep only data for the imported ones
 *drop if ifnative == 1
 drop nativeIng

** save to csv file
 outsheet using "${versatility}/imported/imported_v4.csv", replace
 save "${versatility}/imported/imported_v4.dta", replace
 
 *restore
 
*}
