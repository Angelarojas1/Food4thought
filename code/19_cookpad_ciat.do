
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * relaciona la complejidad de la cocina con variables del mercado      *
   *             laboral teniendo en cuenta la pandemia de 2020.          *
   *																	  *
   * - Inputs: "${rawdata}/cookpad/Cookpad_032023.dta"	                  *
   *           "${codedata}/merge/p50.dta"                                *
   * - Output: "${outputs}/Tables/ivreg_`val'_`var'.tex"     			  *
   * ******************************************************************** *

   ** IDS VAR:     wp5889    // Uniquely identifies people
   ** NOTES:
   ** WRITTEN BY:       Paola Poveda
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 12, 2023

   
	* Import data
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
	merge m:1 country using "${codedata}/recipes/recipe_sum_all.dta"
	*merge m:1 country using "${codedata}/merge/p50.dta"
	
	tab country if _merge==1
	levelsof country if _merge == 3
	display "`r(r)'" ingredients_mean
	* merge == 1 -> 36
	* merge == 2 -> 21
	* merge == 3 -> 114
	
	* Create interaction between gender and IV variable
	*gen fem_nat = fem*std_native
	*gen fem_imp = fem*std_import
	
	* Create log time 
	foreach v of varlist time* {
		gen l`v'=log(`v')
	}
	
	* Label variables
	la var working 			"Employed"
	la var emp_ftemp_pop 	"Full time for employer"
	la var emp_lfpr 		"Labor participation"
	la var emp_work_hours 	"Hours worked per week"
	la var fem 				"Women"
	la var cov_fem 			"Covid x Women"
	*la var fem_nat 		"Women x Native versatility"
	*la var fem_imp 		"Women x Imported versatility"
	
	local time "Time recipes"
	local ingredients "Num ingredients"
	local spices "Num spices"
	
	foreach v in time ingredients spices {
		foreach k in mean median p10 p25 p75 p90 {
			la var `v'_`k' "``v'' `k'"	
		}
	}

	foreach k in mean median p10 p25 p75 p90 {
 		la var ltime_`k' "Log time `k'"	
	}

*------------------------------------------------------------------------------*
	* Regressions
	
	* Using database without versatility variables
	
		*pre covid
		foreach w of varlist ltime* ingredients* spices* {
    
			gen femx = fem*`w'
			la var femx "Women x Complexity"
	
			local lb: variable label `w'
	
			foreach v of varlist working emp_ftemp_pop emp_lfpr emp_work_hours {
	
			reghdfe `v' fem femx hhsize if covid==0, absorb(niso ym) cluster(niso)
 
			sum `v' if e(sample)
			local m `r(mean)'

			outreg2 using "${outputs}\Tables\reg_summary_pre.xls", lab dec(4) excel par(se) stats(coef se) keep(fem femx) addstat(mean.dep.var, `m') addtext(Complexity, "`lb'", period, "pre covid") nocons
}
drop femx
}
erase "${outputs}\Tables\reg_summary_pre.txt"

/*
	* Pre-covid
	foreach w of varlist logmtime mIng mSpice {
	
		gen comp = fem*`w'	
    
		local lb: variable label `w'
		
		* OLS		
		reghdfe working fem comp hhsize if covid==0, absorb(niso ym) cluster(niso)
		
		* First Stage. Should I add controls?
		* reghdfe comp fem fem_nat fem_imp hhsize, absorb(niso ym) cluster(niso)
		*reghdfe comp fem fem_nat fem_imp hhsize, absorb(continentFactor ym) cluster(niso) 

		drop comp
	*		sum `w' if e(sample)
	*		local m `r(mean)'

*	outreg2 using "${outputs}\Tables\reg-fem-pre-vers.xls", lab dec(4) excel par(se) stats(coef se) keep(fem fem_nat fem_imp) addstat(mean.dep.var, `m') addtext(Complexity, "`lb'", period, "2018-2023") nocons
}


*estadisticas descriptivas

glo yv "working emp_ftemp_pop emp_lfpr emp_work_hours"
glo yc "time* ingredients* spices* fem hhsize"

eststo clear
eststo a: estpost sum $yv $yc
*esttab a using "tab-descriptives.rtf", cells("count(fmt(%9.0fc)) mean(fmt(2)) sd(fmt(%9.2fc)) min(fmt(%9.2fc)) max(fmt(%9.0fc))") collabels("Count" "Mean" "S.D." "Min." "Max.") title("Descriptive statistics") noobs label nonumbers nogaps compress replace
