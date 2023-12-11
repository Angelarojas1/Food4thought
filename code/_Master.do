
* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*                Authors: Girija Borker and Margarita Gáfaro          		   *
*						  	Master do-file  							   	   *
* **************************************************************************** *
	
	* Written by: Xinyu Ren and Angela Rojas
	* Last date modified: Dec 4, 2023

	clear all
	set more off
	pause on

	* ***************************************************** *
	
	** Root folder globals 

	if "`c(username)'" == "stell" {
	global projectfolder "/Users/stell/Dropbox/food4thought/analysis23"
	global github "/Users/stell/OneDrive/Escritorio/Documentos/GitHub/Food4thought"
	}
	
	if "`c(username)'" == "[xx's Username]" {
	global projectfolder "[insert ss's root directory for Dropbox]"
	global github "[insert ss's root directory for Github]"
	}

	** Project folder globals
	
	* Dofile sub-folder globals
	global code					"$github/analysis23/code"
	
	global precode				"$projectfolder/precode"
	global precode_ing_tagger	"$precode/recipes/ingredient_tagger"
	global precode_scrape		"$precode/recipes/scrape_recipe_data"
	global precode_vb_const		"$precode/recipes/variable_construction"
	
	* Dataset sub-folder globals
	global precodedata			"$projectfolder/data/precoded"
	global rawdata				"$projectfolder/data/raw"
	global codedata				"$projectfolder/data/coded"
	
	* Output sub-folder globals
	global outputs				"$projectfolder/outputs"


	* ***************************************************** *
	*                Recipe Data Coding                     *
	* ***************************************************** *

	* Scrape recipe data by country
	// Don't run this part. Treat the recipe data as raw
	// $precode_scrape
	
	* Clean recipe data by country
	// Don't run this part. Treat the recipe data as raw
	// $precode_ing_tagger
	
	* Construct variables
	// Don't run this part. Treat the recipe data as raw
	// $precode_vb_const
	
	* ***************************************************** *
	*      Prepare Recipe data by country and FLFP data     *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Merge recipe data and FLFP in 2019
	* 		- 134 countries with FLFP information
	
		do "$code/1_recipes_flfp.do" 
	
	* 	The purpose of this dofile is:
	* 		- Raw correlations of FLFP and cuisine complexity
		
		do "$code/2_recipes_flfp_rawcorr.do"

		
	* ***************************************************** *
	*              Time Use Survey Data Coding              *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		-  compare time use survey with recipe data

		do "$code/3_time_use_survey.do"

		
	* ***************************************************** *
	*                 Cookpad Data Coding                   *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		-  Clean cookpad data

		do "$code/4_cookpad_clean.do"
	
	
	* ***************************************************** *
	*              		 IV Data Coding             	    *
	*               Native & Imported versatility           *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		-  Read in crop suitability data from FAO
	*  		-  Don't run this part. Treat the suitability data as raw
	
	*	do "$code/5_FAO_suitability.do"
	
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		-  Clean data from CIAT Map
	*		-  This gets native ingredient by country and region.
	*       -  Merge data with recipes and FLFP database.
	*       -  135 countries with native ingredient information
	
		do "$code/6_ciat_clean.do"  

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		-  Clean data from suitability databases

		do "$code/7_suitability_clean.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Clean data for calculating versatility.
	*       - Creates native versatility and imported versatility and 
	*       - Creates common flavor (between 2 and 3 ingredients) files.

		do "$code/8_versatility_clean.do" 

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Calculate the distance between any two countries

		do "$code/9_distance_clean.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate geographical controls for all countries

		do "$code/10_geographical_clean.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate native versatility by country

		do "$code/11_native_versatility.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate imported versatility by country

		do "$code/12_imported_versatility.do"

		
	* ***************************************************** *
	*              	 	 Regressions                	    *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Find the best performance 1st stage

		do "$code/13_1ststage_best.do"

	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Merge the different databases created to run the regressions

		do "$code/14_merge_reg.do"

	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Run IV regressions

		do "$code/15_IV_reg.do"
		
	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Merge cookpad and CIAT databases
	*		- Run regressions

		do "$code/16_cookpad_ciat.do"
	