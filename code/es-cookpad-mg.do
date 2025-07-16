* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Margarita Gafaro
* 				Last date modified: July 15, 2025 						   	   *
*				Modified by: Ángela Rojas
*			New (composite) versatility calculation using relative weights
* **************************************************************************** *

version 16

use "$cookpad/cookpad_adm0.dta", replace
merge m:1 adm0 using "$rawdata\suitability\spices\20250616-spices-suitability" /// AR: I don't know the origin of this data.
// BEN MLT and SGP not in spices data 
drop _merge 

merge m:1 adm0 using "$versatility/first_stage_dataset.dta"

*-- Rename variables
ren (median_ingredients median_spices median_totaltime) (ingredients spices time)
ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
		
*-- Create Meal Cook variable
egen mealCook=rowtotal(numLunCook numDinCook)
gen mealCook_year = mealCook*52
bys fem: sum mealCook

*-- Regressions
 est clear
 reghdfe lfpr mealCook if covid == 0, absorb(adm0 ym) cluster(adm0)
 reghdfe lfpr mealCook if covid == 0 & fem==1, absorb(adm0 ym) cluster(adm0)
 // continent has missings 
 reghdfe lfpr mealCook if covid == 0 & fem==1, absorb(continent_code ym) cluster(adm0)
 reghdfe lfpr mealCook  al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(continent_code ym) cluster(adm0)
 
*-- IV regressions
ivreghdfe lfpr (mealCook=spices_max_suitability)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first

eststo s1: ivreghdfe lfpr (mealCook=versatility)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first

ivreghdfe lfpr (mealCook=suit_versatility)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first
  
eststo s2: ivreghdfe hours (mealCook=suit_versatility)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first
  
ivreghdfe p2p (mealCook=suit_versatility)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first
 
ivreghdfe p2p (mealCook=suit_versatility)   al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first
  
ivreghdfe hours (mealCook=suit_versatility)   al_mn pt_mn p  i.cl_md if covid == 0  & fem==1 , absorb(reg2_global ym) cluster(adm0) first
   
/// gender gap within households 
ivreghdfe hours (mealCook=suit_versatility) hhsize  al_mn pt_mn p  i.cl_md if covid == 0 & fem==1, absorb(reg2_global ym) cluster(adm0) first
 
*-- Created output
  esttab s* using "$tables\ivreghdfe_specs.csv", replace