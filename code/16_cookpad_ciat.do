
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * relaciona la complejidad de la cocina con variables del mercado      *
   *             laboral teniendo en cuenta la pandemia de 2020.          *
   *																	  *
   * - Inputs: "${rawdata}\cookpad\Cookpad_032023.dta"	                  *
   *           "${codedata}/merge/p50.dta"                                *
   * - Output: "${outputs}/Tables/ivreg_`val'_`var'.tex"     			  *
   * ******************************************************************** *

   ** IDS VAR:                 // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Paola Poveda
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: 

   
	* Import data
	use "${rawdata}\cookpad\Cookpad_032023.dta", clear
	rename *, lower

	* Organize gender variable
	recode wp1219 (1=0) (2=1), gen(fem)

	* Study Completion Date
	gen y=yofd(field_date)
	gen ym=mofd(field_date)
	gen month=month(field_date)
	
	* Organize country variable
	rename countrynew country

	replace country="Bosnia and Herzegovina" if country=="Bosnia Herzegovina"
	replace country="Cote d'Ivoire" if country=="Ivory Coast"
	
*use "${codedata}/merge/p50.dta", clear
	* Three letter country code
	rename country_iso3 adm0
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

	* Add recipes vbs (time, ingredients, spices)
	merge m:1 adm0 using "${codedata}/merge/p50.dta"
	levelsof country if _merge == 2
	display "`r(r)'"
	* merge == 1 -> 36
	* merge == 2 -> 21
	* merge == 3 -> 114
	
	* Create interaction between gender and IV variable
	gen fem_nat = fem*std_native
	gen fem_imp = fem*std_import
	
	* Label variables
	la var working 			"Employed"
	la var emp_ftemp_pop 	"Full time for employer"
	la var emp_lfpr 		"Labor participation"
	la var emp_work_hours 	"Hours worked per week"
	la var fem 				"Women"
	la var cov_fem 			"Covid x Women"
	la var fem_nat 			"Women x Native versatility"
	la var fem_imp 			"Women x Imported versatility"
	la var logmtime			"Log time"

*------------------------------------------------------------------------------*
	* Regressions
	
	* Whole sample
	foreach w of varlist logmtime mIng mSpice {
    
		local lb: variable label `w'
		
		reghdfe `w' std_native std_import fem_nat fem_imp fem hhsize, absorb(niso ym) cluster(niso)
 
			sum `w' if e(sample)
			local m `r(mean)'

*	outreg2 using "${outputs}\Tables\reg-fem-vers.xls", lab dec(4) excel par(se) stats(coef se) keep(fem fem_nat fem_imp) addstat(mean.dep.var, `m') addtext(Complexity, "`lb'", period, "2018-2023") nocons
}


	* pre covid
	
	foreach w of varlist logmtime mIng mSpice {
	
	local lb: variable label `w'
	
	reghdfe `w' std_native std_import fem_nat fem_imp fem hhsize if covid==0, absorb(niso ym) cluster(niso)
 
 	sum `w' if e(sample)
	local m `r(mean)'

*	outreg2 using "${outputs}\Tables\reg-fem-pre-vers.xls", lab dec(4) excel par(se) stats(coef se) keep(fem femx) addstat(mean.dep.var, `m') addtext(Complexity, "`lb'", period, "pre covid") nocons
}



*estadisticas descriptivas

glo yv "working emp_ftemp_pop emp_lfpr emp_work_hours"
glo yc "time* ingredients* spices* fem hhsize"

eststo clear
eststo a: estpost sum $yv $yc
*esttab a using "tab-descriptives.rtf", cells("count(fmt(%9.0fc)) mean(fmt(2)) sd(fmt(%9.2fc)) min(fmt(%9.2fc)) max(fmt(%9.0fc))") collabels("Count" "Mean" "S.D." "Min." "Max.") title("Descriptive statistics") noobs label nonumbers nogaps compress replace
