
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * relaciona la complejidad de la cocina con variables del mercado      *
   *             laboral teniendo en cuenta la pandemia de 2020.          *
   *																	  *
   * - Inputs: "${cookpad}/Cookpad_clean.dta"			                  *
   *           "${recipes}/cuisine_complexity_all.dta"                    *
   *           "${versatility}/reg_variables.dta"	                      *
   * - Output: "${outputs}/Tables/ivreg_`val'_`var'.tex"     			  *
   * ******************************************************************** *

   ** IDS VAR:     wp5889    // Uniquely identifies people
   ** NOTES:
   ** WRITTEN BY:       Paola Poveda
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 12, 2023

   
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
	

	* Merge with cuisine database that contains time, ingredients, versatility, geographical variables
	merge m:1 country using "${versatility}/reg_variables.dta"
	
	levelsof country if _merge == 3
	display "`r(r)'"
	* merge == 3 -> 118
	
	* Create log time 
	foreach v of varlist time* {
		gen l`v'=log(`v')
	}
	
	* Create interaction between gender and IV variable
	gen fem_nat = fem*std_native
	gen fem_imp = fem*std_import

	* Label variables
	la var fem_nat 		"Women x Native versatility"
	la var fem_imp 		"Women x Imported versatility"
	
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
	
	
	* Create excel file with regression results:
			* Y = Employment variables
			* X = Complexity variables (interaction between time/ingredients/spices and fem)
			* Precovid period

		foreach w of varlist ltime* ingredients* spices* {
			
			* Create complexity variables
			gen femx = fem*`w'
			la var femx "Women x Complexity"
	
			local lb: variable label `w'
			
			* Run regressions with employment variables
			foreach v of varlist working emp_ftemp_pop emp_lfpr emp_work_hours {
	
			reghdfe `v' fem femx hhsize if covid==0, absorb(niso ym) cluster(niso)
 
			sum `v' if e(sample)
			local m `r(mean)'

			outreg2 using "${outputs}\Tables\reg_summary_pre.xls", lab dec(4) excel /// 	
			par(se) stats(coef se) keep(fem femx) addstat(mean.dep.var, `m') ///
			addtext(Complexity, "`lb'", period, "pre covid") nocons
			}
		drop femx
		}
		erase "${outputs}\Tables\reg_summary_pre.txt"	

	
	** Create regressions 

	* Regressions - Pre-covid
	
	foreach w of varlist time_median ingredients_median spices_median {
	
		gen comp = fem*`w'	
    
		local lb: variable label `w'
		
		* First Stage
		reghdfe comp fem fem_nat fem_imp hhsize , absorb(niso ym) cluster(niso)
		eststo reg1
		sum `w' if e(sample)
		local m `r(mean)'
		estadd scalar mean = `mean'
		
		foreach v of varlist working emp_ftemp_pop emp_lfpr emp_work_hours {
		
		* OLS
		reghdfe `v' fem comp hhsize if covid==0, absorb(niso ym) cluster(niso)
		
		eststo regh`v'
		sum work if e(sample)
		local m `r(mean)'
		estadd scalar mean = `mean'
		
		* IV 
		ivreghdfe `v' fem (comp = fem_nat fem_imp) hhsize if covid==0, absorb(niso ym) cluster(niso)
		
		eststo iv`v'
		sum work if e(sample)
		local m `r(mean)'
		estadd scalar mean = `mean'

		
		** Create tables
		
		* For First stage regressions (Y is cuisine variable)
		esttab reg1 using "${outputs}/Tables/cookpad_reg_`w'.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(fem_nat fem_imp)label ///
		mtitles("First stage")  ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{3}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace
		
		* For OLS regressions (Y is cuisine variable)
		esttab regh* using "${outputs}/Tables/cookpad_reg_ols_`w'.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(fem_nat fem_imp comp)label ///
		mtitles("working" "emp_ftemp_pop" "emp_lfpr" "emp_work_hour")  ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{3}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace
		
		* For OLS regressions (Y is cuisine variable)
		esttab iv* using "${outputs}/Tables/cookpad_reg_ols_`w'.tex", ///
		se r2 star(* 0.1 ** 0.05 *** .01) keep(fem_nat fem_imp comp)label ///
		mtitles("working" "emp_ftemp_pop" "emp_lfpr" "emp_work_hour")  ///
		s( r2  mean N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{3}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace
	}
	
	drop comp
}


	*Descriptive statistics

	glo yv "working emp_ftemp_pop emp_lfpr emp_work_hours"
	glo yc "time* ingredients* spices* fem hhsize"

	eststo clear
	eststo a: estpost sum $yv $yc
	esttab a using "${outputs}\Tables\tab-descriptives.rtf", cells("count(fmt(%9.0fc)) mean(fmt(2)) sd(fmt(%9.2fc)) min(fmt(%9.2fc)) max(fmt(%9.0fc))") collabels("Count" "Mean" "S.D." "Min." "Max.") title("Descriptive statistics") noobs label nonumbers nogaps compress replace
