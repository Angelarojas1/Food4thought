   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: In this code we are identifying problems in the data, 
   ** 			   especially in following variables:
   ** Vars: time, vers, population and num of recipes
   ** Written by: Ángela Rojas
   ** Last modified: October 7, 2024
   
**# Time data #1

   **** Check recipe data ****
   
   * Import data 
   use "${recipes}/cuisine_complexity_all.dta", clear
   
   * Check time information
   gen logtime_median = log(time_median)
   sum logtime_median, de // Min: 2.71 Max: 4.79
   
   sum time_median // Min: 15 Max: 120
   
**# Versatility #2

	*** Check versatility data ***
	
	* Import data
	foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66"  "p70"{ 
	
	use "${versatility}/imported/importbycountry_v3_`x'.dta", clear
	sum importVersatility, de

	}

/*
Versatility measure goes from 0.0005 to 0.0707
*/
