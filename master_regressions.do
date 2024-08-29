
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
	global github "C:\Users\stell\OneDrive - Universidad de los andes\Documentos\GitHub\Food4thought"
	}
	
	if "`c(username)'" == "[xx's Username]" {
	global projectfolder "[insert ss's root directory for Dropbox]"
	global github "[insert ss's root directory for Github]"
	}

	** Project folder globals
	
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
	global outputs				"$projectfolder/outputs"

	* ***************************************************** *
	
	* 	The purpose of this dofile is:
	*		- Clean data for calculating versatility.
	*       - Creates native versatility and imported versatility files

		do "$code/8_versatility_clean.do" 
		
	*	The purpose of this dofile is:
	*		- Create imported versatility file that include native ingredients.
	
		do "$code/8_versatility_clean_v2.do" 
		
	*	The purpose of this dofile is:
	*		- Create imported versatility files that don't have suitability filter
	
		do "$code/8_versatility_clean_v3.do" 
		
	*	The purpose of this dofile is:
	*	- Create imported versatility file that include native ingredients.
	*	- Create imported versatility files that don't have suitability filter
	
		do "$code/8_versatility_clean_v4.do" 

	* ***************************************************** *

	
	* 	The purpose of this dofile is:
	*		- Generate imported versatility by country

		do "$code/10_imported_versatility.do"
		
	*	The purpose of this dofile is:
	*		- Create imported versatility measure that include native ingredients.
	
		do "$code/10_imported_versatility_v2.do"
		
	*	The purpose of this dofile is:
	*		- Create imported versatility measure that don't have suitability filter
	
		do "$code/10_imported_versatility_v3.do"
		
	*	The purpose of this dofile is:
	*	- Create imported versatility measure that include native ingredients.
	*	- Create imported versatility measure that don't have suitability filter
	
		do "$code/10_imported_versatility_v4.do"
		
		
	* ***************************************************** *
		
	* 	The purpose of this dofile is:
	*		- Find the best performance 1st stage regressions
	*		  using cookpad variables
	*		- Regressions individual level
	*		- Best: 

		do "$code/20_1stage_best_cookpad.do"
		do "$code/20_1stage_best_cookpad_v2.do"
		do "$code/20_1stage_best_cookpad_v3.do"
		do "$code/20_1stage_best_cookpad_v4.do"
		

		

	