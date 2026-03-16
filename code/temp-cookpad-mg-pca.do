/**********************************************************************
Cuisine Complexity and Female Labor Force Participation
Author: Girija Borker, Margarita Gáfaro, Steve Berggreen

Created: Nov, 2025
Created by: Margarita Gáfaro

Last date modified: Dec 17, 2025
Modified by: Angela Rojas

Description:
This code runs cookpad regressions that are included in the draft 
created for NBER. Date: Dec 8, 2025

- PCA index 
***********************************************************************/

*--- Margarita Gafaro
// global gnr "C:\Users\mgafargo\Dropbox\food4thought\analysis23"
// global codedata "$gnr\data\coded\"
// global versatility "$codedata\iv_versatility\"
// global tables "$gnr\outputs\Tables"
// global cookpad  "$gnr\data\coded\cookpad"
	
	use "$cookpad/cookpad_adm0.dta", replace
	
	global hhcontr " i.income_5 hhsize i.wp1233recoded i.wp3117  " 
	
	global c6 "numrecipes numNative numNativeCIAT trade_distCapital_2000"
	global c7 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability trade_distCapital_2000"
	global c8 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability trade_distCapital_2000 GDP"
	global c9 "numrecipes numNative numNativeCIAT avg_suitability  staple_suitability trade_distCapital_2000 GDP  i.precip_bin temp   abslat lon  landlocked"
	global c10 "numrecipes numNative numNativeCIAT  avg_suitability staple_suitability coltime trade_distCapital_2000 GDP al_mn  i.precip_bin temp  ph_mn     abslat lon rough  landlocked distcr  "
		global c11 "numrecipes numNative numNativeCIAT  avg_suitability staple_suitability coltime   trade_distCapital_2000 GDP al_mn  i.precip_bin temp  ph_mn     abslat lon rough  landlocked distcr  $hhcontr"
	
	
	*--- Create standarized distance variables	
	reghdfe lfpr  w_mean_spices    $c1 if vers_distCapital_2000 != 0 & covid == 0 , absorb(region_cat cl_md ym) cluster(adm0)
	egen vers_distCapital_2000_std=std(vers_distCapital_2000 )	if e(sample)
	
	reghdfe lfpr  w_mean_spices    $c1 if vers_distCapital_3000 != 0 & covid == 0 , absorb(region_cat cl_md ym) cluster(adm0)
	egen vers_distCapital_3000_std=std(vers_distCapital_3000 )	if e(sample)
	
	reghdfe lfpr  w_mean_spices    $c1 if covid == 0 , absorb(region_cat cl_md ym) cluster(adm0)
	egen vers_distCapital_2000_std2=std(vers_distCapital_2000 )	if e(sample)

	label var vers_distCapital_2000_std  "Flavor versatility"
	label var vers_distCapital_2000_std2  "Flavor versatility"
	label var vers_distCapital_3000_std   "Flavor versatility"
	lab var suit_versatility "Flavor versatiltiy, all ingredients"
	lab var fem "Female"
	
// define samples 
global s1 "fem==1"
global s0 "fem==0"
global s2 "fem==1 & nonsingle==1"
global s3 "fem==0 & nonsingle==1"
global s4 "nonsingle==1" // Married or cohabitting
global s5 "nonsingle==0" // Single
 

	*------------------------------------------*
	**#   Standarized PCA Index                *
	*------------------------------------------*
	
	*keep if continent == "Europe"

	*-------- OLS --------*
