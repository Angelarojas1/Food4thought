/// country level 

   ** EDITTED BY:       
   ** Last date modified: 
   

	********************************************
**#	* 		Regressions - interactions	 	   *
	* Region FE
	********************************************
		
global gnr "C:\Users\mgafargo\Dropbox\food4thought\analysis23"
global codedata "$gnr\data\coded\"
global versatility "$codedata\iv_versatility\"
global tables "$gnr\outputs\Tables"


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
		


	
	encode region, gen(region_cat)

	gen LFP_female = LFP if fem_lfp == 1
	gen LFP_male   = LFP if fem_lfp == 0
	
* creating the LFP gap at the country-level
	collapse (mean) LFP_male LFP_female median_spices w_mean_spices vers_distCapital_2000 vers_distCapital_3000 trade_distCapital_2000 trade_distCapital_3000 avg_suitability staple_suitability numNative numNativeCIAT al_mn precip ph_mn   temp abslat lon rough  landlocked distcr  numrecipes  GDP (first) continent region_cat cl_md pca_index, by(adm0)

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
		label var vers_distCapital_2000 "Flavor versatility"
	
	
	
	egen precip_bin = cut(precip), at(0(50)250)
	
	

	/// women only estimations 
	
 // --> missing in GDP for two countries 
	reghdfe LFP_female vers_distCapital_2000 $c1 if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	
	egen vers_distCapital_2000_std=std(vers_distCapital_2000 )	if e(sample)
	
	reghdfe LFP_female vers_distCapital_2000 $c1   , absorb(region_cat cl_md) vce(robust)
	
	egen vers_distCapital_2000_std2=std(vers_distCapital_2000 )	if e(sample)
	
	label var vers_distCapital_2000_std  "Flavor versatility"
	label var vers_distCapital_2000_std2  "Flavor versatility"
	
	label var w_mean_spices  "Average spices"
	
		
	global c6 "numrecipes numNative numNativeCIAT trade_distCapital_2000"
	global c7 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability trade_distCapital_2000"
	global c8 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability  trade_distCapital_2000 GDP"
	global c9 "numrecipes numNative numNativeCIAT avg_suitability  staple_suitability  trade_distCapital_2000 GDP  i.precip_bin temp   abslat lon  landlocked"
	global c10 "numrecipes numNative numNativeCIAT  avg_suitability staple_suitability   trade_distCapital_2000 GDP al_mn  i.precip_bin temp  ph_mn     abslat lon rough  landlocked distcr  "
	

/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// OLS table Panel A. female, Panel B. male, Panel C gap  
/////////////////////////////////////////////////////////////////////////////////////////////	
	
cd "$tables"

// PANEL A-C 

