   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile creates common flavor files 	        	  *
   *																	  *
   * - Inputs: "${versatility}/cuisine_ciat_suit.dta"	  	 			  *
   *		   "${precodedata}/flavor_profile/CIAT/{}.json"
   * - Output: "${versatility}/common_flavor.dta"             			  *
   *		   "${versatility}/common_flavor_3ing.csv"		  			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 28, 2023

******************************************************************************
* Calculate the number of common flavors between ingredients in CIAT database
******************************************************************************

**** Between 2 ingredients as a group ****

** import data
 use  "${versatility}/cuisine_ciat_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** generate every combination of ingredients(group of 2)
 gen ingredient2 = ingredient
 fillin ingredient ingredient2
 drop if ingredient == ingredient2
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_clean.dta")

end

**** Between 3 ingredients as a group ****

** import data
 use  "${versatility}/cuisine_ciat_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** generate every combination of ingredients(group of 3)
 gen ingredient2 = ingredient
 gen ingredient3 = ingredient
 fillin ingredient ingredient2 ingredient3
 drop if _fillin == 0
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_3ing.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor_3ing.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2, ingredient3): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2)).intersection(getflavor(ingredient3))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"], row["ingredient3"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_3ing_clean.dta")

end
 
******************************************************************************
* Calculate the number of common flavors between ingredients in Milla database
******************************************************************************
{
/*
**** Between 2 ingredients as a group ****

** import data
 use  "${versatility}/milla_ing_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** Drop ingredients without compounds data
 drop if ingredient == "annatto" | ingredient == "jatropha" | ingredient == "reed canary grass" | ingredient == "sugarcane" | ingredient == "switchgrass" | ingredient == "watermelons" | ingredient == "wetland rice"
 
** generate every combination of ingredients(group of 2)
 gen ingredient2 = ingredient
 fillin ingredient ingredient2
 drop if ingredient == ingredient2
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_m.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor_m.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_clean_m.dta")

end

**** Between 3 ingredients as a group ****

** import data
/*
 use  "${versatility}/milla_ing_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** Drop ingredients without compounds data
 drop if ingredient == "annatto" | ingredient == "jatropha" | ingredient == "reed canary grass" | ingredient == "sugarcane" | ingredient == "switchgrass" | ingredient == "watermelons" | ingredient == "wetland rice"
 
 
** generate every combination of ingredients(group of 3)
 gen ingredient2 = ingredient
 gen ingredient3 = ingredient
 fillin ingredient ingredient2 ingredient3
 drop if _fillin == 0
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_3ing_m.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor_3ing_m.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2, ingredient3): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2)).intersection(getflavor(ingredient3))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"], row["ingredient3"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_3ing_clean_m.dta")

end
*/

*/
}
*********************************************************************************
* Calculate the number of common flavors between ingredients in Milla data + CIAT
*********************************************************************************

**** Between 2 ingredients as a group ****

** import data
 use  "${versatility}/milla_ciat_ing_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** Drop ingredients without compounds data
 drop if ingredient == "annatto" | ingredient == "jatropha" | ingredient == "reed canary grass" | ingredient == "sugarcane" | ingredient == "switchgrass" | ingredient == "watermelons" | ingredient == "wetland rice" | ingredient == "kokum"
 
** generate every combination of ingredients(group of 2)
 gen ingredient2 = ingredient
 fillin ingredient ingredient2
 drop if ingredient == ingredient2
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_m_c.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor_m_c.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_clean_m_c.dta")

end