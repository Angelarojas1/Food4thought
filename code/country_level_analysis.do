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
**#	* 	 	Regressions - interactions	 	   *
	* Continent FE
	********************************************
	

	use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
	 
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability  al_mn"
	global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon "
	global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability"

	reghdfe LFP median_spices $c4, absorb(continent cl_md)
	cap drop s
	gen s=1 if  e(sample) 
	global s1 "if s==1" // indicator of countries with all information
	global s2 "if median_totaltime<90 &  s==1"  // Cleaned time
	global s3 "if  cookpad==1 &  s==1"  // Cookpad


	*-------- OLS --------*

	 cd "$tables"
	forvalue j=1/3 { 
	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_totaltime ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_spices ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.w_mean_spices ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_ingredients ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	estout using reg-ols-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.median_totaltime median_totaltime 1.fem_lfp#c.median_spices median_spices 1.fem_lfp#c.w_mean_spices w_mean_spices 1.fem_lfp#c.median_ingredients median_ingredients) drop(_cons 0.fem_lfp 0.fem_lfp#c.median_totaltime 0.fem_lfp#c.median_spices 0.fem_lfp#c.w_mean_spices 0.fem_lfp#c.median_ingredients) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace

	} 

	*-------- Reduced Form --------*

	forvalue j=1/3 { 
	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_versatility ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_versatility2 ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.suit_versatility ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	estout using reg-rf-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_versatility native_versatility 1.fem_lfp#c.native_versatility2 native_versatility2 1.fem_lfp#c.suit_versatility suit_versatility) drop(_cons 0.fem_lfp 0.fem_lfp#c.native_versatility 0.fem_lfp#c.native_versatility2 0.fem_lfp#c.suit_versatility) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace

	} 

	* Spices
	forvalue j=1/3 { 
	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers2 ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.suit_spice_vers ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
	 }
	estout using reg-rfsp-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_spice_vers native_spice_vers 1.fem_lfp#c.native_spice_vers2 native_spice_vers2 1.fem_lfp#c.suit_spice_vers suit_spice_vers) drop(_cons 0.fem_lfp 1.fem_lfp 0.fem_lfp#c.native_spice_vers 0.fem_lfp#c.native_spice_vers2 0.fem_lfp#c.suit_spice_vers) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace
	} 

	
	
	********************************************
**#	* 		Regressions - interactions	 	   *
	* Region FE
	********************************************
	

	use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
	 
	egen LFP_mean = mean(LFP), by(country)
	label var LFP_mean "LFP Mean"

	global c1 "numrecipes LFP_mean"
	global c2 "numrecipes avg_suitability  al_mn LFP_mean"
	global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP_mean"
	global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP_mean"
	reghdfe LFP median_spices $c4, absorb(region cl_md)
	cap drop s
	gen s=1 if  e(sample) 
	global s1 "if s==1" // indicator of countries with all information


	*-------- OLS --------*
	 cd "$tables"
	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_totaltime ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_spices ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.w_mean_spices ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.median_ingredients ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	estout using reg-ols-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.median_totaltime median_totaltime 1.fem_lfp#c.median_spices median_spices 1.fem_lfp#c.w_mean_spices w_mean_spices 1.fem_lfp#c.median_ingredients median_ingredients) drop(_cons 0.fem_lfp 0.fem_lfp#c.median_totaltime 0.fem_lfp#c.median_spices 0.fem_lfp#c.w_mean_spices 0.fem_lfp#c.median_ingredients) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace


	*-------- Reduced Form --------*

	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_versatility ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_versatility2 ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.suit_versatility ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	estout using reg-rf-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_versatility native_versatility 1.fem_lfp#c.native_versatility2 native_versatility2 1.fem_lfp#c.suit_versatility suit_versatility) drop(_cons 0.fem_lfp 0.fem_lfp#c.native_versatility 0.fem_lfp#c.native_versatility2 0.fem_lfp#c.suit_versatility) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace


	* Spices
	eststo clear
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers ${c`i'}  ${s1}, absorb(region cl_md) vce(robust)
	 }
	forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers2 ${c`i'} ${s1}, absorb(region cl_md) vce(robust)
	 }
	 forvalue i=1/4{ 
	eststo: reghdfe LFP i.fem_lfp##c.suit_spice_vers ${c`i'} ${s1}, absorb(region cl_md) vce(robust)
	 }
	estout using reg-rfsp-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_spice_vers native_spice_vers 1.fem_lfp#c.native_spice_vers2 native_spice_vers2 1.fem_lfp#c.suit_spice_vers suit_spice_vers) drop(_cons 0.fem_lfp 1.fem_lfp 0.fem_lfp#c.native_spice_vers 0.fem_lfp#c.native_spice_vers2 0.fem_lfp#c.suit_spice_vers) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace 


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
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability  al_mn"
	global c3 "numrecipes avg_suitability  al_mn GDP"
	global c4 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	encode region, gen(region_cat)

	gen LFP_female = LFP if fem_lfp == 1
	gen LFP_male   = LFP if fem_lfp == 0

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

	*-------------------------------------------*
