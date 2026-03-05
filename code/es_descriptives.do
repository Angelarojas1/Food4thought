
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

	estpost summarize z_pca_index totaltime_orig numberofingredients numberofspices , detail

	estadd scalar countries = `N_countries'
	estadd scalar observations = `N'
	
	label var z_pca_index "Cuisine Complexity Index"
	label var totaltime_orig  "Cooking time"
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
	
	*--- Vars for stats
	keep if vers_distCapital_2000 != 0 & covid == 0
	
	* Income
// 	tab income_5, gen(inc_)
//	
// 	local vl : value label income_5
// 	levelsof income_5, local(levels)
//
// 	foreach l of local levels {
// 		local lab : label `vl' `l'
// 		label variable inc_`l' "\hspace{0.5cm} `lab'"
// 	}
	
	* Religion
	tab wp1233recoded, gen(rel_)
	
	local vl : value label wp1233recoded

	levelsof wp1233recoded, local(levels)

	foreach l of local levels {
		local lab : label `vl' `l'
		label variable rel_`l' "\hspace{0.5cm} `lab'"
	}

	* Education
	tab wp3117, gen(edu_)
	
	local vl : value label wp3117

	levelsof wp3117, local(levels)

	foreach l of local levels {
		local lab : label `vl' `l'
		label variable edu_`l' "\hspace{0.5cm} `lab'"
	}
	
	eststo clear
	
	gen rel_other = rel_3
	replace rel_other = rel_4 if rel_5 == 1
	replace rel_other = rel_5 if rel_5 == 1
	replace rel_other = rel_6 if rel_6 == 1
	replace rel_other = rel_7 if rel_7 == 1
	replace rel_other = rel_8 if rel_8 == 1
	
	gen edu_other = edu_4
	replace edu_other = edu_5 if edu_5 == 1
	
	local vars fem age lfpr fulltime fullemployee meals spousecook ///
	hhsize rel_1 rel_2 rel_other edu_1 edu_2 ///
	edu_3 edu_other
	
	*inc_1 inc_2 inc_3 inc_4 inc_5 
	
	quietly levelsof adm0, local(countries)
	local N_countries : word count `countries'
		
foreach v of local vars {
    
    * Female
    quietly count if fem == 1
    local Nf = r(N)

    estpost summarize `v' if fem == 1
    estadd scalar N_obs = `Nf'
    estadd scalar countries = `N_countries'
    eststo F_`v'
    
    * Male
    quietly count if fem == 0
    local Nm = r(N)

    estpost summarize `v' if fem == 0
    estadd scalar N_obs = `Nm'
    estadd scalar countries = `N_countries'
    eststo M_`v'
    
    * Total
    quietly count
    local Nt = r(N)

    estpost summarize `v'
    estadd scalar N_obs = `Nt'
    estadd scalar countries = `N_countries'
    eststo T_`v'
}
	
	label var fem "Female"
	label var lfpr "Labor Force Participation"
	label var fulltime "Employed full-time"
	label var fullemployee "Employed full-time for employer"
	label var meals "Number of meals cooked"
	label var spousecook "Spouse cooked"
	label var age "Age"
	label var hhsize "Household size"
// 	label var inc_1 "\hspace{0.5cm} Poorest 20\%"
// 	label var inc_2 "\hspace{0.5cm} Second 20\%"
// 	label var inc_3 "\hspace{0.5cm} Middle 20\%"
// 	label var inc_4 "\hspace{0.5cm} Fourth 20\%"
// 	label var inc_5 "\hspace{0.5cm} Richest 20\%"
	label var rel_other "\hspace{0.5cm} Other"
	label var edu_1 "\hspace{0.5cm} Elementary education"
	label var edu_2 "\hspace{0.5cm} Secondary education"
	label var edu_3 "\hspace{0.5cm} 4 years education beyond high school"
	label var edu_other "\hspace{0.5cm} Other"

	esttab T_fem F_fem M_fem ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) noline ///
    nonumber noobs nomtitle fragment ///
    label replace 
	
	esttab T_age F_age M_age ///
	using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 
	
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
    label append 
	
// 	esttab T_inc_1 F_inc_1 M_inc_1 ///
// using "$tables/descriptive_gender.tex", ///
//     cells("mean(fmt(2)) sd(fmt(2))") ///
//     collabels(, none ) ///
//     nonumber noobs nomtitle fragment noline ///
// 	refcat(inc_1 "\textit{Income}", nolabel) ///
//     label append 
//	
// 	esttab T_inc_2 F_inc_2 M_inc_2 ///
// 	using "$tables/descriptive_gender.tex", ///
//     cells("mean(fmt(2)) sd(fmt(2))") ///
//     collabels(, none ) ///
//     nonumber noobs nomtitle fragment noline ///
//     label append 
//	
// 	esttab T_inc_3 F_inc_3 M_inc_3 ///
// using "$tables/descriptive_gender.tex", ///
//     cells("mean(fmt(2)) sd(fmt(2))") ///
//     collabels(, none ) ///
//     nonumber noobs nomtitle fragment noline ///
//     label append 
//
// esttab T_inc_4 F_inc_4 M_inc_4 ///
// using "$tables/descriptive_gender.tex", ///
//     cells("mean(fmt(2)) sd(fmt(2))") ///
//     collabels(, none ) ///
//     nonumber noobs nomtitle fragment noline ///
//     label append 
//
// esttab T_inc_5 F_inc_5 M_inc_5 ///
// using "$tables/descriptive_gender.tex", ///
//     cells("mean(fmt(2)) sd(fmt(2))") ///
//     collabels(, none ) ///
//     nonumber noobs nomtitle fragment noline ///
//     label append 
	
	esttab T_hhsize F_hhsize M_hhsize ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 
	
	esttab T_rel_1 F_rel_1 M_rel_1 ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
	refcat(rel_1 "\textit{Religion}", nolabel) ///
    label append 

esttab T_rel_2 F_rel_2 M_rel_2 ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 

esttab T_rel_other F_rel_other M_rel_other ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 
	
	esttab T_edu_1 F_edu_1 M_edu_1 ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
	refcat(edu_1 "\textit{Education}", nolabel) ///
    label append 

esttab T_edu_2 F_edu_2 M_edu_2 ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 

esttab T_edu_3 F_edu_3 M_edu_3 ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 

esttab T_edu_other F_edu_other M_edu_other ///
using "$tables/descriptive_gender.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    stats(countries N_obs, ///
        fmt(%9.0f %9.0f) ///
        labels("Countries" "Observations")) ///
    label append
	
	
/*
*****************************************************
*            Cookpad database robust			    *
*****************************************************
clear all

	use "$cookpad/cookpad_adm0.dta", replace
	
	keep if age >= 24 & age <= 55
	
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
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) noline ///
    nonumber noobs nomtitle fragment ///
    label replace 
	
	esttab T_lfpr F_lfpr M_lfpr ///
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append

	esttab T_fulltime F_fulltime M_fulltime ///
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline  ///
    label append
	
	esttab T_fullemployee F_fullemployee M_fullemployee ///
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append
	
	esttab T_meals F_meals M_meals ///
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
    label append 
	
	esttab T_spousecook F_spousecook M_spousecook ///
	using "$tables/descriptive_gender_24_55.tex", ///
    cells("mean(fmt(2)) sd(fmt(2))") ///
    collabels(, none ) ///
    nonumber noobs nomtitle fragment noline ///
	stats(countries N_obs, ///
	fmt(%9.0f %9.0f) ///
    labels("Countries" "Observations")) ///
    label append

