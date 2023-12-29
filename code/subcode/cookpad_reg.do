
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *	        Keep only important variables for regressions		  	  *
   * - Inputs: "${cookpad}/Cookpad_clean.dta"			                  *
   * ******************************************************************** *

   ** IDS VAR:     wp5889    // Uniquely identifies people
   ** NOTES:
   ** WRITTEN BY:       Paola Poveda
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 29, 2023

   
	* Import data
	use "${cookpad}/Cookpad_clean.dta", clear
	
	* Three letter country code
	rename three_letter_country_code adm0
	encode adm0, gen(niso)
	
	* Covid variable	
	gen covid=(ym>=722)
*	tab ym covid

	* Employment variables
	recode emp_work_hours 98=. // Total Number of Hours Work Per Week
	replace emp_work_hours=0 if emp_unemp==1 // underemployment index
	replace emp_work_hours=0 if emp_lfpr==0 // Labor force participation index
	
	gen working= emp_lfpr
	recode working 1=0 if emp_unemp==1

	* Household size
	replace hhsize=. if hhsize<1 
	
	* Interaction
	gen cov_fem=covid*fem
	
	* Keep relevant variables
	keep wp5889 country adm0 working emp_ftemp_pop emp_lfpr emp_work_hours niso ym fem hhsize covid cov_fem
		
	* Label variables
	la var working 			"Employed"
	la var emp_ftemp_pop 	"Full time for employer"
	la var emp_lfpr 		"Labor participation"
	la var emp_work_hours 	"Hours worked per week"
	la var fem 				"Women"
	la var cov_fem 			"Covid x Women"