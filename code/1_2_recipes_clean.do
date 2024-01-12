   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * This dofile checks recipe information to be sure it makes sense i.e. recipes with more number of ingredients takes longer to cook
   *																	  *
   * - Inputs: "${recipes}/recipe_all_countries.dta"		      		  *
   * - Output:   										          		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: Ene 12, 2024

* import data
use "${recipes}/recipe_all_countries.dta", clear

* Drop recipes with information as zero in time and number of ingredients
drop if totaltime==0 // 6,155 observations deleted
drop if numberofingredients==0 // 590 observations deleted

** drop recipes that the total time are higher than 99%
bys country: egen p99 = pctile(totaltime), p(99)
drop if totaltime > p99
note: `r(N_drop)' recipes are dropped because of higher than 99%.

* Explore countries that have recipes with only one ingredient and cooking time is higher than 30 minutes

tab country if totaltime > 2 & numberofingredients == 1

/*
**checked and is okay
Argentina
Australia
Botswana
Bulgaria
China
Fiji
Germany
India - we lose 23 recipes that don't have list of ingredients and other variables. And like 4 of the recipes that only use 1 ingredient don't have full ingredients list.
Japan
Lithuania
Maldives
Philippines
Russia
Slovakia
South Africa
South Korea
Spain
United Kingdom
zimbabwe - We lose 15 recipes that don't have list of ingredients

**Checked and there's something to fix
Armenia- many recipes without information, others have ingredients but no time.
Brazil is okay but we are losing 34 recipes because the code didn't count the ingredients
Chile there's something wrong with the number of ingredients (0 and 1) for 29 recipes
Croatia - There's something wrong with this
Cuba is okay but we are losing 39 recipes because the code didn't count the ingredients
Dominican Republic is okay, but there's something weird with totaltime, there are recipes that take too long
Germany and Greece database is the same, fix it
Jordan, we lose 67 recipes because the ingredients are not separated by ''
Latvia, 4 recipes out of 69 don't have the correct number of ingredients
Lybia 26 recipes without any information, 4 recipes using one ingredient but is because it doesn't have information in the listofingredients, it does in listofinstructions
Peru, 71 recipes without correct number of ingredients (0 and 1)
Singapore the recipe with only one ingredient is because doesn't have info in listofingredients
Suriname 130 recipes with one ingredient because the ingredients are not separated by ''

*/

* After previous check for the cases where the recipes use a lot of ingredients but few time
tab country if totaltime < 10 & numberofingredients > 10
sort country numberofingredients totaltime 
tab nameoftherecipe if totaltime > 30 & numberofingredients == 1 & country == "Croatia"

* Later
tab country if numberofingredients == 0