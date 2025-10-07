   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              	  This dofile cleans MLFP database 				      *
   *																	  *
   * - Inputs: "${rawdata}/mlfp/MLFP.csv"							      *
   *           "${rawdata}/flfp/FLFP.csv"							      *
   * - Output: "${flfp}/LFPlong2019.dta"				          *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Septembre 26,2025
   
   *-- Import FLFP data 
   use "${flfp}/FLFPlong2019.dta",clear
   
   *-- Merge with MLFP data
   merge 1:1 adm0 using "${mlfp}/MLFPlong2019.dta"
   
   *-- Keep countries in both datasets
   keep if _merge == 3
   
   *-- Keep variables of interest 
   drop country_name country_number indicatorname _merge
   
   rename FLFP LFP_F
   rename MLFP LFP_M
   reshape long LFP_, i(country adm0 year) j(sex, string)
   rename LFP_ LFP
   
   *-- Encode indicator variable
   gen fem_lfp = (sex == "F")
   label define femlbl 0 "Male" 1 "Female"
   label values fem_lfp femlbl
   drop sex

   save "${codedata}/merge/lfplong2019.dta", replace