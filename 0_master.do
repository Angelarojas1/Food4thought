* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Master dataset generation file
* **************************************************************************** *
	
	

	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	** Root folder globals 

	if "`c(username)'" == "stell" {
	global projectfolder "C:/Users/stell/Dropbox/food4thought/analysis23"
	global github "C:\Users\stell\Dropbox\food4thought\analysis23"
	}
	
	if "`c(username)'" == "wb641362" { // Varun
	global projectfolder "C:\Users\wb641362\Dropbox\food4thought\analysis23"
	global github "C:\Users\wb641362\OneDrive - WBG\Documents\GitHub\Food4thought"
	}
	
	if "c(username)" == "mgafargo" { // Margarita
	global projectfolder "C:\Users\mgafargo\Dropbox\food4thought"
	}

	** Project folder globals
	global files "$projectfolder\data\coded"
	
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
	global versatility          "$codedata/iv_versatility"
	global cookpad              "$codedata/cookpad"
	global fao_suit             "$codedata/FAO_suitability"

	
	* Output sub-folder globals
	global outputs				"$files/Outputs"
	global tables				"$projectfolder\outputs\Tables"
	
	* ***************************************************** *

	** Install packages (run once)
	
	* ssc install aaplot
	* ssc install ivreghdfe
	
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
	*     				FLFP Data Coding				    *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean FLFP data
	* 		- 134 countries with FLFP information
	
		do "$code/3_flfp_clean.do" 	
	
	* ***************************************************** *
	*                 Distance Data Coding                  *
	* ***************************************************** *	
		
	* 	The purpose of this dofile is:
	*		- Calculate the distance between any two countries
	*		- Info for 139 countries
	*       - This is for imported versatility variable

		do "$code/4_distance_clean.do"	
		
	* ***************************************************** *
	*              		 IV Data Coding             	    *
	*               Native & Imported versatility           *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		-  Clean data from CIAT Map
	*		-  This gets native ingredients by country and region.
	*       -  Merges ingredient data with recipes and FLFP database.
	*       -  136 countries with native ingredient information
	
		do "$code/5_ciat_clean.do"  

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Clean data from suitability databases
	*		- 136 countries with suitability data
	*       - For the other 5 countries we create the suitability data

		do "$code/6_suitability_clean.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*       - Creates common flavor (between 2 and 3 ingredients) files.

		do "$code/7_common_flavor.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate versatility by country

		do "$code/34_new_versatility_including_native.do"
		
		
	* ***************************************************** *
	*                 Cookpad Data Coding                   *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Clean cookpad data

		do "$code/35_cookpad_data.do"
		
	* ***************************************************** *
	*            First Stage IV Dataset Creation            *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Add a cookpad indicator to versatility dataset
	
		do "$code/37_FirstStage_versatility_dataset.do"
		
	*=======================================================*
	*	Please proceed to master_regressions for analysis
	*=======================================================*
	