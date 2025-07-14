* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Cookpad Data Exploration
* **************************************************************************** *
	
	
	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	*======================================================
	*				Cookpad Analysis
	*------------------------------------------------------
	
	
	use "$cookpad/cookpad_adm0.dta", replace
	
	
	*** regressions
	/*
	i.	FLFP = average cooking time + average cooking time*number of meals
	ii.	FLFP = average cooking time*number of meals
	iii.FLFP = log (average cooking time) + log (average cooking time*number of meals)
	iv.	FLFP = log (average cooking time* number of meals)
	*/
	 
	ren (median_ingredients median_spices median_totaltime) (ingredients spices time)
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_time = log(time)
	gen femx = fem * time
	gen fem_logx = fem*log_time
	
	est clear
	foreach o of varlist p2p lfpr hours {
		eststo f1_`o': reghdfe `o' fem fem_logx if covid == 0, absorb(adm0 ym) cluster(adm0)
	}
	esttab f1_* using "$tables/cookpad_regressions.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label