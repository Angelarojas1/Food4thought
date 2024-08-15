
   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * relaciona la complejidad de la cocina con variables del mercado      *
   *             laboral teniendo en cuenta la pandemia de 2020.          *
   *																	  *
   * - Inputs: ""			              *
   * - Output: ""     			  *
   * ******************************************************************** *

   ** IDS VAR:     wp5889    // Uniquely identifies people
   ** NOTES:
   ** WRITTEN BY:       Paola Poveda
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 29, 2023
   
   
   use "${recipes}/cuisine_complexity_all.dta",clear
   * use "${versatility}/reg_variables_cp.dta", clear

	** organize cookpad data
	preserve
	do "${code}/subcode/cookpad_reg.do"
	tempfile cookpad
	save `cookpad', replace
	restore
	
	** merge with cookpad
	quietly merge 1:m country using `cookpad'
	drop if _merge == 2
	* merge == 1 -> 21
	* drop _merge*

	quietly unique adm0
	assert `r(sum)' == 139

	* Create excel file with regression results:
		* Y = Employment variables
		* X = Complexity variables (interaction between time/ingredients/spices and fem)
		* Precovid period

	foreach v of varlist time* {
		gen l`v'=log(`v')
	}
	
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

			outreg2 using "${outputs}\Tables\cookpad\reg_summary_pre_2024.xls", lab dec(4) excel /// 	
			par(se) stats(coef se) keep(fem femx) addstat(mean.dep.var, `m') ///
			addtext(Complexity, "`lb'", period, "pre covid") nocons
			}
		
		drop femx
		}
		erase "${outputs}\Tables\cookpad\reg_summary_pre_2024.txt"	

	** Create regressions 

	* Regressions - Pre-covid
	
eststo clear	
	foreach w of varlist ltime_median ingredients_median spices_median {
	
		gen comp = fem*`w'	
		la var comp "Women x Complexity"
    
		local lb: variable label `w'
		
		* First Stage
		reghdfe comp fem fem_nat fem_imp hhsize if covid==0, absorb(niso ym) cluster(niso)
		eststo reg1`w'
		sum `w' if e(sample)
		local m_r `r(mean)'
		estadd scalar mean_r = `m_r'
		
		foreach v of varlist working emp_ftemp_pop emp_lfpr emp_work_hours {
	
		* OLS
		quietly reghdfe `v' fem comp hhsize if covid==0, absorb(niso ym) cluster(niso)
		
		eststo regh`v'
		sum `v' if e(sample)
		local m_ols `r(mean)'
		estadd scalar mean_ols = `m_ols'
	
		* IV 
		quietly ivreghdfe `v' fem  hhsize (comp = fem_nat fem_imp) if covid==0, absorb(niso ym)
		
		eststo iv`v'
		sum `v' if e(sample)
		local m_iv `r(mean)'
		estadd scalar mean_iv = `m_iv'
		
		** Create tables
		
		* For OLS regressions (Y is cuisine variable)
		esttab regh* using "${outputs}/Tables/cookpad_reg_ols_`w'.tex", ///
		b(3) se(3) r2 star(* 0.1 ** 0.05 *** .01) keep(fem comp) label ///
		s( r2  mean_ols N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace
		
		* For IV regressions (Y is cuisine variable)
		esttab iv* using "${outputs}/Tables/cookpad_reg_iv_`w'.tex", ///
		b(3) se(3) r2 star(* 0.1 ** 0.05 *** .01) keep(fem comp) label ///
		s( r2  mean_iv N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace
	} 
	
		** Create table
		
		* For First stage regressions (Y is cuisine variable)
		esttab reg1* using "${outputs}/Tables/cookpad_reg_1st.tex", ///
		b(3) se(3) r2 star(* 0.1 ** 0.05 *** .01) keep(fem fem_nat fem_imp) label ///
		mtitles("Time*Fem" "Ingredient*Fem" "Spices*Fem") ///
		s( r2  mean_r N, ///
		labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
		nobaselevels  prehead("\begin{tabular}{l*{4}{c}} \hline\hline") ///
		fragment postfoot("\hline" "\end{tabular}") replace

	drop comp
}


	*Descriptive statistics

	glo yv "working emp_ftemp_pop emp_lfpr emp_work_hours"
	glo yc "time* ingredients* spices* fem hhsize"

	eststo clear
	eststo a: estpost sum $yv $yc
	esttab a using "${outputs}\Tables\cookpad\tab-descriptives.rtf", cells("count(fmt(%9.0fc)) mean(fmt(2)) sd(fmt(%9.2fc)) min(fmt(%9.2fc)) max(fmt(%9.0fc))") collabels("Count" "Mean" "S.D." "Min." "Max.") title("Descriptive statistics") noobs label nonumbers nogaps compress replace
