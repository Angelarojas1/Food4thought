   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile merges country recipe databases			  *
   *																	  *
   * - Inputs: "${rawdata}/time use/Multinational Time Use Study/         *
   *			ALL_HAF_external.dta"									  *
   *			"${recipes}/cuisine_complexity_sum.dta"		  			  *
   * - Output: "${outputs}/Figures/survey_recipe.png"			          *
   * ******************************************************************** *

   ** IDS VAR:          country        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Jan 28, 2026

*================================================
* Time Use Survey: Cooking time by sex and country
*================================================
  
  *----------------------------------------*
  *        Eurostat 2010 : 18 countries    *
  *----------------------------------------*
 
   *--- Import Eurostat data for males 2010
   import excel "$rawdata\time use\world\Eurostat_2010\tus_00educ__custom_19830016_spreadsheet.xlsx",  ///
  sheet("Sheet 1") cellrange(A11:C37) firstrow clear
  
  drop C
  
  *- Drop observations without data
  drop if missing(Timespenthhmm)
  drop if Timespenthhmm == ":" | Timespenthhmm == "not available"
  
  rename Timespenthhmm male 
  tempfile males 
  save `males'
  
   *--- Import Eurostat data for females 2010
   import excel "$rawdata\time use\world\Eurostat_2010\tus_00educ__custom_19830016_spreadsheet.xlsx",  ///
  sheet("Sheet 2") cellrange(A11:C37) firstrow clear
  
  drop C

  *- Drop observations without data
  drop if missing(Timespenthhmm)
  drop if Timespenthhmm == ":" | Timespenthhmm == "not available"
  
  rename Timespenthhmm female
  
  merge 1:1 UNITLabels using `males', nogen
  
  *- Create column mentioning year of data 
  gen year = 2010
  gen Variable = "Food management except dish washing"
  
  rename UNITLabels country
  
  order country female male year Variable
  
  tempfile euro_2010
  save `euro_2010'

  *----------------------------------------*
  *        Eurostat 2020 : 7 countries     *
  *----------------------------------------*
  
  *--- Import Eurostat data for males

  import excel "$rawdata\time use\world\Eurostat_2020\tus_20educ__custom_19829904_spreadsheet.xlsx", ///
  sheet("Sheet 1") cellrange(A11:O16) clear
  
  *- Drop cells without information
  drop if missing(B)
  drop C E G I K M O 
  drop if A == ":"
  drop A
  
  sxpose, clear
  
  rename (_var1 _var2) (country male)
  
  gen year = 2020
  gen Variable = "Food management except dish washing"

  tempfile males 
  save `males'
  
  *--- Import Eurostat data for females

  import excel "$rawdata\time use\world\Eurostat_2020\tus_20educ__custom_19829904_spreadsheet.xlsx", ///
  sheet("Sheet 2") cellrange(A11:O16) clear
  
  *- Drop cells without information
  drop if missing(B)
  drop C E G I K M O 
  drop if A == ":"
  drop A
  
  sxpose, clear
  
  rename (_var1 _var2) (country female)
  
  gen year = 2020
  gen Variable = "Food management except dish washing"

  merge 1:1 country using `males', nogen
  
  order country female male year Variable
  
  *--- Append with data from 2010
  
  append using `euro_2010'
  
  *- Some countries are repated, we leave most recent data
  gsort country
  drop if country == "Austria" & year == 2010
  drop if country == "Estonia" & year == 2010
  drop if country == "Finland" & year == 2010
  drop if country == "Germany" & year == 2010
  drop if country == "Norway" & year == 2010
  drop if country == "Serbia" & year == 2010

  tempfile europe
  save `europe'

  *----------------------------------------*
  *     Other sources: rest of the world   *
  *----------------------------------------*
  
  *- Import data
	import excel "$rawdata\time use\world\cooking_time.xlsx", ///
	sheet("data") firstrow clear allstring

	destring year, replace
	
  *- Append with Europe data
	append using `europe'
	
  *- Organize country variable	
	gsort country
	replace country = trim(country)
	replace country = "Turkey" if country == "Türkiye"

  *- Organize time variable
	replace female = trim(female)
	replace male = trim(male)
	
	 split female, parse(":")
	 destring female1 female2, replace

	 gen female_min = female1*60 + female2
	 drop female1 female2
	  
	 split male, parse(":")
	 destring male1 male2, replace

	 gen male_min = male1*60 + male2
	 drop male1 male2
 
 *** Merge with FLFP for graph
	 merge 1:1 country using "${flfp}/FLFPlong2019.dta", keep(3) nogen
	 
	 save "$codedata/merge/cooking_time_world.dta", replace
	 
/*
*================================================
* Time Use Survey vs. Recipe data
*================================================

* import survey data
use "${rawdata}/time use/Multinational Time Use Study/ALL_HAF_external.dta",clear

* get the label of country
label list country

keep country isocountry main18 survey 

rename main18 survey_avgtime
rename survey year
drop if survey_avgtime == 0

sum survey_avgtime, de
list if survey_avgtime < 0 
drop if survey_avgtime < 0 

collapse (mean)survey_avgtime, by(country isocountry)
rename isocountry two_letter_country_code

* merge with recipe data
merge 1:1 two_letter_country_code using "${recipes}/cuisine_complexity_sum.dta", force
assert inlist(_merge, 1, 2, 3)
keep if _merge == 3
drop _merge

* scatter plot
twoway (scatter survey_avgtime time_mean, mlabel(country) c(. l) ms(Oh none) legend(off) ytitle("Avg Prep Time in survey"))(lfit survey_avgtime survey_avgtime)
graph export "${outputs}/Figures/survey_recipe.png", replace
