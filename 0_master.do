* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Girija Borker, Margarita Gáfaro, Steve Berggreen
* 				Last date modified: June 17, 2025 						   	   *
*				Modified by: Ángela Rojas
*				Master dataset generation file
* **************************************************************************** *
	
	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	** Root folder globals 

	if "`c(username)'" == "stell" { // Angela
	cd "C:\Users\stell\OneDrive\Escritorio\Documentos\GitHub\Food4thought"
	global projectfolder "C:/Users/stell/Dropbox/food4thought/analysis23"
	global github "C:\Users\stell\OneDrive\Escritorio\Documentos\GitHub\Food4thought"
	}
	
	if "c(username)" == "mgafargo" { // Margarita 
	cd "C:\Users\mgafargo\Dropbox\food4thought\analysis23\"
	global projectfolder "C:\Users\mgafargo\Dropbox\food4thought/analysis23"
	global github "C:\Users\mgafargo\Dropbox\food4thought"
	}
	
	* Dofile sub-folder globals
	global code					"$github/code"
	
	* Python codes folder
	global precode				"$github/precode" 
	global recipe_code          "$precode/recipes"	
	
	* Dataset sub-folder globals
	global precodedata			"$projectfolder/data/precoded"
	global rawdata				"$projectfolder/data/raw"
	global codedata				"$projectfolder/data/coded"
	
	global recipes              "$codedata/recipes"
	global flfp             	"$codedata/FLFP"
	global mlfp             	"$codedata/MLFP"
	global gdp	             	"$codedata/GDP"
	global versatility          "$codedata/iv_versatility"
	global cookpad              "$codedata/cookpad"
	global fao_suit             "$codedata/FAO_suitability"
	global pop                  "$codedata/population"

	
	* Output sub-folder globals
	global outputs				"$projectfolder/outputs"
	global tables				"$outputs/Tables"
	global figures				"$outputs/Figures"
	
	* ***************************************************** *
	
	* Setting the ado path with required packages
	sysdir set PLUS "${code}/ado"

	** Install packages (run once)
	
	* ssc install aaplot
	* ssc install ivreghdfe
	* ssc install ivreg2
	* ssc install reghdfe
	* ssc install ftools
	* ssc install ranktest
	* ssc install winsor4
	* ssc install dataex
	* ssc install geoinpoly
	* ssc install kountry
	* ssc install winsor4
	* ssc install shp2dta
	* ssc install spmap
	
	** Section to create all the folders I need in data/coded folder
	* mkdir
	
	* ***************************************************** *
	*                Recipe Data Coding                     *
	* ***************************************************** *

	* Scrape recipe data by country - Python
	// Don't run this part. Treat the recipe data as raw
	// "$recipes/scrape_recipe_data"
	
	* Clean recipe data by country - Python
	// Don't run this part. Treat the recipe data as raw
	// "$recipes/ingredient_tagger"
	
	* Construct variables - Python
	// Don't run this part. Treat the recipe data as raw
	// "$recipes/variable_construction"
	
	* 	The purpose of this dofile is:
	*		- Merge recipe data for 139 countries.
	*		- Run only if you are adding a country.
	
	*	do "$code/1_merge_recipes.do" 	

	* 	The purpose of this dofile is:
	*		- Clean recipes dataset
	* 		- Create time, ingredients and spices variables for 
	*         different percentiles (cuisine complexity variables)
	*		- Country level databases
	
		do "$code/2_cuisine_variables.do" 
		
	* ***************************************************** *
	*     				 LFP Data Coding				    *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean FLFP data
	* 		- 134 countries with FLFP information
	
		do "$code/3_flfp_clean.do" 	

	* 	The purpose of this dofile is:
	*		- Clean MLFP data
	* 		- 221 countries with MLFP information
	
		do "$code/mlfp_clean.do" 	
		
	* 	The purpose of this dofile is:
	*		- Merges FLFP and MLFP data
	
		do "$code/lfp_clean.do" 	
		
	* ***************************************************** *
	*     				 GDP Data Coding				    *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean GDP data (per capita and total)
	* 		-  countries with GDP information
	
		do "$code/gdp_clean.do" 
	
	* ***************************************************** *
	*             Population Data Coding				    *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean population data

		do "$code/population_clean.do" 
		
	* ***************************************************** *
	*                  CPI Data Coding	    			    *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean consumer price index

		do "$code/cpi_clean.do" 
		
	* ***************************************************** *
	*               Exchange rate Data Coding	    		*
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean Exchange rate local currency – USD

		do "$code/exchange_rate_clean.do" 
		
	* ***************************************************** *
	*              Appliances price Data Coding	    		*
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean appliances price index for US and EU

		do "$code/price_index_clean.do" 
		
	* ***************************************************** *
	*                 Distance Data Coding                  *
	* ***************************************************** *	
		
	* 	The purpose of this dofile is:
	*		- Calculate the distance between any two countries
	*		- Info for 139 countries
	*       - This is for imported versatility variable

		do "$code/4_distance_clean.do"	
		
	* ***************************************************** *
	*        Native ingredients clasification       	    *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		-  Clean data from CIAT Map
	*		-  This gets native ingredients by country and region.
	*       -  Merges ingredient data with recipes and FLFP database.
	*       -  136 countries with native ingredient information
	
		do "$code/5_ciat_clean.do"  

	* 	The purpose of this dofile is:
	*		-  Clean data from Millan data 
	*		-  Creates dataset for Millan + CIAT
	
		do "$code/crop_origin_clean.do"
		
	* ***************************************************** *
	*              		 Suitability                	    *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Clean data from suitability databases
	*		- 136 countries with suitability data
	*       - For the other 5 countries we create the suitability data

		do "$code/6_suitability_clean.do"
		
	* 	The purpose of this dofile is:
	*		- Merge Milla and CIAT data with suitability data

		do "$code/suitability_clean_milla.do"
	
	* ***************************************************** *
	*             FAO suitability Data Coding               *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Read in crop suitability data from FAO
	*		- Creates suitability variable
	*  		- Don't run this part. Treat the suitability data as raw
	
		do "$code/13_FAO_suitability.do"
		
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*       - Creates common flavor (between 2 and 3 ingredients) files.

		do "$code/7_common_flavor.do"

	* ***************************************************** *
	*              		 IV Data Coding             	    *
	*               Native & Imported versatility           *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Clean data for calculating versatility.
	*       - Creates native versatility and imported versatility files

		do "$code/8_versatility_clean_v2.do" 
		
	* ***************************************************** *
		
	*	The purpose of this dofile is:
	*		- Create every combination between 2 ingredients
		
	    do "$code/32_2ingredient_combination.do"
		
	* ***************************************************** *
	*         Geographical Controls from Galor              *
	* ***************************************************** *	
	
	* 	The purpose of this dofile is:
	*		- Clean control variables from Galor data 

		do "$code/10_galor_clean.do"
		
	* ***************************************************** *
	*              Geographical Data Coding                 *
	* ***************************************************** *	
	
	* 	The purpose of this dofile is:
	*		- Generate geographical controls for all countries
	*		- Info for 138 countries (Kosovo pending)

		do "$code/11_geographical_clean.do"
		
	* ***************************************************** *
	*                 Cookpad Data Coding                   *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean cookpad data

		do "$code/12_cookpad_clean.do"
		
	* ***************************************************** *
	*              		 IV Data Analysis             	    *
	*                  Versatility variables                *
	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Generate only native versatility measures. 

		do "$code/34_new_versatility_only_native_m_c.do"
	
	* 	The purpose of this dofile is:
	*		- Generate versatility by country

		*do "$code/34_new_versatility_including_native.do" // in archive folder
		
	* 	The purpose of this dofile is:
	*		- Generate versatility by country using Milla data

		*do "$code/34_new_versatility_including_native_milla.do" // in archive folder	
		
	* 	The purpose of this dofile is:
	*		- Generate versatility by country using Milla + CIAT data

		*do "$code/34_new_versatility_including_native_milla_ciat.do" // in archive folder	
		
	* ***************************************************** *
	*                 Cookpad Data Coding                   *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Merge cookpad and versatility data
	*		- Add a cookpad indicator to versatility dataset

		do "$code/35_cookpad_data.do"
		
	* ***************************************************** *
	*            First Stage IV Dataset Creation            *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Create database with all variables needed for 
	*		  regressions
	
		do "$code/37_FirstStage_versatility_dataset.do"
		
	*********************************************************
	*					Versatility Analysis
	*********************************************************
	
	* 	The purpose of this dofile is:
	*		- Create desciptive statistics
	
	    do "$code/es_descriptives.do"

	
	* 	The purpose of this dofile is:
	*		- Run cookpad regressions
	*		- Contains OLS, 1stage, RF, IV
	
		do "$code/36_cookpad_analysis.do"

	* 	The purpose of this dofile is:
	*		- Run cookpad regressions
	*		- The file was created by MG
	
		do "$code/es-cookpad-mg.do"
		
	* 	The purpose of this dofile is:
	*		- Run country level regressions
		
		do "$code/country_level_analysis.do"
		
	* 	The purpose of this dofile is:
	*		- Run country level regressions
	*		- The file was created by MG
		
		do "$code/temp-mg.do"
		
	* 	The purpose of this dofile is:
	*		- Run individual level regressions
	*		- The file was created by MG for draft sent on december 8
		
		do "$code/temp-cookpad-mg-v2.do"
		
	* 	The purpose of this dofile is:
	*		- Run individual level regressions using PCA index
	*		- The file was created by MG for draft sent on december 8
		
		do "$code/temp-cookpad-mg-pca.do"
		
	* 	The purpose of this dofile is:
	*		- Run country level regressions
	*		- The file was created by Steve
	*		- Focus on regression using native spices versatility 
		
		do "$code/native_spice_reg_251015.do"
		
	* ***************************************************** *
	*                        Graphs                         *
	* ***************************************************** *
	
	*	do "$code/cuisine_histograms.do" // in archive folder
		
	* ***************************************************** *
	
	*	The purpose of this dofile is:
	*		- Creates plots: winsorized variables, outliers, mexico vs Colombia
	
		* do "$code/30_time_outliers.do" // in archive folder
		
	* ***************************************************** *
	
	*	The purpose of this dofile is:
	*		- Creates heat maps for FLFP, MLFP and gap.
	
		 do "$code/heat_maps_lfp.do" // in archive folder
		 
	* ***************************************************** *
	
	*	The purpose of this dofile is:
	*		- Creates line graphs for FLFP, MLFP and gap vs cuisine variables
	
		 do "$code/graphs_lfp_cuisine.do" // in archive folder
		 
	* ***************************************************** *
	
	*	The purpose of this dofile is:
	*		- Creates bar graph for cooking time around the world
	*		- Uses Time Use Survey data
	
		 do "$code/bar_cook_time.do" // in archive folder
	
	