
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *             This  dofile cleans greographical control data           *
   *																	  *
   * - Inputs: "${recipes}/cuisine_complexity_sum.dta"  				  *
   *           "${precodedata}/suitability/spices_suitability.dta"        *
   *           "${precodedata}/suitability/crop_suitability.dta"          *
   *           "${precodedata}/suitability/country-vars-9nov23.csv"       *
   * - Output: "${versatility}/geographical.dta"              			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 12, 2023

****************************************
* Data cleaning for geographical control data
****************************************

use "${recipes}/cuisine_complexity_sum.dta", clear

 preserve
 keep adm0 country
 duplicates drop 
 isid adm0
 tempfile adm0
 save `adm0', replace
 restore
 
use "${precodedata}/suitability/spices_suitability.dta", clear
 keep adm0 al_mn pt_mn ph_mn cl_md
 isid adm0
 tempfile geo1
 save `geo1', replace

use "${precodedata}/suitability/crop_suitability.dta", clear
 keep adm0 al_mn pt_mn ph_mn cl_md
 isid adm0
 tempfile geo2
 save `geo2', replace

import delimited using "${precodedata}/suitability/country-vars-9nov23.csv", case(lower) clear
 drop v1
 rename country adm0
 destring ph_mn, force replace

 append using `geo1'
 append using `geo2'

 duplicates drop adm0, force
 isid adm0

 merge 1:1 adm0 using `adm0'
 tab _merge
 drop if country == "Kosovo"
 assert _merge != 2
 drop if _merge == 1
 drop _merge

 unique adm0
 assert `r(sum)' == 138

* Check if we have information for all countries
 sum al_mn pt_mn ph_mn cl_md 

* Label variables
label var al_mn "Average altitude (mts)"  // 138 countries
label var pt_mn "Total precipitation in 1999 (mm)" // 137 countries (Tonga)
label var ph_mn "Average pH" // 124 countries
label var cl_md "Most common climate zone (KG2)" // 138 countries

save "${versatility}/geographical.dta", replace
