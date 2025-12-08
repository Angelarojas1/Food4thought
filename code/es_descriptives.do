
*****************************************************
*            Recipe database 					    *
*****************************************************
clear all 
eststo clear

	use "${recipes}/recipe_all_countries.dta", clear

	do "$code/subcode/recipe_cleaning.do"
		
	summarize numrecipe
	local N = r(N)

	quietly levelsof adm0, local(countries)
	local N_countries : word count `countries'

	estpost summarize z_pca_index TotalTime numberofingredients numberofspices , detail

	estadd scalar countries = `N_countries'
	estadd scalar observations = `N'
	
	label var z_pca_index "Cuisine Complexity Index"
	label var totaltime   "Cooking time"
	label var numberofingredients "Number of ingredients"
	label var numberofspices "Number of spices"
	
	esttab using "$tables/summary_table_recipe.tex", ///
    cells("mean(fmt(2)) sd(fmt(2)) p50(fmt(2)) min(fmt(2)) max(fmt(2))") ///
    stats(countries observations, ///
	fmt(%9.0f %9.0f) ///
    labels("Countries" "Observations")) ///
    collabels(,none) ///
    noobs nonumber nomtitle noline ///
    fragment lab ///
    replace
	
*****************************************************
*            Cookpad database 					    *
*****************************************************
clear all

	use "$cookpad/cookpad_adm0.dta", replace
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
		
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
	
	*--- Vars for stats
	eststo clear

	local vars fem lfpr fulltime fullemployee meals spousecook
	
	quietly levelsof adm0, local(countries)
	local N_countries : word count `countries'
		
foreach v of local vars {
    
    * Female
    estpost summarize `v' if fem == 1
    eststo F_`v'
    count if fem == 1
    estadd scalar N_obs = r(N)
    estadd scalar countries = `N_countries'
    
    * Male
    estpost summarize `v' if fem == 0
    eststo M_`v'
    count if fem == 0
    estadd scalar N_obs = r(N)
    estadd scalar countries = `N_countries'
    
    * Total
    estpost summarize `v'
    eststo T_`v'
    count
    estadd scalar N_obs = r(N)
    estadd scalar countries = `N_countries'
}

	
	label var fem "Female"
	label var lfpr "Labor Force Participation"
	label var fulltime "Employed full-time"
	label var fullemployee "Employed full-time for employer"
	label var meals "Number of meals cooked"
	label var spousecook "Spouse cooked"
		
	esttab T_fem F_fem M_fem ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) noline ///
    nonumber noobs nomtitle fragment ///
    label replace 
	
	esttab T_lfpr F_lfpr M_lfpr ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append

	esttab T_fulltime F_fulltime M_fulltime ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline  ///
    label append
	
	esttab T_fullemployee F_fullemployee M_fullemployee ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append
	
	esttab T_meals F_meals M_meals ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 
	
	esttab T_spousecook F_spousecook M_spousecook ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
	stats(countries N_obs, ///
	fmt(%9.0f %9.0f) ///
    labels("Countries" "Observations")) ///
    label append
