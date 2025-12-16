	
global gnr "C:\Users\mgafargo\Dropbox\food4thought\analysis23"
global codedata "$gnr\data\coded\"
global versatility "$codedata\iv_versatility\"
global tables "$gnr\outputs\Tables"
global cookpad  "$gnr\data\coded\cookpad"
	
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
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA con las variables estandarizadas
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
	
		sum  pca_index 
		gen z_pca_index  = ( pca_index  - r(mean)) / r(sd)
	
	label var pca_index "PCA Index"
	
	label var z_pca_index "Cuisine complexity"
 
	label var w_mean_spices  "Average spices"
	
	
	encode region, gen(region_cat)
	
	egen precip_bin = cut(precip), at(0(50)250)
	
	egen meals=rowtotal(numDinCook numLunCook)
	
	gen partjob=cond(hours==1 | hours==2,1,0) if hours!=0. & hours!=98
	
	gen spousecook=cond(wp19962==1 | wp19970==1,1,cond(wp19962==2 | wp19970==2,0,.)) 
	
	gen nonsingle=cond(wp1223==2|wp1223==8,1,0) if (wp1223!=6 & wp1223!=7 & wp1223!=.)  
	
	// other employment outcomes 
	// fulltime work condition on lfp 
	gen fullemployee=cond(emp_2010==1,1,0) if emp_2010!=. & emp_2010!=6 
	gen fulltime=cond(emp_2010<=2,1,0) if emp_2010!=. & emp_2010!=6 
	
	// share lunches and 
	gen pmeals=(numLunCook+numDinCook)/(numLunEat+numDinEat)
	replace pmeals=1 if pmeals>1 & pmeals!=.
	
	egen cont_cat=group(continent)
	gen lmedian_time=log(median_totaltime)
	gen lmean_time=log(w_mean_totaltime)
	lab var lmean_time "Log. average cooking time"
	lab var staple_suitability  "Mean Staple Suitability"
	
	global hhcontr " i.income_5 hhsize i.wp1233recoded i.wp3117  " 
	
	global c6 "numrecipes numNative numNativeCIAT trade_distCapital_2000"
	global c7 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability trade_distCapital_2000"
	global c8 "numrecipes numNative numNativeCIAT avg_suitability staple_suitability  trade_distCapital_2000 GDP"
	global c9 "numrecipes numNative numNativeCIAT avg_suitability  staple_suitability  trade_distCapital_2000 GDP  i.precip_bin temp   abslat lon  landlocked"
	global c10 "numrecipes numNative numNativeCIAT  avg_suitability staple_suitability   trade_distCapital_2000 GDP al_mn  i.precip_bin temp  ph_mn     abslat lon rough  landlocked distcr  "
		global c11 "numrecipes numNative numNativeCIAT  avg_suitability staple_suitability   trade_distCapital_2000 GDP al_mn  i.precip_bin temp  ph_mn     abslat lon rough  landlocked distcr  $hhcontr"
	
	
	
	
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
global s4 "nonsingle==1"
global s5 "nonsingle==0"
 
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	 
	
	*-------- FLFP --------*
 
	 cd "$tables"
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe lfpr z_pca_index    ${c`i'} if  vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_index_ols_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	

 
  
forvalue j=4/5 {
eststo clear
	forvalue i=6/11{
	eststo:  reghdfe lfpr c.z_pca_index##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	
	eststo:  reghdfe lfpr i.fem c.z_pca_index#1.fem $hhcontr    if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		
	 estout using reg_index_ols_gap_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index 1.fem 1.fem#c.z_pca_index) ///
		varlabels("c.z_pca_index#1.fem " "Female × Cuisine complexity" "1.fem" "Female=1") ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}
 
 
 
	*------------------------------------------*
	**#  		       IV           *
	*------------------------------------------*

	
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  ivreg2 lfpr (z_pca_index   = vers_distCapital_2000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
			qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	estadd scalar Ffirst=e(rkf)

	}
	 	 
	 estout using reg_index_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 Ffirst, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		


	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  ivreg2 lfpr (z_pca_index   = vers_distCapital_3000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_3000 != 0 & covid == 0  & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	estadd scalar Ffirst=e(rkf)

	}
	 	 
	 estout using reg_index_iv_`j'_cook_robust.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index  ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 Ffirst, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		


 


 	*------------------------------------------*
	**#  		       first stage            *
	*------------------------------------------*

	
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe  z_pca_index    vers_distCapital_2000_std  ${c`i'}   if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'} & lfpr!=.,  absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_index_fs_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep( vers_distCapital_2000_std ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared"  ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		



	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe  z_pca_index    vers_distCapital_3000_std  ${c`i'}   if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'} & lfpr!=.,  absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_index_fs_`j'_cook_robust.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep( vers_distCapital_3000_std ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared"  ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		





	

/////////////////////////
///// other outcomes/////
/////////////////////////

	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	 
 
	 
	foreach var in partjob  fulltime fullemployee meals spousecook pmeals  {
	 
	forvalue j=0/3 {
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe `var' z_pca_index   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'} , absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using r`var'_index_ols_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	
	}
	 
	 
foreach var in partjob  fulltime fullemployee meals pmeals  {
	forvalue j=4/5 {
eststo clear
	forvalue i=6/11{
	eststo:  reghdfe `var' c.z_pca_index##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	
	eststo:  reghdfe `var' i.fem c.z_pca_index#1.fem  $hhcontr   if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		
	 estout using r`var'_index_ols_gap_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index  1.fem 1.fem#c.z_pca_index  ) ///
		varlabels("1.fem#c.z_pca_index " "Female × Cuisine complexity" "1.fem" "Female=1") ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
	}
}
	 
 	 
foreach var in spousecook  {
	forvalue j=4/4 {
eststo clear
	forvalue i=6/11{
	eststo:  reghdfe `var' c.z_pca_index##i.fem   ${c`i'} if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	
	eststo:  reghdfe `var' i.fem c.z_pca_index#1.fem  $hhcontr   if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(adm0 ) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
		
	 estout using r`var'_index_ols_gap_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index  1.fem 1.fem#c.z_pca_index ) ///
		varlabels("1.fem#c.z_pca_index" "Female × Cuisine complexity" "1.fem" "Female=1") ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
	}
}



 
	*------------------------------------------*
	**#  		       IV           *
	*------------------------------------------*

	foreach var in partjob  fulltime fullemployee spousecook meals pmeals   {
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  ivreg2  `var'  (z_pca_index   = vers_distCapital_2000_std) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
	estadd scalar Ffirst=e(rkf)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using r`var'_index_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(z_pca_index ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 Ffirst, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		

}


*spousecook meals


//////////////////////////////
////// total time ///////////
/////////////////////////////



	*-------- FLFP --------*
 
	 cd "$tables"
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe lfpr lmean_time   ${c`i'} if  vers_distCapital_2000 != 0 & covid == 0 & ${s`j'}, absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_time_ols_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(lmean_time ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2, labels("Mean dep. var." "Observations" "R-squared") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}	

 
 
	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  ivreg2 lfpr (lmean_time  = vers_distCapital_2000_std ) ${c`i'} i.region_cat i.cl_md i.ym if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'}, partial(i.region_cat i.cl_md i.ym) cluster(adm0)
	estadd scalar Ffirst=e(rkf)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_time_iv_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(lmean_time ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 Ffirst, labels("Mean dep. var." "Observations" "R-squared"  "First stage F-statistic") fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		


	forvalue j=0/3 {
	
	eststo clear
	forvalue i=6/11{
	eststo:  reghdfe lmean_time   vers_distCapital_2000_std  ${c`i'}   if vers_distCapital_2000 != 0 & covid == 0  & ${s`j'} & lfpr!=.,  absorb(region_cat cl_md ym) cluster(adm0)
		qui sum `e(depvar)' if e(sample)
		estadd scalar Mean = r(mean)
	}
	 	 
	 estout using reg_time_fs_`j'_cook.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep( vers_distCapital_2000_std) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared"  ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
}		

 