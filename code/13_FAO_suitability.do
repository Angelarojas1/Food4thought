   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *         			This dofile cleans FAO information    		  	  *
   *																	  *
   * - Inputs: "${rawdata}/suitability/FAO/crop_suitability_country/     ///
   *			`k'_ctr_Low_CRUTS32/`k'_CRUTS32_Hist_8110Lr_ctr.csv"      *
   *		   "${fao_suit}/crop_name.dta"				  *
   * - Output: "${fao_suit}/suitability_FAO.dta"	          *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 24, 2023

****************DATA CLEANING FOR CROP NAME***********************

* import data
import excel "${rawdata}/suitability/FAO/crop_name.xlsx", sheet("Sheet1") firstrow clear

* save as dta file
save "${fao_suit}/crop_name.dta", replace


****************SUITABILITY FOR STAPLES FROM FAO***********************

* import data
foreach k in alf ban bck brl bsg cab car chk cit coc cof con cot cow csv flx fml grd ///
grm jtr mis mze mzs oat olp olv oni pea phb pig pml rcd rcg rcw rsd rub rye sfl  ///
soy spo srg sub suc swg tea tob tom whe wpo yam{
	import delimited "${rawdata}/suitability/FAO/crop_suitability_country/`k'_ctr_Low_CRUTS32/`k'_CRUTS32_Hist_8110Lr_ctr.csv", clear
	
	* keep only total lands
	keep if lc == 11 & exc == 5 & aez == 35
	tempfile b`k'
	save `b`k''
} 

* append all data 
use `balf', clear

foreach k in ban bck brl bsg cab car chk cit coc cof con cot cow csv flx fml grd ///
grm jtr mis mze mzs oat olp olv oni pea phb pig pml rcd rcg rcw rsd rub rye sfl ///
soy spo srg sub suc swg tea tob tom whe wpo yam{
	append using `b`k''
}

* merge with crop_name
merge m:1 crp using "${fao_suit}/crop_name.dta", keep(1 3) nogen

* lavel variables
la var adm0 "Country-level administrative ISO"
la var admin0_name "Country name"
la var crp "Crop acronym"
la var extents "Total area of spatial unit in square kilometers (km2)"
la var suit_vs "very suitable land (km2)"
la var suit_s "suitable land (km2)"
la var suit_ms "moderately suitable land (km2)"
la var suit_vms "very marginally suitable land (km2)"
la var suit_ns "not suitable land (km2)"
la var ingredient "Ingredient name"

* keep variables
keep adm0 admin0_name crp extents suit_vs suit_s suit_ms suit_vms suit_ns ingredient

* generate suitability
gen suitability = (suit_s + suit_vs)/extents

* save data
save "${fao_suit}/suitability_FAO.dta", replace