foreach j in female male gap {
	
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_`j' w_mean_spices   ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_ols_`j'.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	
	 
/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// Reduced form   Panel A. reduced form FLFP, Panel B gap,  and Panel C.  first stage 
/////////////////////////////////////////////////////////////////////////////////////////////

cd "$tables"
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_female vers_distCapital_2000_std ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_fem_country.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_male vers_distCapital_2000_std ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_male_country.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

	
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_gap vers_distCapital_2000_std ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_gap_country.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
	
	
	
	
// first stage 
eststo clear
	forvalue i=6/10{
	eststo:  reghdfe  w_mean_spices  vers_distCapital_2000_std ${c`i'}   if vers_distCapital_2000 != 0 & LFP_female!=., absorb(region_cat cl_md) vce(robust)
			qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	 estout using reg_fs_country.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
   postfoot("\hline") replace

 
 
 
/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// IV  Panel A.  FLFP, Panel B gap 
/////////////////////////////////////////////////////////////////////////////////////////////
 
 
foreach j in female male gap {
	
	eststo clear
	forvalue i=6/10{
	eststo: ivreg2 LFP_`j' (w_mean_spices  = vers_distCapital_2000_std) i.region_cat i.cl_md ${c`i'} if vers_distCapital_2000 != 0, robust partial( i.region_cat i.cl_md)  
	
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_iv_`j'.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	
	
	
 ///////////////////////////////////
 /// including IV with 0 
 //////////////////////////////////
 
 
 
/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// OLS table Panel A. female, Panel B. male, Panel C gap  
/////////////////////////////////////////////////////////////////////////////////////////////	
	
cd "$tables"

// PANEL A-C 

foreach j in female male gap {
	
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_`j' w_mean_spices   ${c`i'} , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_ols_`j'_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	
	 
/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// Reduced form   Panel A. reduced form FLFP, Panel B gap,  and Panel C.  first stage 
/////////////////////////////////////////////////////////////////////////////////////////////

cd "$tables"
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_female vers_distCapital_2000_std2 ${c`i'}  , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_fem_country_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std2) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_male vers_distCapital_2000_std2 ${c`i'} , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_male_country_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std2) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

	
	eststo clear
	forvalue i=6/10{
	eststo:  reghdfe LFP_gap vers_distCapital_2000_std2 ${c`i'} , absorb(region_cat cl_md) vce(robust)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_rf_gap_country_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std2) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
	
	
	
	
// first stage 
eststo clear
	forvalue i=6/10{
	eststo:  reghdfe  w_mean_spices  vers_distCapital_2000_std2 ${c`i'}   if LFP_female!=., absorb(region_cat cl_md) vce(robust)
			qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	
	 estout using reg_fs_country_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(vers_distCapital_2000_std2) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
   postfoot("\hline") replace

 
 
 
/////////////////////////////////////////////////////////////////////////////////////////////
/// TABLE	
/// IV  Panel A.  FLFP, Panel B gap 
/////////////////////////////////////////////////////////////////////////////////////////////
 
 
foreach j in female male gap {
	
	eststo clear
	forvalue i=6/10{
	eststo: ivreg2 LFP_`j' (w_mean_spices  = vers_distCapital_2000_std2) i.region_cat i.cl_md ${c`i'} , robust partial( i.region_cat i.cl_md)  
	
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_iv_`j'_ws.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(w_mean_spices) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 widstat, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	
	
	
	
	
	
	
	
	
 
 
 
 
 ///////////////// END 
 
	
	//OLS 
	forvalue i=6/10{
		di "******** `i' **************"
	reghdfe LFP_female w_mean_spices numNative numNativeCIAT ${c`i'}  if vers_distCapital_3000 != 0, absorb(region_cat cl_md) vce(robust)
	}
	
	// reduced form 
	forvalue i=6/10{
	eststo: reghdfe LFP_female vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	}
	
	// first stage 
	forvalue i=6/10{
	 reghdfe  w_mean_spices  vers_distCapital_2000 ${c`i'}   if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	}
	
		// native IV (native_spice_vers OK - native_versatility  (specifc 8) )
		
	forvalue i=6/10{
	 reghdfe  w_mean_spices native_versatility   ${c`i'}   if vers_distCapital_2000 != 0 &  LFP_female!=., absorb(region_cat cl_md) vce(robust)
	}	
		
	
	// IV
	forvalue i=6/10{
		di "************ `i' ****************"
	ivreg2 LFP_female (w_mean_spices  = vers_distCapital_2000) i.region_cat i.cl_md ${c`i'} if vers_distCapital_3000 != 0, robust partial( i.region_cat i.cl_md)
	}
	
	
forvalue i=6/10{
		di "************ `i' ****************"
	ivreg2 LFP_female (w_mean_spices  = native_versatility vers_distCapital_2000) i.region_cat i.cl_md ${c`i'} if vers_distCapital_2000 != 0   , robust partial( i.region_cat i.cl_md) first
	}
	
	

	
	
	
	
	
	
	
// interaction -- Not working
	// OLS
	forvalue i=6/10{
		di "******** `i' **************"
	reghdfe LFP fem_w_mean_spices w_mean_spices fem_lfp  ${c`i'}   if vers_distCapital_2000 != 0, absorb(region_cat cl_md) vce(robust)
	}
	
	forvalue i=15/15{
		di "******** `i' **************"
	reghdfe LFP fem_w_mean_spices w_mean_spices fem_lfp   ${c`i'}   if vers_distCapital_2000 != 0, absorb(adm0) vce(robust)
	}
	
	// reduced form 
	forvalue i=15/15{
	 reghdfe LFP fem_vers_distCapital_2000 vers_distCapital_2000 fem_lfp  ${c`i'} if vers_distCapital_3000 != 0 , absorb(region_cat cl_md) vce(robust)
	}
	
forvalue i=15/15{
	 reghdfe LFP  fem_vers_distCapital_2000 vers_distCapital_2000 fem_lfp  ${c`i'} if vers_distCapital_2000 != 0 , absorb(adm0) vce(robust)
	}
	
 
	
	// IV
	forvalue i=15/15{
	ivreg2 LFP  ( fem_w_mean_spices w_mean_spices  = fem_vers_distCapital_2000  vers_distCapital_2000) i.fem_lfp i.region_cat i.cl_md ${c`i'} if vers_distCapital_2000 != 0, robust partial( i.region_cat i.cl_md)
	}	
	
		forvalue i=15/15{
	ivreg2 LFP  ( fem_w_mean_spices w_mean_spices  = fem_vers_distCapital_2000  vers_distCapital_2000) i.fem_lfp i.Country ${c`i'} if vers_distCapital_2000 != 0, robust partial(i.Country)
	}	
	
	
// men only estimations 
	
forvalue i=11/15{
		di "******** `i' **************"
	reghdfe LFP_male w_mean_spices  ${c`i'}   if vers_distCapital_2000 != 0, absorb(region_cat cl_md) vce(robust)
	}
	
	// reduced form 
	forvalue i=11/15{
	 reghdfe LFP_male vers_distCapital_2000 ${c`i'} if vers_distCapital_2000 != 0 , absorb(region_cat cl_md) vce(robust)
	}
	
 
	
	// IV
	forvalue i=11/15{
	ivreg2 LFP_male (w_mean_spices  = vers_distCapital_2000) i.region_cat i.cl_md ${c`i'} if vers_distCapital_2000 != 0, robust partial( i.region_cat i.cl_md)
	} 	
	