**#	*                 FLFP                      *
	*-------------------------------------------*

	*--- OLS

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_OLS.tex, ///
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
	eststo: reghdfe LFP_female c.vers_distCapital_2000 ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_female c.vers_distCapital_3000 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
// 	 forvalue i=1/5{ 
// 	eststo: reghdfe LFP_female c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
// 	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_dist.tex, ///
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
		
		
	* IV REGRESSIONS FOR vers_distCapital_2000, vers_distCapital_3000

	eststo clear

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_female (w_mean_spices = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md, robust first
	}

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_female (w_mean_spices = vers_distCapital_2000) ${c`i'} i.region_cat i.cl_md, robust first
	}

// 	forvalue i=1/5 { 
// 		eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
// 	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_flfp_IV_dist.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

		

	*--------- Control for MLFP instead of GDP -----------------*
	

	global c5 "numrecipes LFP_male"
	global c6 "numrecipes avg_suitability  al_mn LFP_male"
	global c7 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP_male"
	global c8 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP_male"

	*--- OLS

	eststo clear
	forvalue i=5/8{ 
	eststo: reghdfe LFP_female c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=5/8{ 
	eststo: reghdfe LFP_female c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_OLS_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
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
	forvalue i=5/8{ 
	eststo: reghdfe LFP_female c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=5/8{ 
	eststo: reghdfe LFP_female c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=5/8{ 
	eststo: reghdfe LFP_female c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_flfp_RF_c.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
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
	forvalues i=5/8 { 
		ivreg2 LFP_female (w_mean_spices = native_spice_vers ) ${c`i'} i.region_cat i.cl_md, robust
		local fstat = e(widstat)  
		estadd scalar F_first = `fstat'   
		eststo
	}

	forvalues i=5/8 { 
		ivreg2 LFP_female (w_mean_spices = native_spice_vers2 ) ${c`i'} i.region_cat i.cl_md, robust
		local fstat = e(widstat)
		estadd scalar F_first = `fstat'
		eststo
	}

	forvalues i=5/8 { 
		ivreg2 LFP_female (w_mean_spices = native_spice_vers2_dist ) ${c`i'} i.region_cat i.cl_md, robust
		local fstat = e(widstat)
		estadd scalar F_first = `fstat'
		eststo
	}

	 cd "${tables}"
	 
	estout using reg_flfp_IV_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(F_first j N r2, labels("F-stat First Stage" " " "Observations" "R-squared") fmt(%9.2f %9.1gc %9.1gc %4.3f)) ///
		replace

	*-------------------------------------------*
**#	*                 MLFP                      *
	*-------------------------------------------*

	*--- OLS

	eststo clear
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_OLS.tex, ///
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
	eststo: reghdfe LFP_male c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=1/5{ 
	eststo: reghdfe LFP_male c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF.tex, ///
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

	* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

	eststo clear

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
	}

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
	}

	forvalue i=1/5 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
	}

	cd "${tables}"

	* Export table including F-stat
	estout using reg_mlfp_IV.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lccccccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace

		
	*--------- Control for FLFP instead of LFP -----------------*

	global c9 "numrecipes LFP_female"
	global c10 "numrecipes avg_suitability  al_mn LFP_female"
	global c11 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP_female"
	global c12 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP_female"

	*--- OLS

	eststo clear
	forvalue i=9/12{ 
	eststo: reghdfe LFP_male c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=9/12{ 
	eststo: reghdfe LFP_male c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_OLS_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
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
	forvalue i=9/12{ 
	eststo: reghdfe LFP_male c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }
	forvalue i=9/12{ 
	eststo: reghdfe LFP_male c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
	 }
	 forvalue i=9/12{ 
	eststo: reghdfe LFP_male c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
	 }

	 cd "$tables"
	 
	estout using reg_mlfp_RF_c.tex, ///
		style(tex)  ///
		prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
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

	forvalue i=9/12 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
	}

	forvalue i=9/12 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
	}

	forvalue i=9/12 { 
		eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
	}

	cd "${tables}"

	* Export table with F-stat
	estout using reg_mlfp_IV_c.tex, ///
		style(tex) ///
		prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
		postfoot("\bottomrule" "\end{tabular}") ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		order(w_mean_spices) ///
		drop(_cons *.region_cat *.cl_md) ///
		label ml(none) collabels(none) ///
		stats(j N r2 widstat, ///
			  labels(" " "Observations" "R-squared" "First-stage F-stat") ///
			  fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
		replace