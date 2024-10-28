   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: In this code we create scatters x axis is versatility
   **			   and y axis is time
   ** Written by: Ángela Rojas
   ** Last modified: October 15, 2024
   
   *global today : display %tdCYND date(c(current_date), "DMY")
   *mkdir "${outputs}/data_check/scatter"

	* Import time data
	use "${recipes}/cuisine_complexity_sum.dta", clear
	gen logtime_median = log(time_median)
	
	* Merge with population data
	preserve
	use "${pop}/populationlong2019_2023.dta", clear
	keep if year == 2019
	
	* Keep top 10%
	egen p90 = pctile(pop), p(90)
	tempfile pop_19
	save `pop_19'
	restore
	
	* Merge with population data
	preserve
	use "${pop}/populationlong2019_2023.dta", clear
	keep if year == 2023
	
	* Keep top 10%
	egen p90 = pctile(pop), p(90)
	tempfile pop_23
	save `pop_23'
	restore
	
	foreach z in "p0" "p10" "p33" "p25" "p50" "p60" "p66" "p70" {
	preserve
	
	* Merge this with imported versatility data
	merge 1:1 adm0 using "${versatility}/imported/importbycountry_v2_`z'.dta"
	drop _merge
	egen std_import = std(importVersatility)
	
	merge 1:m adm0 using `pop_19', keep(3) nogen
	keep if pop >= p90
	
	* Create variables as we use them in the regressions

	twoway (scatter logtime_median importVersatility [w=pop]) ///
	(scatter logtime_median importVersatility, msy(none) mlab(country) leg(off) mlabsize(vsmall) mlabcolor(black)) , /// Outlier is cyprus
	xtitle("Imported Versatility `z'", size(small)) ytitle("", size(small)) ///
	xlabel(, nogrid) ylabel(,nogrid)  
	
	graph save "${outputs}/data_check/scatter/pop19_`z'.gph", replace
	
	
	merge 1:m adm0 using `pop_23', keep(3) nogen
	keep if pop >= p90
	
	* Create variables as we use them in the regressions

	twoway (scatter logtime_median importVersatility [w=pop]) ///
	(scatter logtime_median importVersatility, msy(none) mlab(country) leg(off) mlabsize(vsmall) mlabcolor(black)) , /// Outlier is cyprus
	xtitle("Imported Versatility `z'" ,size(small)) ytitle("", size(small)) ///
	xlabel(, nogrid) ylabel(,nogrid) 
	graph save "${outputs}/data_check/scatter/pop23_`z'.gph", replace
	
restore	
	}
	
	graph combine "${outputs}/data_check/scatter/pop19_p0.gph" "${outputs}/data_check/scatter/pop19_p10.gph" "${outputs}/data_check/scatter/pop19_p25.gph" "${outputs}/data_check/scatter/pop19_p33.gph" "${outputs}/data_check/scatter/pop19_p50.gph" "${outputs}/data_check/scatter/pop19_p60.gph" "${outputs}/data_check/scatter/pop19_p66.gph" "${outputs}/data_check/scatter/pop19_p70.gph", ycommon col(3) graphregion(color(white)) l1("Log Time Median", size(small)) note("Population data 2019")
	
	graph export "${outputs}/data_check/scatter/pop2019.png", replace
	
	* Combine graphs
	graph combine "${outputs}/data_check/scatter/pop23_p0.gph" "${outputs}/data_check/scatter/pop23_p10.gph" "${outputs}/data_check/scatter/pop23_p25.gph" "${outputs}/data_check/scatter/pop23_p33.gph" "${outputs}/data_check/scatter/pop23_p50.gph" "${outputs}/data_check/scatter/pop23_p60.gph" "${outputs}/data_check/scatter/pop23_p66.gph" "${outputs}/data_check/scatter/pop23_p70.gph", ycommon col(3) graphregion(color(white)) l1("Log Time Median", size(small)) note("Population data 2023")
	
	graph export "${outputs}/data_check/scatter/pop2023.png", replace
	
