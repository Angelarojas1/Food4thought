* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: 
* 				Last date modified: June 16, 2025 						   	   *
*				Cookpad Data Exploration
* **************************************************************************** *	

	********************************************
	**#  		Regressions -  COOKPAD 	       *
	**# Region FE
	********************************************
	
	use "$cookpad/cookpad_adm0.dta", replace
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
		
		foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability al_mn"
	global c3 "numrecipes avg_suitability al_mn GDP"
	global c4 "numrecipes avg_suitability al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes avg_suitability al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c6 "numrecipes"
	global c7 "numrecipes avg_suitability trade_distCapital_2000 al_mn"
	global c8 "numrecipes avg_suitability trade_distCapital_2000 al_mn GDP"
	global c9 "numrecipes avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon GDP"
	global c10 "numrecipes  avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c11 "numrecipes"
	global c12 "numrecipes avg_suitability trade_distCapital_3000 al_mn"
	global c13 "numrecipes avg_suitability trade_distCapital_3000 al_mn GDP"
	global c14 "numrecipes avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon GDP"
	global c15"numrecipes  avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	encode region, gen(region_cat)
	
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	*-------- FLFP --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 1, absorb(region_cat cl_md ym) cluster(adm0) 
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 1, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 1, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 
	 estout using reg_flfp_OLS_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	*-------- MLFP --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 0, absorb(region_cat cl_md ym) cluster(adm0) 
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 estout using reg_mlfp_OLS_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	*-------- Gap --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr i.fem##c.median_totaltime  ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.w_mean_spices ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.median_ingredients ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 estout using reg_gap_OLS_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.median_totaltime median_totaltime 1.fem#c.w_mean_spices w_mean_spices 1.fem#c.median_ingredients median_ingredients) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

	
	*------------------------------------------*
	**#  	        First Stage                *
	*------------------------------------------*
	
	*-------- FLFP --------*

	eststo clear

	 forvalue i=1/5 { 
	eststo: reghdfe w_mean_spices c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5 { 
	eststo: reghdfe w_mean_spices c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10 { 
	eststo: reghdfe w_mean_spices c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15 { 
	eststo: reghdfe w_mean_spices c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_fs_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
	
			*-------- MLFP --------*

	eststo clear

	 forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe w_mean_spices c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe w_mean_spices c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_fs_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

	*-------- GAP --------*

	eststo clear

	forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices 1.fem#c.vers_distCapital_2000 ${c`i'} fem vers_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices 1.fem#c.vers_distCapital_3000 ${c`i'} fem vers_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe w_mean_spices 1.fem#c.vers_distCapital_2000 ${c`i'} fem vers_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe w_mean_spices 1.fem#c.vers_distCapital_3000 ${c`i'} fem vers_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_gap_fs_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.vers_distCapital_2000 vers_distCapital_2000 1.fem#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace


	*------------------------------------------*
	**#  	        Reduced form               *
	*------------------------------------------*
	
	*-------- FLFP --------*

	eststo clear
// 	forvalue i=1/5 { 
// 	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 1, absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5 { 
// 	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 1, absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	 forvalue i=1/5 { 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5 { 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10 { 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15 { 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
	
		*-------- MLFP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 0 , absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 0, absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	 	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(region_cat cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
			*-------- GAP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers ${c`i'} if covid == 0, absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers2 ${c`i'} if covid == 0, absorb(region_cat cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	 	 forvalue i=1/5{ 
	eststo: reghdfe lfpr 1.fem#c.vers_distCapital_2000 ${c`i'} fem vers_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr 1.fem#c.vers_distCapital_3000 ${c`i'} fem vers_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe lfpr 1.fem#c.vers_distCapital_2000 ${c`i'} fem vers_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe lfpr 1.fem#c.vers_distCapital_3000 ${c`i'} fem vers_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(i.region_cat i.fem cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF_cookpad.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.vers_distCapital_2000 vers_distCapital_2000 1.fem#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	*------------------------------------------*
	**#   IV  - native spices versatility       *
	*------------------------------------------*

	*-------- FLFP --------*

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if if covid == 0 & fem == 1 , robust cluster(adm0) 
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if covid == 0 & fem == 1 , robust cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 1 & vers_distCapital_2000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 1 & vers_distCapital_2000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_flfp_IV_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
	
		*-------- MLFP --------*

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 , robust cluster(adm0) 
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 , robust cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
	
		forvalue i=1/5{ 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5{ 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.region_cat i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}


	cd "${tables}"

	* Export table with F-stat
	estout using reg_mlfp_IV_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

		*-------- Gap --------*
		
	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers native_spice_vers) fem ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if covid == 0, robust cluster(adm0) 
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers2 native_spice_vers2) fem ${c`i'} ///
// 		i.region_cat i.cl_md i.ym if covid == 0, robust cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) ${c`i'}  ///
		i.region_cat i.fem i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) ${c`i'}  ///
		i.region_cat i.fem i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.region_cat i.fem i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.region_cat i.fem i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_gap_IV_cookpad.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.w_mean_spices w_mean_spices) ///
		drop(_cons 0.fem* *.region_cat* *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
	
	********************************************
	**#  		Regressions -  COOKPAD 	       *
	**# Country FE
	********************************************
	
	use "$cookpad/cookpad_adm0.dta", replace
	
	encode adm0, gen(adm0_code)
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
	
		foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability al_mn"
	global c3 "numrecipes avg_suitability al_mn GDP"
	global c4 "numrecipes avg_suitability al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes avg_suitability al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c6 "numrecipes"
	global c7 "numrecipes avg_suitability trade_distCapital_2000 al_mn"
	global c8 "numrecipes avg_suitability trade_distCapital_2000 al_mn GDP"
	global c9 "numrecipes avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon GDP"
	global c10 "numrecipes  avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c11 "numrecipes"
	global c12 "numrecipes avg_suitability trade_distCapital_3000 al_mn"
	global c13 "numrecipes avg_suitability trade_distCapital_3000 al_mn GDP"
	global c14 "numrecipes avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon GDP"
	global c15"numrecipes  avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	*-------- Gap --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr i.fem##c.median_totaltime  ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.w_mean_spices ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.median_ingredients ${c`i'} if covid == 0, absorb(adm0 cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 estout using reg_gap_OLS_cookpad_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.median_totaltime median_totaltime 1.fem#c.w_mean_spices w_mean_spices 1.fem#c.median_ingredients median_ingredients) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

	*------------------------------------------*
	**#  	        Reduced form               *
	*------------------------------------------*
			
			*-------- GAP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers ${c`i'} if covid == 0, absorb(adm0_code cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers2 ${c`i'} if covid == 0, absorb(adm0_code cl_md ym) cluster(adm0) 
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_2000 ${c`i'} if covid == 0 & vers_distCapital_2000 != 0, absorb(adm0_code cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_3000 ${c`i'} if covid == 0 & vers_distCapital_3000 != 0, absorb(adm0_code cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_2000 ${c`i'} i.fem#c.trade_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(adm0_code cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_3000 ${c`i'} i.fem#c.trade_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(adm0_code cl_md ym) cluster(adm0) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF_cookpad_c.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.vers_distCapital_2000 vers_distCapital_2000 1.fem#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	*------------------------------------------*
	**#   IV  - native spices versatility       *
	*------------------------------------------*

		*-------- Gap --------*
		
	//	gen femx = fem*w_mean_spices
	// ivreg2 lfpr (i.fem#c.w_mean_spices w_mean_spices = i.fem#c.native_spice_vers native_spice_vers) fem ${c`i'}

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers native_spice_vers) fem ${c`i'} ///
// 		i.adm0_code i.cl_md i.ym if covid == 0, robust cluster(adm0) 
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers2 native_spice_vers2) fem ${c`i'} ///
// 		i.adm0_code i.cl_md i.ym if covid == 0, robust cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) fem ${c`i'}  ///
		i.adm0_code i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) fem ${c`i'}  ///
		i.adm0_code i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) fem i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.adm0_code i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) fem i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.adm0_code i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_gap_IV_cookpad_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.w_mean_spices w_mean_spices) ///
		drop(_cons 0.fem* *.adm0_code *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
	
	********************************************
	**#  		Regressions -  COOKPAD 	       *
	**# Correcting migrants data 			   *
	********************************************
	
	use "$cookpad/cookpad_adm0_m.dta", replace
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
										
	preserve 
	use "${versatility}\native_versatility_m_c_dist.dta", clear
	collapse (mean) native_spice_vers2_dist, by(adm0)
	tempfile distance
	save `distance'
	restore

	merge m:1 adm0 using `distance', keep(3) nogen
	
	* relabel everything
	foreach v of varlist * {
		local lbl : variable label `v'

		* Clean up symbols
		local lblclean : subinstr local lbl "_" " ", all
		local lblclean : subinstr local lblclean "(" "", all
		local lblclean : subinstr local lblclean ")" "", all

		* Remove "mean " if it occurs at the beginning (within first 5 characters)
		if strpos(lower(substr("`lblclean'", 1, 5)), "mean") {
			local lblclean = substr("`lblclean'", 6, .)
		}

		label variable `v' "`lblclean'"
	}
	
 
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability  al_mn"
	global c3 "numrecipes avg_suitability  al_mn GDP"
	global c4 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	encode region, gen(region_cat)

	
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	*-------- FLFP --------*

	 cd "$tables"
	eststo clear
	forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	}
	forvalue i=1/5{ 
		eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
 }
	 forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
 }

	 estout using reg_flfp_OLS_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		
	
	*-------- MLFP --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 estout using reg_mlfp_OLS_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		
	*-------- Gap --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr i.fem##c.median_totaltime  ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.w_mean_spices ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.median_ingredients ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 estout using reg_gap_OLS_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.median_totaltime median_totaltime 1.fem#c.w_mean_spices w_mean_spices 1.fem#c.median_ingredients median_ingredients) ///
		drop(_cons 0.fem 0.fem#c.median_totaltime 0.fem#c.w_mean_spices 0.fem#c.median_ingredients) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
	
	*------------------------------------------*
	**#  	        Reduced form               *
	*------------------------------------------*
	
	*-------- FLFP --------*

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers2_dist ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_cook_m.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
	
		*-------- MLFP --------*

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.native_spice_vers2_dist ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF_cook_m.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
	
	*-------- GAP --------*

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.native_spice_vers ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.native_spice_vers2 ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.native_spice_vers2_dist ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF_cook_m.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.native_spice_vers native_spice_vers 1.fem#c.native_spice_vers2 native_spice_vers2 1.fem#c.native_spice_vers2_dist native_spice_vers2_dist) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		
	*------------------------------------------*
	**#   IV  - native spices versatility       *
	*------------------------------------------*
	encode adm0_fe, gen(adm0_fe_code)
	
	*-------- FLFP --------*

	eststo clear

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym if fem == 1 , robust cluster(adm0_fe) 
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym if fem == 1 , robust cluster(adm0_fe)
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2_dist) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if fem == 1 , robust cluster(adm0_fe)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_flfp_IV_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
	
		*-------- MLFP --------*

	eststo clear

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym if fem == 0 , robust cluster(adm0_fe) 
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym if fem == 0 , robust cluster(adm0_fe)
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2_dist) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if fem == 0 , robust cluster(adm0_fe)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_mlfp_IV_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

	*-------- Gap --------*
	eststo clear

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers native_spice_vers) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym, robust cluster(adm0_fe) 
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers2 native_spice_vers2) ${c`i'} ///
		i.adm0_fe_code i.cl_md i.ym, robust cluster(adm0_fe)
	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers2_dist native_spice_vers2_dist) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym, robust cluster(adm0_fe)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_gap_IV_cook_m.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.w_mean_spices w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym 0.fem#c.w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
		
		
	********************************************
	**#  		Regressions -  COOKPAD 	       *
	**# Only migrants data 			   *
	********************************************
	
	use "$cookpad/cookpad_adm0_m.dta", replace
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
							
	*-- Only keep data for migrants
	keep if country_fe != country
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
	
	* relabel everything
	foreach v of varlist * {
		local lbl : variable label `v'

		* Clean up symbols
		local lblclean : subinstr local lbl "_" " ", all
		local lblclean : subinstr local lblclean "(" "", all
		local lblclean : subinstr local lblclean ")" "", all

		* Remove "mean " if it occurs at the beginning (within first 5 characters)
		if strpos(lower(substr("`lblclean'", 1, 5)), "mean") {
			local lblclean = substr("`lblclean'", 6, .)
		}

		label variable `v' "`lblclean'"
	}
	
	foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability al_mn"
	global c3 "numrecipes avg_suitability al_mn GDP"
	global c4 "numrecipes avg_suitability al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes avg_suitability al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c6 "numrecipes"
	global c7 "numrecipes avg_suitability trade_distCapital_2000 al_mn"
	global c8 "numrecipes avg_suitability trade_distCapital_2000 al_mn GDP"
	global c9 "numrecipes avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon GDP"
	global c10 "numrecipes  avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c11 "numrecipes"
	global c12 "numrecipes avg_suitability trade_distCapital_3000 al_mn"
	global c13 "numrecipes avg_suitability trade_distCapital_3000 al_mn GDP"
	global c14 "numrecipes avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon GDP"
	global c15"numrecipes  avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	encode region, gen(region_cat)
	
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	*-------- FLFP --------*

	 cd "$tables"
	eststo clear
	forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	}
	forvalue i=1/5{ 
		eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
 }
	 forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
 }

	 estout using reg_flfp_OLS_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		
	
	*-------- MLFP --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr c.median_totaltime  ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr c.w_mean_spices ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.median_ingredients ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 estout using reg_mlfp_OLS_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(median_totaltime w_mean_spices median_ingredients) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		
	*-------- Gap --------*

	 cd "$tables"
		eststo clear
		forvalue i=1/5{ 
		eststo: reghdfe lfpr i.fem##c.median_totaltime  ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
		}
		forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.w_mean_spices ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.median_ingredients ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	 }

	 estout using reg_gap_OLS_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.median_totaltime median_totaltime 1.fem#c.w_mean_spices w_mean_spices 1.fem#c.median_ingredients median_ingredients) ///
		drop(_cons 0.fem 0.fem#c.median_totaltime 0.fem#c.w_mean_spices 0.fem#c.median_ingredients) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
	
	*------------------------------------------*
	**#  	        Reduced form               *
	*------------------------------------------*
	
	*-------- FLFP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 1, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5 { 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10 { 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15 { 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 1 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_cook_m_o.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
	
		*-------- MLFP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr c.native_spice_vers2 ${c`i'} if covid == 0 & fem == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe lfpr c.vers_distCapital_2000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe lfpr c.vers_distCapital_3000 ${c`i'} if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF_cook_m_o.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	
	*-------- GAP --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe lfpr i.fem##c.native_spice_vers2 ${c`i'} if covid == 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
// 	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_2000 ${c`i'} if covid == 0 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_3000 ${c`i'} if covid == 0 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_2000 ${c`i'} i.fem#c.trade_distCapital_2000 if covid == 0 & vers_distCapital_2000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe lfpr i.fem##c.vers_distCapital_3000 ${c`i'} i.fem#c.trade_distCapital_3000 if covid == 0 & vers_distCapital_3000 != 0, absorb(adm0_fe cl_md ym) cluster(adm0_fe) 
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF_cook_m_o.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.vers_distCapital_2000 vers_distCapital_2000 1.fem#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFPR" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace
		
	*------------------------------------------*
	**#   IV  - native spices versatility       *
	*------------------------------------------*
	
	encode adm0_fe, gen(adm0_fe_code)
	
	*-------- FLFP --------*

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym if fem == 1 , robust cluster(adm0_fe) 
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym if fem == 1 , robust cluster(adm0_fe)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & fem == 1 & vers_distCapital_2000 != 0 , robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if  covid == 0 & fem == 1 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if  covid == 0 & fem == 1 & vers_distCapital_2000 != 0 , robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if  covid == 0 & fem == 1 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_flfp_IV_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
		
		*-------- MLFP --------*

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym if fem == 0 , robust cluster(adm0_fe) 
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices = native_spice_vers2) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym if fem == 0 , robust cluster(adm0_fe)
// 	}
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if fem == 0 & vers_distCapital_2000 != 0 , robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	forvalue i=1/5{ 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.adm0_fe_code  i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_2000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_2000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices = vers_distCapital_3000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & fem == 0 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_mlfp_IV_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

	*-------- Gap --------*
	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers native_spice_vers) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym, robust cluster(adm0_fe) 
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.native_spice_vers2 native_spice_vers2) ${c`i'} ///
// 		i.adm0_fe_code i.cl_md i.ym, robust cluster(adm0_fe)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) fem ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_2000 vers_distCapital_2000) fem i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & vers_distCapital_2000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 lfpr (w_mean_spices i.fem#c.w_mean_spices = i.fem#c.vers_distCapital_3000 vers_distCapital_3000) fem i.fem#c.trade_distCapital_2000 ${c`i'}  ///
		i.adm0_fe_code i.cl_md i.ym if covid == 0 & vers_distCapital_3000 != 0, robust cluster(adm0_fe)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}


	cd "${tables}"

	* Export table with F-stat
	estout using reg_gap_IV_cook_m_o.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem#c.w_mean_spices w_mean_spices) ///
		drop(_cons *.adm0_fe_code *.cl_md *.ym 0.fem#c.w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFPR" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

		
	