// 
// 	 cd "$tables"
// 	forvalue j=0/3 {
//	
// 	eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe lfpr z_pca_recipe  ${c`i'} if  vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	 
// 	 estout using reg_index_ols_`j'_cook.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe ) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N, labels("Mean dep. var." "Observations") fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// }	
//
// 
//
// 	forvalue j=4/5 {
// eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe lfpr c.z_pca_recipe##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	
// 	eststo:  reghdfe lfpr i.fem c.z_pca_recipe#1.fem $hhcontr    if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
//		
// 	 estout using reg_index_ols_gap_`j'_cook.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe 1.fem 1.fem#c.z_pca_recipe) ///
// 		varlabels("c.z_pca_recipe#1.fem " "Female × Cuisine complexity" "1.fem" "Female=1") ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N F , labels("Mean dep. var." "Observations" "F-statistic" ) fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// }

 
 
	*-------- IV --------*
	
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo m`i':  ivreg2 lfpr (z_pca_recipe   = vers_distCapital_2000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
		qui sum lfpr if e(sample)
		local m = r(mean)
		estadd scalar Ffirst=e(rkf)
	estadd scalar Mean = `m': m`i'

	}
	 	 
	 estout using reg_index_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_recipe ) ///
		label ml(none) collabels(none) ///
		stats(Mean N Ffirst, labels("Mean dep. var." "Observations" "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	

// 	forvalue j=0/3 {
//	
// 	eststo clear
// 	forvalue i=6/11{
// 	eststo:  ivreg2 lfpr (z_pca_recipe   = vers_distCapital_3000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_3000 != 0 & covid == 0  & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	estadd scalar Ffirst=e(rkf)
//
// 	}
//	 	 
// 	 estout using reg_index_iv_`j'_cook_robust.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe  ) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2 Ffirst, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// }		

	*-------- First Stage --------*
	
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe z_pca_recipe  vers_distCapital_2000_std    ${c`i'}   if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'} & lfpr!=.,  absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_index_fs_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep( vers_distCapital_2000_std   ) ///
		label ml(none) collabels(none) ///
		stats(Mean N F, labels("Mean dep. var." "Observations" "F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		


// 	forvalue j=0/3 {
//	
// 	eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe  z_pca_recipe    vers_distCapital_3000_std  ${c`i'}   if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'} & lfpr!=.,  absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	 
// 	 estout using reg_index_fs_`j'_cook_robust.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep( vers_distCapital_3000_std ) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared"  ) fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// }		

	
	********************************************
	*				Other Outcomes             *
	********************************************

	*------------------------------------------*
	**#   Standarized PCA Index                *
	*------------------------------------------*

	*-------- OLS --------*
	 
// 	foreach var in fulltime fullemployee meals spousecook {
//	 
// 	forvalue j=0/3 {
// 	eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe `var' z_pca_recipe   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'} , absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	 
// 	 estout using r`var'_index_ols_`j'_cook.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe ) ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// }	
// 	}
//	 
	 
// 	foreach var in fulltime fullemployee {
// 	forvalue j=4/5 {
// eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe `var' c.z_pca_recipe##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	
// 	eststo:  reghdfe `var' i.fem c.z_pca_recipe#1.fem  $hhcontr   if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
//		
// 	 estout using r`var'_index_ols_gap_`j'_cook.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe  1.fem 1.fem#c.z_pca_recipe  ) ///
// 		varlabels("1.fem#c.z_pca_recipe " "Female × Cuisine complexity" "1.fem" "Female=1") ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N F, labels("Mean dep. var." "Observations" "F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// 	}
// }
	 
 	 
// foreach var in meals spousecook  {
// 	forvalue j=4/4 {
// eststo clear
// 	forvalue i=6/11{
// 	eststo:  reghdfe `var' c.z_pca_recipe##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
// 	}
//	 	
// 	eststo:  reghdfe `var' i.fem c.z_pca_recipe#1.fem  $hhcontr   if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
// 		qui sum `e(depvar)' if e(sample)
// 		estadd scalar Mean = r(mean)
//		
// 	 estout using r`var'_index_ols_gap_`j'_cook.tex, ///
// 		style(tex) ///
// 		cells(b(star f(3)) se(par f(3))) ///
// 		starlevels(* 0.10 ** 0.05 *** 0.01) ///
// 		keep(z_pca_recipe  1.fem 1.fem#c.z_pca_recipe ) ///
// 		varlabels("1.fem#c.z_pca_recipe" "Female × Cuisine complexity" "1.fem" "Female=1") ///
// 		label ml(none) collabels(none) ///
// 		stats(Mean N F, labels("Mean dep. var." "Observations" "F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
// 		postfoot("\hline") ///
//     replace
// 	}
// }

	*-------- IV --------*

	foreach var in fulltime fullemployee {
	forvalue j=1/2 {
	
	eststo clear
	forvalue i=6/11{
	eststo m`i':  ivreg2  `var'  (z_pca_recipe = vers_distCapital_2000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		local m = r(mean)
	estadd scalar Ffirst=e(rkf)
	estadd scalar Mean = `m': m`i'

	}
	 	 
	 estout using r`var'_index_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_recipe) ///
		label ml(none) collabels(none) ///
		stats(Mean N Ffirst, labels("Mean dep. var." "Observations" "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		


	foreach var in spousecook meals {
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo m`i':  ivreg2  `var'  (z_pca_recipe = vers_distCapital_2000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		local m = r(mean)
	estadd scalar Ffirst=e(rkf)
	estadd scalar Mean = `m': m`i'
	}
	 	 
	 estout using r`var'_index_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_recipe) ///
		label ml(none) collabels(none) ///
		stats(Mean N Ffirst, labels("Mean dep. var." "Observations" "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		

}

	}
*spousecook meals
