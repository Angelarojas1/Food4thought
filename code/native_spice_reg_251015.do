   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile runs reduced form estimation	        	  *
   *																	  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Steve Berggreen
   ** Created: 			20251015
   ** EDITTED BY:       
   ** Last date modified:

**# Regresions in 20251027 file. 

	use "$versatility/first_stage_native_m_c.dta", clear

	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability  al_mn"
	global c3 "numrecipes avg_suitability  al_mn GDP"
	global c4 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	* creating the LFP gap at the country-level
	collapse (mean) $c5 LFP_male LFP_female median_spices w_mean_spices native_spice_vers native_spice_vers2 suit_spice_vers (first) continent region_cat cl_md , by(adm0)

	gen LFP_gap = LFP_female-LFP_male

	preserve 
	use "${versatility}\native_versatility_m_c_dist.dta", clear
	collapse (mean) native_spice_vers2_dist, by(adm0)
	tempfile distance
	save `distance'
	restore

	merge 1:1 adm0 using `distance', keep(3) nogen

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

	*--- OLS

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_gap_OLS.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices median_spices) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace


	*--- REDUCED FORM

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF.tex, ///
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


	*--- FIRST STAGE - mean spices

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices  native_spice_vers  ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices  native_spice_vers2  ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices  native_spice_vers2_dist  ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_gap_first_mean_spice.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace

	*-- FIRST STAGE - median spices --*

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe median_spices  native_spice_vers  ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe median_spices  native_spice_vers2  ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe median_spices  native_spice_vers2_dist  ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }

	 cd "${tables}"
	 
	estout using reg_gap_first_median_spice.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace

		
	* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

	eststo clear
	forvalue i=1/5{ 
	eststo: ivreg2 LFP_gap (w_mean_spices = native_spice_vers ) ${c`i'}  i.region_cat i.cl_md, robust
	 }
	forvalue i=1/5{ 
	eststo: ivreg2 LFP_gap (w_mean_spices = native_spice_vers2 ) ${c`i'}  i.region_cat i.cl_md, robust
	 }
	 forvalue i=1/5{ 
	eststo: ivreg2 LFP_gap (w_mean_spices = native_spice_vers2_dist ) ${c`i'}  i.region_cat i.cl_md, robust
	 }

	 cd "${tables}"
	 
	estout using reg_gap_IV.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace
		

*******************************************************************************
**# Regresions including new versatility measure


		
	use "$versatility/first_stage_native_m_c.dta", clear
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability  al_mn"
	global c3 "numrecipes avg_suitability  al_mn GDP"
	global c4 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"


	* creating the LFP gap at the country-level
	collapse (mean) $c5 LFP_male LFP_female median_spices w_mean_spices vers_distCapital_2000 vers_distCapital_3000 (first) continent region_cat cl_md, by(adm0)

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


	*--- REDUCED FORM

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.vers_distCapital_2000 ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_gap c.vers_distCapital_3000 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_gap_RF_dist.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace


	*--- FIRST STAGE - mean spices

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices  vers_distCapital_2000  ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe w_mean_spices  vers_distCapital_3000  ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_gap_first_mean_spice_dist.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace

	*-- FIRST STAGE - median spices --*

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe median_spices vers_distCapital_2000  ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe median_spices  vers_distCapital_3000  ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }

	 cd "${tables}"
	 
	estout using reg_gap_first_median_spice_dist.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(vers_distCapital_2000 vers_distCapital_3000) ///
		drop(_cons) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace

		
	* IV REGRESSIONS FOR vers_distCapital_2000, vers_distCapital_3000

	eststo clear
	forvalue i=1/5{ 
	eststo: ivreg2 LFP_gap (w_mean_spices = vers_distCapital_2000) ${c`i'}  i.region_cat i.cl_md, robust
	 }
	forvalue i=1/5{ 
	eststo: ivreg2 LFP_gap (w_mean_spices = vers_distCapital_3000 ) ${c`i'}  i.region_cat i.cl_md, robust
	 }


	 cd "${tables}"
	 
	estout using reg_gap_IV_dist.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
		replace

