   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * 				 This dofile cleans cookpad database				  *
   *																	  *
   * - Inputs: "${rawdata}/cookpad/Cookpad_032023.dta"				      *
   * - Output: "${cookpad}/Cookpad_clean.dta"						      *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 13, 2023

****************************************
* Data cleaning for cookpad 
****************************************

	*import data
	use "${rawdata}/cookpad/Cookpad_032023.dta", clear

	rename *, lower

	* Organize gender variable
	recode wp1219 (1=0) (2=1), gen(fem)
	
	* Study Completion Date
	gen y=yofd(field_date)
	gen ym=mofd(field_date)
	gen month=month(field_date)
	
	* Organize country variable
	rename countrynew country

	replace country="Bosnia And Herzegovina" if country=="Bosnia Herzegovina"
	replace country="Cote D'Ivoire" if country=="Ivory Coast"
	

	* rename variables
	rename (country_iso3 wgt year_wave wp19967 wp19960 wp19975 wp19968 wp1219) ( three_letter_country_code weight year numLunCook numLunEat numDinCook numDinEat gender)

	* replace missing values
	foreach var of varlist numLunCook numLunEat numDinCook numDinEat{
		replace `var' = . if `var' == 98 | `var' == 99
	}

* save dataset
save "${cookpad}/Cookpad_clean.dta", replace

