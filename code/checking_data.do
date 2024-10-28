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
   ** Last modified: October 15, 2024
   
// global today : display %tdCYND date(c(current_date), "DMY")
// mkdir "${outputs}/data_check"
// mkdir "${outputs}/data_check/statistics"
   
   	 ** Create an output table
	 mat MAT_table = J(13,5,.)
	 mat coln MAT_table = "N" "Mean" "SD" "Min" "Max" 
	 mat rown MAT_table = "Log Time Median" "Time Median" "No Recipes" "Imp Ver P0" "Imp Ver P10" "Imp Ver P25" "Imp Ver P33" "Imp Ver P50" "Imp Ver P60" "Imp Ver P66" "Imp Ver P70" "Pop 2019" "Pop 2023"
   
	**# 	Time data 	#

   * Import data 
   use "${recipes}/cuisine_complexity_all.dta", clear
   
   preserve 
   keep country adm0
   tempfile countries
   save `countries'
   restore
   
   * Check time information
   gen logtime_median = log(time_median)
   sum logtime_median, de // Min: 2.71 Max: 4.79
   mat MAT_table[1,1] = (r(N),r(mean),r(sd),r(min),r(max))
   
   sum time_median // Min: 15 Max: 120
   mat MAT_table[2,1] = (r(N),r(mean),r(sd),r(min),r(max))
   
   * Check number of recipes
   sum num_recipes, de //Why is this important?
   * We are not including it in the regression.
   mat MAT_table[3,1] = (r(N),r(mean),r(sd),r(min),r(max))
   
	**# 	Versatility 	#
	
	local l = 3
	foreach x in "p0" "p10" "p25" "p33" "p50" "p60" "p66"  "p70"{ 
	
	* Import data
	use "${versatility}/imported/importbycountry_v2_`x'.dta", clear
	
	local ++l
	* Check data
	sum importVersatility, de
	mat MAT_table[`l',1] = (r(N),r(mean),r(sd),r(min),r(max))

	}

/*
Versatility measure goes from 0.0005 to 0.0707
*/

     **#      Population 	#
	 
	 * Import data
	 use "${pop}/populationlong2019_2023.dta", clear
	 merge m:1 adm0 using `countries', keep(3)
	 // Kosovo doesn't have population information
	 
	 * Check data
	 sum pop if year == 2019, de
	 mat MAT_table[12,1] = (r(N),r(mean),r(sd),r(min),r(max))
	 
	 sum pop if year == 2023, de
	 mat MAT_table[13,1] = (r(N),r(mean),r(sd),r(min),r(max))
	 
	 matlist MAT_table
	 
	 * Output 2. Frmttable (recomendado para doc y tex)
	frmttable using "${outputs}/data_check/statistics/summary_statistics.doc", replace sdec(2) 				///
		statmat(MAT_table)
	 

