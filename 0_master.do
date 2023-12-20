
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
	global code					"$github/code"
	
	global precode				"$projectfolder/precode"
	global recipes              "$precode/recipes"	
	
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
	global outputs				"$projectfolder/outputs"
	
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
	*		- Clean data for calculating versatility.
	*       - Creates native versatility and imported versatility and 

		do "$code/8_versatility_clean.do" 

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate native versatility by country

		do "$code/9_native_versatility.do"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Generate imported versatility by country

		do "$code/10_imported_versatility.do"
		
		
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
	*             FAO suitability Data Coding               *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Read in crop suitability data from FAO
	*		- Creates suitability variable
	*  		- Don't run this part. Treat the suitability data as raw
	
	*	do "$code/13_FAO_suitability.do"
	
	* ***************************************************** *
	*              Time Use Survey Data Validation          *
	* ***************************************************** *

	* 	The purpose of this dofile is:
	*		- Compare time variable from survey data vs 
	*		  recipe data

		do "$code/14_time_use_survey.do"
	
	* ***************************************************** *
	*          		 FLFP raw correlations     	 	        *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	* 		- Raw correlations of FLFP and cuisine complexity
	*		- 134 countries with FLFP information
		
		do "$code/15_cuisine_flfp_rawcorr.do"
				
		
	* ***************************************************** *
	*              	 	 Regressions                	    *
	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Runs regressions ussing cookpad, FLFP and cuisine 
	*			complexity variables
	* 		- Creates scatter plots:
	*		  	Complexity variables vs avg meals cooked
		
		do "$code/16_cookpad_flfp_cuisine_reg.do"

	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Find the best performance 1st stage regressions
	*		- Best: p60, g3simple

		do "$code/17_1ststage_best.do"

	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Merge the different databases created to run regressions

		do "$code/18_merge_reg.do"

	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Run IV regressions

		do "$code/19_IV_reg.do"
		
	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Merge cookpad and CIAT databases
	*		- Run regressions

		do "$code/20_cookpad_ciat.do"
		

	