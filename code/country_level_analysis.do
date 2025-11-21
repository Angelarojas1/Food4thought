   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile runs reduced form estimation	        	  *
   *																	  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** Created: 			20251004
   ** EDITTED BY:       
   ** Last date modified: 
   

	********************************************
**#	* 		Regressions - interactions	 	   *
	* Region FE
	********************************************
	

	use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
		
	foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA con las variables estandarizadas
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
	
	label var pca_index "PCA Index"
	

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
	
	*-------- First Stage --------*

	eststo clear
	 forvalue i=1/5{ 
	eststo: reghdfe pca_index i.fem_lfp##c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe pca_index i.fem_lfp##c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe pca_index i.fem_lfp##c.vers_distCapital_2000 ${c`i'} i.fem_lfp#c.trade_distCapital_2000 if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe pca_index i.fem_lfp##c.vers_distCapital_3000 ${c`i'} i.fem_lfp#c.trade_distCapital_3000 if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 
	estout using reg-fs-pca-gap.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order( 1.fem_lfp#c.vers_distCapital_2000 vers_distCapital_2000  1.fem_lfp#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace


	*-------- OLS --------*
	
	 cd "$tables"
	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP i.fem_lfp##c.pca_index ${c`i'}, absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 
	estout using reg-ols-gap-pca.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem_lfp#c.pca_index pca_index) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace


// 	 cd "$tables"
// 	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP i.fem_lfp##c.median_totaltime ${c`i'}, absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	 forvalue i=1/5{ 
// 	eststo: reghdfe LFP i.fem_lfp##c.w_mean_spices ${c`i'}, absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	 forvalue i=1/5{ 
// 	eststo: reghdfe LFP i.fem_lfp##c.median_ingredients ${c`i'}, absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
//	 
// 	estout using reg-ols-gap.tex, ///
// 		style(tex) ///
// 		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
// 		postfoot("\bottomrule" "\end{tabular}") ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		order(1.fem_lfp#c.median_totaltime median_totaltime 1.fem_lfp#c.w_mean_spices w_mean_spices 1.fem_lfp#c.median_ingredients median_ingredients) ///
// 		drop(_cons 0.fem*) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
//     replace


	*-------- Reduced Form --------*

	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers2 ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	 forvalue i=1/5{ 
	eststo: reghdfe LFP i.fem_lfp##c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe LFP i.fem_lfp##c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=7/10{ 
	eststo: reghdfe LFP i.fem_lfp##c.vers_distCapital_2000 ${c`i'} i.fem_lfp#c.trade_distCapital_2000 if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 forvalue i=12/15{ 
	eststo: reghdfe LFP i.fem_lfp##c.vers_distCapital_3000 ${c`i'} i.fem_lfp#c.trade_distCapital_3000 if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	 
	estout using reg-rf-gap.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order( 1.fem_lfp#c.vers_distCapital_2000 vers_distCapital_2000  1.fem_lfp#c.vers_distCapital_3000 vers_distCapital_3000) ///
		drop(_cons 0.fem*) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

	
	*-------- IV --------*
	
	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP (w_mean_spices i.fem_lfp#c.w_mean_spices = i.fem_lfp#c.native_spice_vers native_spice_vers) fem_lfp ${c`i'} ///
// 		i.region_cat i.cl_md , robust cluster(adm0) 
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP (w_mean_spices i.fem_lfp#c.w_mean_spices = i.fem_lfp#c.native_spice_vers2 native_spice_vers2) fem_lfp ${c`i'} ///
// 		i.region_cat i.cl_md , robust cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}

	forvalue i=1/5 { 
		eststo: ivreg2 LFP (pca_index i.fem_lfp#c.pca_index = i.fem_lfp#c.vers_distCapital_2000 vers_distCapital_2000) fem_lfp ${c`i'}  ///
		i.region_cat i.cl_md if vers_distCapital_2000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=1/5 { 
		eststo: ivreg2 LFP (pca_index i.fem_lfp#c.pca_index = i.fem_lfp#c.vers_distCapital_3000 vers_distCapital_3000) fem_lfp ${c`i'}  ///
		i.region_cat i.cl_md if vers_distCapital_3000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10 { 
		eststo: ivreg2 LFP (pca_index i.fem_lfp#c.pca_index = i.fem_lfp#c.vers_distCapital_2000 vers_distCapital_2000) fem_lfp ${c`i'} i.fem_lfp#c.trade_distCapital_2000 ///
		i.region_cat i.cl_md if vers_distCapital_2000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	forvalue i=12/15 { 
		eststo: ivreg2 LFP (pca_index i.fem_lfp#c.pca_index = i.fem_lfp#c.vers_distCapital_3000 vers_distCapital_3000) fem_lfp ${c`i'} i.fem_lfp#c.trade_distCapital_3000 ///
		i.region_cat i.cl_md if vers_distCapital_3000 != 0 , robust cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_gap_pca_IV.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(1.fem_lfp#c.pca_index pca_index) ///
		drop(_cons 0.fem* *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFP" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

	********************************************
**#	*   		     Regressions 	 	       *
	* No interactions
	* Y = FLFP / MLFP
	* Use GDP as a control
	* Region and climate FE
	********************************************

	use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear

	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)	
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA con las variables estandarizadas
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
		
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

	gen LFP_female = LFP if fem_lfp == 1
	gen LFP_male   = LFP if fem_lfp == 0

	* creating the LFP gap at the country-level
	collapse (mean) $c5 LFP_male LFP_female median_spices w_mean_spices vers_distCapital_2000 vers_distCapital_3000 trade_distCapital_2000 trade_distCapital_3000 (first) continent region_cat cl_md pca_index, by(adm0)

	gen LFP_gap = LFP_female-LFP_male

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
	
		label var pca_index "PCA Index"
	
		*--- FIRST STAGE

 	eststo clear

	forvalue i=1/5{ 
	eststo: reghdfe pca_index c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe pca_index c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=7/10{ 
	eststo: reghdfe pca_index c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=12/15{ 
	eststo: reghdfe pca_index c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_fs_pca_dist.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		replace

	*-------------------------------------------*
**#	*                 FLFP                      *
	*-------------------------------------------*
	
	*--- OLS

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.pca_index ${c`i'}  , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_pca_OLS.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(pca_index) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

// 	*--- OLS
//
// 	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.median_totaltime ${c`i'}  , absorb(region_cat cl_md) vce(robust)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.median_ingredients ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
//
// 	 cd "$tables"
//	 
// 	estout using reg_flfp_OLS.tex, ///
// 		style(tex) ///
// 		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
// 		postfoot("\bottomrule" "\end{tabular}") ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		order(median_totaltime w_mean_spices median_ingredients) ///
// 		drop(_cons) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
//     replace


	*--- REDUCED FORM

 	eststo clear
// 		forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=7/10{ 
	eststo: reghdfe LFP_female c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=12/15{ 
	eststo: reghdfe LFP_female c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_dist.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		replace
		
		
	* IV REGRESSIONS FOR vers_distCapital_2000, vers_distCapital_3000

	eststo clear

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
	forvalue i=1/5 { 
		eststo: ivreg2 LFP_female (pca_index = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_2000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_female (pca_index = vers_distCapital_3000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_3000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	forvalue i=7/10 { 
		eststo: ivreg2 LFP_female (pca_index = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_2000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=12/15 { 
		eststo: ivreg2 LFP_female (pca_index = vers_distCapital_3000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_3000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_flfp_IV_pca_dist.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(pca_index) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFP" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

	*-------------------------------------------*
**#	*                 MLFP                      *
	*-------------------------------------------*
	
	*--- OLS

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.pca_index ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_pca_OLS.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(pca_index) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
    replace

	*--- OLS

// 	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_male c.median_totaltime ${c`i'}  , absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_male c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_male c.median_ingredients ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 	qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	 }
//
// 	 cd "$tables"
//	 
// 	estout using reg_mlfp_OLS.tex, ///
// 		style(tex) ///
// 		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
// 		postfoot("\bottomrule" "\end{tabular}") ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		order(median_totaltime w_mean_spices median_ingredients) ///
// 		drop(_cons) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
//     replace


	*--- REDUCED FORM

 	eststo clear
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_male c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 	 }
// 	forvalue i=1/5{ 
// 	eststo: reghdfe LFP_male c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
// 	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0, absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0, absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=7/10{ 
	eststo: reghdfe LFP_male c.vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0, absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }
	forvalue i=12/15{ 
	eststo: reghdfe LFP_male c.vers_distCapital_3000 ${c`i'} if vers_distCapital_3000 != 0, absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean LFP" "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		replace

	* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

	eststo clear
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//
// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
	forvalue i=1/5{ 
		eststo: ivreg2 LFP_male (pca_index = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_2000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=1/5{ 
		eststo: ivreg2 LFP_male (pca_index = vers_distCapital_3000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_3000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=7/10{ 
		eststo: ivreg2 LFP_male (pca_index = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_2000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	forvalue i=12/15{ 
		eststo: ivreg2 LFP_male (pca_index = vers_distCapital_3000) ${c`i'} i.region_cat i.cl_md if vers_distCapital_3000 != 0, robust first
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}

	cd "${tables}"

	* Export table including F-stat
	estout using reg_mlfp_pca_IV.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(pca_index) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, ///
			  labels("Mean LFP" "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace
