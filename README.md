# Replication Package for: The Burden of Putting Food on the Table: Cuisine Complexity and Women’s Labor Force Participation

We study if more complex cuisines—requiring greater time and specialized skills for food preparation—lead to women bearing a disproportionate cooking burden that crowds out labor force participation. We propose a household time-allocation model with a cooking technology in which the accumulation of cooking-specific human capital interacts with cuisine complexity to generate persistent female specialization in cooking, arising from initial productivity differences in labor outside the household. Using nearly 70,000 online recipes from 137 countries, we construct a cuisine complexity index based on cooking time, ingredient variety, and spices. Merging this with individual-level data on women's economic participation, we employ an instrumental variable strategy leveraging exogenous variation in native ingredient flavor versatility. Results show that an increase in cuisine complexity by one standard deviation reduces women's labor force participation by 18 percent overall and 25 percent for married women. This effect operates through women's cooking specialization: complexity reduces meals cooked by men but not women. 

## Contents

1. [Overview](#overview)
2. [Data Availability](#data-availability)
3. [Instructions for Replicators](#instructions-for-replicators)
4. [List of Exhibits](#list-of-exhibits)
5. [Requirements](#requirements)

The rest of the contents of this README file is highly desirable, but not strictly needed for reproducibility. The points above are needed.

6. [Code Description](#code-description)
7. [Folder Structure](#folder-structure)


## Overview

The code in this replication package create the figures and tables in the paper using Stata. A main file runs all of the code to generate the data for the outputs. The replicator should expect the code to run for about xx hours.

## Data Availability

This section will outline where and how the data supporting the findings of the study can be accessed and used. This is crucial, especially for replicating the results, as only the same data will be able to produce consistent results. Make sure to list all the datasets used and categorize them as follows:

- [ ] All data are publicly available.

- [ ] Some data cannot be made publicly available.

- [ ] No data can be made publicly available.

### Statement about Rights

- [ ] I certify that the author(s) of the manuscript have legitimate access to and permission to use the data used in this manuscript.
- [ ] I certify that the author(s) of the manuscript have documented permission to redistribute/publish the data contained within this replication package. Appropriate permission are documented in the LICENSE.txt file.

## Dataset list

### Available on Dropbox. [Link](https://www.dropbox.com/scl/fo/ryfoxivg9i4crk142py0a/AGOC8kHZsflsDJ2AcHu8qYw?rlkey=1lyhl4fvy16ikxlnooim50ug0&st=qonapjtb&dl=0)
| Data file | Source | Notes    | Provided |
|-----------|--------|----------|---------|
| `data/precoded/recipes/*` | Websites | The files in this folder contain lists of recipes by country. The data were collected from multiple sources and compiled using the code available in the precoded folder. However, this code should not be run again, as the websites used as data sources may have changed over time, which could result in outputs that differ from the original data. See below for more details. |  Yes  |
| `data/precoded/suitability/staple_suitability.dta` | FAO | Staple suitability by country. |  Yes  |
| `data/precoded/suitability/spices_suitability.dta` | FAO | Spices suitability and geographical variables by country.|  Yes  |
| `data/precoded/suitability/spices_suitability_10nov23.dta` | FAO | Spices suitability by country. |  Yes  |
| `data/precoded/suitability/crop_suitability.dta` | FAO | Crops suitability and geographical variables by country. |  Yes  |
| `data/precoded/suitability/country-vars-9nov23.csv` | FAO | Geographical variables by country. |  Yes  |
| `data/precoded/flavor_profile/flavor_cleaned/*` | [FlavorDB](https://cosylab.iiitd.edu.in/flavordb/search) | Flavor molecules by ingredient. Using the code in the folder data/precoded/flavor_profile, the JSON files containing the ingredients and their flavor molecules were downloaded and then renamed. Since the website could change, the code should not be run again. Accessed in March 2023. |  Yes  |
| `data/raw/gdp/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_134819.csv` | [World Bank](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD) | Country level GDP per capita data from 1990 to 2019. Accessed on October, 2025. |  Yes  |
| `data/raw/CIAT/food_supplies_countries_regions_all_merge.csv` | [CIAT](https://github.com/CIAT-DAPA/cwr_interdependence) | Used to identify the region each country belongs to. Accessed on March, 2023. |  Yes  |
| `data/raw/CIAT/ingredients_category.xlsx` | Created by team | List of ingredients and an indicator for fruits.  |  Yes  |
| `data/raw/CIAT/region_ingredients.xlsx` | [CIAT](https://cgspace.cgiar.org/server/api/core/bitstreams/f84f3289-ed7d-45ab-9397-43a2683cf028/content) | Native ingredients for each region. The information from the map was manually transcribed into a database. Accessed on March, 2023. |  Yes  |
| `data/raw/cookpad/Cookpad_032023.dta` | Cookpad | Survey database collected by Gallup. |   |
| `data/raw/Crop_Origins_Phylo-master/Crop_Origins_Phylo_v_live\crop_origins_v_live/crop_origins_live_db.csv` | [Crop Origins and Phylo Food](https://github.com/rubenmilla/Crop_Origins_Phylo/tree/master/Crop_Origins_Phylo_v_live/crop_origins_v_live) | This database includes a comprehensive checklist of crops species cultivated for food, and data on diverse continuous and categorical descriptors of antiquity of cultivation, organ harvested for primary use, growth form, agricultural relevance, and identities, distribution and climate at origin of crops wild progenitors. Accessed on August, 2025. |  Yes  |
| `data/raw/Crop_Origins_Phylo-master/ecoregion_country.xlsx` | [Crop Origins and Phylo Food](https://github.com/rubenmilla/Crop_Origins_Phylo/tree/master/Crop_Origins_Phylo_v_live/crop_origins_v_live) | Country and ecoregion it belongs to. Accessed on August, 2025. |  Yes  |
| `data/raw/distance/geo_cepii.dta` | Created by team | Location information for country's capital. |  Yes |
| `data/raw/Galor/CountryLevel.dta` | [Oded Galor and Ömer Özak](https://www.openicpsr.org/openicpsr/project/113035/version/V1/view?path=/pcms/projects/1/1/3/0/113035/V1.0.1/20150020_data/data&type=folder) | Geographical variables by country. Accessed on September, 2025 |  Yes  |
| `data/raw/plough/Alesina_Giuliano_Nunn_QJE_2013_Replication_Materials/Replication_Materials/crosscountry_dataset.dta` | [Alberto Alesina, Paola Giuliano and Nathan Nunn](https://www.dropbox.com/scl/fi/qaacivo811xrnik5jmdz0/Alesina_Giuliano_Nunn_QJE_2013_Replication_Materials.zip?dl=0&e=1&file_subpath=%2FReplication_Materials&rlkey=n3q8pf0x2nee26vfilhmrvkqb) | Country level variables used for the paper `ON THE ORIGINS OF GENDER ROLES: WOMEN AND THE PLOUGH'. Accessed on August 5, 2026. |  No  |
| `data/raw/roster_spices/roster_spices_edited.xlsx` | Created by team | List of spices |  Yes  |
| `data/raw/roster_spices/spices.xlsx` | Created by team | List of spices |  Yes  |



### Precoded dataset list. 
This section provides details on the sources of the files stored in the `data/precoded/recipes/initial` folder. The files in the intermediate and final folders are derived from the information contained in these initial files.

| Data file | Source | Notes    |License to share data |
|-----------|--------|----------|---------|
| `Afghanistan.csv` | [Afghan kitchen recipes](http://www.afghankitchenrecipes.com/) | Accessed on July 3, 2022. | Yes |
| `Albania.csv` | [My Albanian Food](https://www.myalbanianfood.com/albanian-recipes/) | Accessed on July 3, 2022. | Yes |
| `Algeria.csv` | [Algerian Cookbook](https://www.amazon.com/Algerian-Cookbook-Authentic-Cooking-Recipes-ebook/dp/B07JM6R3ZR) | Accessed on July 28, 2022. | Yes |
| `Argentinas.csv` | [Recetas Argentinas](https://www.recetas-argentinas.com/) | Accessed on October 7, 2021. | Yes |
| `Armenia.csv` | [The Armenian Kitchen](https://thearmeniankitchen.com/) | Accessed on July 31, 2022. | Yes |
| `Aruba.csv` | [Taste of Aruba](https://aruba.bynder.com/m/4fcf5faabcb5ad77/original/Taste-Of-Aruba-2020-Digital.pdf) | Accessed on July 28, 2022. | Yes |
| `Australia.csv` | [Taste](http://taste.com.au/) | Accessed on October 15, 2021. | Yes |
| `Austria.csv` | [Chefkoch](http://chefkoch.de/) | Accessed on October 15, 2021. | Yes |
| `Bahamas.csv` | [Yummly](https://www.yummly.com/recipes/bahamian) | Accessed on July 3, 2022. | Yes |
| `Bahrain.csv` | [Cookpad](https://cookpad-com.translate.goog/ae/search/%D8%A7%D9%84%D8%A8%D8%AD%D8%B1%D9%8A%D9%86?_x_tr_sl=ar&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=sc) | Accessed on July 3, 2022. | Yes |
| `Bangladesh.csv` | [The Bangladeshi Kitchen](https://www.thebangladeshikitchen.com/recipes/) | Accessed on July 3, 2022. | Yes |
| `Barbados.csv` | [Yummly](https://www.yummly.com/recipes/barbados) | Accessed on July 3, 2022. | Yes |
| `Belarus.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t86,96/Osteuropa-Weissrussland-Rezepte.html) | Accessed on January 24, 2022. | Yes |
| `Belgium.csv` | [June d'Arville](https://www.junedarville.com/recipes/belgian) | Accessed on July 4, 2022. | Yes |
| `Belize.csv` | [Flavors of the World - Belize](https://www.dropbox.com/s/xd0vkvmocapp8ab/Flavors%20of%20the%20World%20-%20Belize%20Over%2025%20Delicious%20Recipes%20You%20Cant%20Resist%20%28Nancy%20Silverman%29%20%28z-lib.org%29.pdf?dl=0) | Accessed on April 25, 2022. | Yes |
| `Benin.csv` | [Cuisine AZ](https://www.cuisineaz.com/cuisine-du-monde/benin-p265) | Accessed on July 3, 2022. | Yes |
| `Bolivia.csv` | [Cocina Boliviana](https://www.cocina-boliviana.com/) | Accessed on October 8, 2021. | Yes |
| `Bosnia and Herzegovina.csv` | [All That's Jas](https://www.all-thats-jas.com/category/bosnia-and-herzegovina/) | Accessed on May 17, 2022. | Yes |
| `Botswana.csv` | [Very Good Recipes](https://verygoodrecipes.com/botswana) | Accessed on July 13, 2022. | Yes |
| `Brazil.csv` | [Cocina Brasileña](https://www.cocina-brasilena.com/) | Accessed on October 8, 2021. | Yes |
| `Bulgaria.csv` | [Gotvach](https://recepti.gotvach.bg/?n=1) | Accessed on July 3, 2022. | Yes |
| `Cabo Verde.csv` | [Yummly](https://www.yummly.com/recipes/cape-verde) | Accessed on July 3, 2022. | Yes |
| `Cambodia.csv` | [Cambodia Recipe](https://www.cambodiarecipe.com/cuisine/cambodian/?sort=date) | Accessed on July 3, 2022. | Yes |
| `Cameroon.csv` | [Cookpad](https://cookpad.com/us/search/cameroon?event=search.typed_query) | Accessed on July 3, 2022. | Yes |
| `Canada.csv` | [Taste Canada](https://tastecanada.org/recipes/) | Accessed on May 17, 2022. | Yes |
| `Chile.csv` | [Cocina Chilena](https://www.cocina-chilena.com/) | Accessed on October 8, 2021. | Yes |
| `China.csv` | [Meishichina](https://home.meishichina.com/recipe-list.html) | Accessed on June 1, 2022. | Yes |
| `Colombia.csv` | [Cocina Colombiana](https://www.cocina-colombiana.com/) | Accessed on October 8, 2021. | Yes |
| `Comoros.csv` | [Cuisine des îles Comores](https://www.scribd.com/read/519866335/Cuisine-des-iles-Comores-Cuisine) | Accessed on August 10, 2022. | Yes |
| `Costa Rica.csv` | [Recetas Costa Rica](https://www.recetascostarica.com/) | Accessed on October 8, 2021. | Yes |
| `Cote Divoire.csv` | [196 Flavors](https://www.196flavors.com/category/continent/africa/west-africa/cote-divoire/) | Accessed on April 25, 2022. | Yes |
| `Croatia.csv` | [Coolinarika](https://www.coolinarika.com/) | Accessed on July 3, 2022. | Yes |
| `Cuba.csv` | [Cocina Cubana](https://www.cocina-cubana.com/) | Accessed on October 8, 2021. | Yes |
| `Cyprus.csv` | [Afrodite's Kitchen](https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/) | Accessed on May 17, 2022. | Yes |
| `Czech.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,86,97/Europa-Osteuropa-Tschechien-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Denmark.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,130/Europa-Daenemark-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Dominica.csv` | [Dominica Gourmet](https://dominicagourmet.com/) | Accessed on May 17, 2022. | Yes |
| `Dominican Republic.csv` | [Dominican Cooking](https://www.dominicancooking.com/recipe-index) | Accessed on May 17, 2022. | Yes |
| `Ecuador.csv` | [Cocina Ecuatoriana](https://www.cocina-ecuatoriana.com/) | Accessed on October 8, 2021. | Yes |
| `Egypt.csv` | [Just Food](http://justfood.tv/) | Accessed on July 5, 2022. | Yes |
| `EI Salvador.csv` | [Recetas Salvador](https://www.recetassalvador.com/) | Accessed on October 8, 2021. | Yes |
| `Eritrea.csv` | [196 Flavors](https://www.196flavors.com/category/continent/africa/east-africa/eritrea/) | Accessed on April 25, 2022. | Yes |
| `Estonia.csv` | [Povar](https://povar.ru/list/estonskaya/) | Accessed on July 3, 2022. | Yes |
| `Ethiopia.csv` | [Ethiopian cookbook](https://www.amazon.com/dp/B07W8BZPRR?tag=cuisinen04-20&linkCode=osi&th=1&psc=1) | Accessed on August 10, 2022. | Yes |
| `Fiji.csv` | [That Fiji Taste](https://thatfijitaste.com/) | Accessed on May 16, 2022. | Yes |
| `Finland.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,158/Europa-Finnland-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `France.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,84/Europa-Frankreich-Rezepte.html) | Accessed on January 19, 2022. | Yes |
| `Georgia.csv` | [Georgian cookbook](https://www.amazon.com/dp/B08WL4MXYP/ref=dp-kindle-redirect?_encoding=UTF8&btkr=1) | Accessed on July 13, 2022. | Yes |
| `Germany.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,65/Europa-Deutschland-Rezepte.html) | Accessed on January 18, 2022. | Yes |
| `Ghana.csv` | [Ghanaian cookbook](https://www.amazon.com/dp/B07SXRFRR1?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on April 23, 2022. | Yes |
| `Greece.csv` | [Chefkoch](http://chefkoch.de/) | Accessed on January 19, 2022. | Yes |
| `Guatemala.csv` | [Recetas Guatemala](https://www.recetas-guatemala.com/) | Accessed on October 8, 2021. | Yes |
| `Guinea.csv` | [Guinée Gourmande](https://www.guinee-gourmande.com/) | Accessed on May 16, 2022. | Yes |
| `Guyana.csv` | [Guyanese Style Cooking](https://www.amazon.com/Guyanese-Style-Cooking-Sazieda-Jabar-ebook/dp/B07957TQ8F/ref=tmm_kin_swatch_0?_encoding=UTF8&qid=&sr=) | Accessed on June 22, 2022. | Yes |
| `Haiti.csv` | [Haitian Recipes](https://haitian-recipes.com/recipes/) | Accessed on May 16, 2022. | Yes |
| `Honduras.csv` | [Recetas Honduras](https://www.recetashonduras.com/) | Accessed on October 8, 2021. | Yes |
| `Hungary.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,85,86/Europa-Ungarn-Osteuropa-Rezepte.html) | Accessed on January 24, 2022. | Yes |
| `Iceland.csv` | [Food.com](https://www.food.com/topic/icelandic) | Accessed on April 26, 2022. | Yes |
| `India.csv` | [Archana's Kitchen](https://www.archanaskitchen.com/recipes) | Accessed on April 30, 2022. | Yes |
| `Indonesia.csv` | [Resep Koki](http://resepkoki.id/) | Accessed on November 9, 2021. | Yes |
| `Iran.csv` | [The Persian Pot](http://www.thepersianpot.com/) | Accessed on June 22, 2022. | Yes |
| `Iraq.csv` | [Atyab Tabkha](http://atyabtabkha.com/) | Accessed on July 3, 2022. | Yes |
| `Ireland.csv` | [Delish](https://www.delish.com/) | Accessed on April 25, 2022. | Yes |
| `Israel.csv` | [Walla Food](http://food.walla.co.il/) | Accessed on July 3, 2022. | Yes |
| `Italy.csv` | [GialloZafferano](https://www.giallozafferano.com/latest-recipes/) | Accessed on October 8, 2021. | Yes |
| `Jamaica.csv` | [Jamaican Foods and Recipes](https://jamaicanfoodsandrecipes.com/) | Accessed on May 16, 2022. | Yes |
| `Japan.csv` | [Delish Kitchen](https://delishkitchen.tv/) | Accessed on July 3, 2022. | Yes |
| `Jordan.csv` | [Ultimate Jordanian Cookbook](https://www.amazon.com/Ultimate-Jordanian-Cookbook-Dishes-Cuisines-ebook/dp/B09J8SDLHJ) | Accessed on July 4, 2022. | Yes |
| `Kazakhstan.csv` | [Russian Food](https://www.russianfood.com/recipes/bytype/?fid=130) | Accessed on July 3, 2022. | Yes |
| `Kenya.csv` | [FAO Kenyan recipes](https://www.fao.org/3/i9056en/I9056EN.pdf) | Accessed on April 14, 2022. | Yes |
| `Kosovo.csv` | [Balkan Lunch Box](https://balkanlunchbox.com/category/country/kosovo-recipes/) | Accessed on May 9, 2022. | Yes |
| `Kuwait.csv` | [Kuwaiti cookbook](https://www.amazon.com/dp/B091GGBWJP/ref=dp-kindle-redirect?_encoding=UTF8&btkr=1) | Accessed on June 7, 2023. | Yes |
| `Kyrgyzstan.csv` | [Russian Food](https://www.russianfood.com/recipes/bytype/?fid=173) | Accessed on July 6, 2022. | Yes |
| `Laos.csv` | [Lao-Style Recipes](https://www.amazon.com/Lao-Style-Recipes-Complete-Cookbook-ebook/dp/B07W14K879/ref=tmm_kin_swatch_0?_encoding=UTF8&qid=&sr=) | Accessed on June 7, 2023. | Yes |
| `Latvia.csv` | [Receptes](https://receptes.eu/cuisine/latviesu) | Accessed on May 9, 2022. | Yes |
| `Lebanon.csv` | [Feel Good Foodie](https://feelgoodfoodie.net/recipe/category/type/lebanese-inspired/) | Accessed on May 9, 2022. | Yes |
| `Liberia.csv` | [Clean Foodie Cravings](https://cleanfoodiecravings.com/category/recipe/) | Accessed on May 9, 2022. | Yes |
| `Libya.csv` | [Just Food](https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/%D8%A7%D9%84%D8%A8%D9%84%D8%AF/%D8%A7%D9%83%D9%84%D8%A7%D8%AA-%D9%84%D8%A8%D9%86%D8%A7%D9%86%D9%8A%D8%A9/50)| Accessed on May 17, 2022. | Yes |
| `Liechtenstein.csv` | [Alpine Cookbook](https://www.dropbox.com/s/icxdiexj6fdf2rf/Alpine%20cookbook%20%20comfort%20food%20from%20the%20mountains%20%28Bingemer%2C%20Susanna%20Gerlach%2C%20Hans%20Knezevic%20etc.%29%20%28z-lib.org%29.pdf?dl=0) | Accessed on June 6, 2023. | Yes |
| `Lithuania.csv` | [La Maistas](https://www.lamaistas.lt/virtuve/lietuvos-virtuve) | Accessed on May 9, 2022. | Yes |
| `Luxembourg.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,161/Europa-Luxemburg-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Madagascar.csv` | [Recettes de Madagascar](https://recettes.de/madagascar) | Accessed on July 3, 2022. | Yes |
| `Malaysia.csv` | [Resepi Che Nom](http://resepichenom.com/) | Accessed on December 15, 2021. | Yes |
| `Maldives.csv` | [Maldives Cook](https://maldivescook.com/) | Accessed on July 3, 2022. | Yes |
| `Malta.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,167/Europa-Malta-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Mauritius.csv` | [Mauritian Food Recipes](https://mauritianfoodrecipes.com/all-recipes/) | Accessed on May 9, 2022. | Yes |
| `Mexico.csv` | [La Cocina Mexicana](https://www.la-cocina-mexicana.com/) | Accessed on October 8, 2021. | Yes |
| `Moldova.csv` | [1000.menu](https://1000.menu/catalog/moldavskaya-kuxnya) | Accessed on July 3, 2022. | Yes |
| `Mongolia.csv` | [Easy Mongolian Cookbook](https://www.amazon.com/Easy-Mongolian-Cookbook-Authentic-Delicious-ebook/dp/B07WRM6BW8/ref=tmm_kin_swatch_0?_encoding=UTF8&qid=&sr=) | Accessed on June 22, 2022. | Yes |
| `Morocco.csv` | [BBC Good Food](https://www.bbcgoodfood.com/recipes/collection/moroccan-recipes) | Accessed on May 10, 2022. | Yes |
| `Mozambique.csv` | [SBS Food](https://www.sbs.com.au/food/cuisine/mozambican) | Accessed on May 10, 2022. | Yes |
| `Myanmar.csv` | [SBS Food](https://www.sbs.com.au/food/cuisine/myanmar) | Accessed on May 10, 2022. | Yes |
| `Namibia.csv` | [Kochbar](https://www.kochbar.de/kochen/namibisch-kochen-namibische-kueche.html) | Accessed on May 6, 2022. | Yes |
| `Nepal.csv` | [Food.com](https://www.food.com/topic/nepalese) | Accessed on April 26, 2022. | Yes |
| `Netherlands.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,1076/Europa-Niederlande-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `New Zealand.csv` | [Food.com](https://www.food.com/topic/new-zealand) | Accessed on July 3, 2022. | Yes |
| `Nicaragua.csv` | [Recetas Nicaragua](https://www.recetas-nicaragua.com/) | Accessed on October 8, 2021. | Yes |
| `Niger.csv` | [Recettes du Niger](https://recettes.de/niger) | Accessed on July 3, 2022. | Yes |
| `North Korea.csv` | [North Korean Recipes](https://www.dropbox.com/s/sjl4mrwu6eqy806/North%20Korean%20Recipes%20A%20Complete%20Cookbook%20of%20Down-Home%20Dish%20Ideas%20%28Anthony%20Boundy%29%20%EF%BC%88Englishrise%29.pdf?dl=0) | Accessed on April 25, 2022. | Yes |
| `Norway.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,133,160/Europa-Skandinavien-Norwegen-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Pakistan.csv` | [Pakistan Eats](https://www.pakistaneats.com/recipe-index/) | Accessed on May 6, 2022. | Yes |
| `Panama.csv` | [Recetas Panama](https://www.recetaspanama.com/) | Accessed on October 8, 2021. | Yes |
| `Paraguay.csv` | [Recetas Paraguay](https://www.recetasparaguay.com/) | Accessed on October 8, 2021. | Yes |
| `Peru.csv` | [Comida Peruana](https://www.comida-peruana.com/) | Accessed on October 8, 2021. | Yes |
| `Philippines.csv` | [Panlasang Pinoy](http://panlasangpinoy.com/) | Accessed on December 20, 2021. | Yes |
| `Poland.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,86,125/Europa-Osteuropa-Polen-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Portugal.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,149/Europa-Portugal-Rezepte.html) | Accessed on January 24, 2022. | Yes |
| `Romania.csv` | [Savori Urbane](https://savoriurbane.com/lista-retete-de-la-a-la-z/) | Accessed on July 3, 2022. | Yes |
| `Russia.csv` | [Russian Food](http://russianfood.com/) | Accessed on July 4, 2022. | Yes |
| `Samoa.csv` | [Samoan cookbook](https://www.amazon.com/dp/B01EE4I6NU?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on July 4, 2022. | Yes |
| `Senegal.csv` | [Cuisine AZ](https://www.cuisineaz.com/cuisine-du-monde/senegal-p248) | Accessed on April 26, 2022. | Yes |
| `Serbia.csv` | [Ultimate Serbian Cookbook](https://www.amazon.com/Ultimate-Serbian-Cookbook-dishes-Balkan-ebook/dp/B088RJH2KY) | Accessed on July 13, 2022. | Yes |
| `Singapore.csv` | [My Singapore Food](http://mysingaporefood.com/recipes/) | Accessed on July 3, 2022. | Yes |
| `Slovakia.csv` | [Dobrú Chuť](https://dobruchut.aktuality.sk/recepty/79/slovenska-kuchyna/) | Accessed on April 26, 2022. | Yes |
| `Slovenia.csv` | [Anina Kuhinja](https://www.aninakuhinja.si/kategorija_receptov/slovenski-tradicionalni-recepti/) | Accessed on July 3, 2022. | Yes |
| `Solomon Islands.csv` | [Pacific Islands cookbook](https://www.amazon.com/dp/B01EE4I6NU?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on July 4, 2022. | Yes |
| `South Africa.csv` | [Food24](https://www.food24.com/south-african-recipes/) | Accessed on July 3, 2022. | Yes |
| `South Korea.csv` | [My Korean Kitchen](https://mykoreankitchen.com/recipes/) | Accessed on July 3, 2022. | Yes |
| `Spain.csv` | [Recetas de Rechupete](http://recetasderechupete.com/) | Accessed on December 16, 2021. | Yes |
| `Sri Lanka.csv` | [Top Sri Lankan Recipe](https://www.topsrilankanrecipe.com/) | Accessed on July 3, 2022. | Yes |
| `Sudan.csv` | [Food.com](https://www.food.com/topic/sudanese) | Accessed on April 26, 2022. | Yes |
| `Suriname.csv` | [Smulweb](https://www.smulweb.nl/recepten/surinaamse) | Accessed on April 26, 2022. | Yes |
| `Sweden.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,132,133/Europa-Schweden-Skandinavien-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `Switzerland.csv` | [Chefkoch](http://chefkoch.de/) | Accessed on January 19, 2022. | Yes |
| `Syria.csv` | [Atyab Tabkha](https://www.atyabtabkha.com/tag/%D8%A7%D9%84%D9%85%D8%B7%D8%A8%D8%AE-%D8%A7%D9%84%D8%B3%D9%88%D8%B1%D9%8A) | Accessed on July 3, 2022. | Yes |
| `Tajikistan.csv` | [Povar](https://povar.ru/list/tadzhikskaya/) | Accessed on July 3, 2022. | Yes |
| `Thailand.csv` | [Rasa Malaysia](https://rasamalaysia.com/recipes/thai-recipes/) | Accessed on April 25, 2022. | Yes |
| `Tonga.csv` | [Pacific Islands cookbook](https://www.amazon.com/dp/B01EE4I6NU?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on July 4, 2022. | Yes |
| `Tunisia.csv` | [196 Flavors](https://www.196flavors.com/category/continent/africa/north-africa/tunisia/) | Accessed on April 25, 2022. | Yes |
| `Turkey.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t103/Tuerkei-Rezepte.html) | Accessed on January 24, 2022. | Yes |
| `Turkmenistan.csv` | [Tagamlar](https://tagamlar.com/) | Accessed on July 3, 2022. | Yes |
| `Tuvalu.csv` | [Pacific Islands cookbook](https://www.amazon.com/dp/B01EE4I6NU?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on August 31, 2022. | Yes |
| `Ukraine.csv` | [Food Obozrevatel](http://food.obozrevatel.com/) | Accessed on July 3, 2022. | Yes |
| `United Arab Emirates.csv` | [UAE Recipes](https://www.amazon.com/Enticing-Exotic-UAE-Recipes-Excellent-ebook/dp/B08YNQN5C6/ref=tmm_kin_swatch_0?_encoding=UTF8&qid=&sr=) | Accessed on June 7, 2023. | Yes |
| `United Kingdom.csv` | [Chefkoch](https://www.chefkoch.de/rs/s0t29,117/Europa-Grossbritannien-Rezepte.html) | Accessed on January 23, 2022. | Yes |
| `United States.csv` | [BBC Good Food](https://www.bbcgoodfood.com/recipes/collection/american-recipes) | Accessed on April 25, 2022. | Yes |
| `Uruguay.csv` | [Cocina Uruguaya](https://www.cocina-uruguaya.com/) | Accessed on October 8, 2021. | Yes |
| `Uzbekistan.csv` | [Uzbek Travel Guide](https://uztravelguide.com/uzbek-cuisine/recipe-book) | Accessed on July 3, 2022. | Yes |
| `Vanuatu.csv` | [Pacific Islands cookbook](https://www.amazon.com/dp/B01EE4I6NU?tag=cuisinen04-20&linkCode=ogi&th=1&psc=1) | Accessed on July 4, 2022. | Yes |
| `Venezuela.csv` | [Recetas Venezolanas](https://www.recetas-venezolanas.com/) | Accessed on October 8, 2021. | Yes |
| `Vietnam.csv` | [Rasa Malaysia](https://rasamalaysia.com/recipes/vietnamese-recipes/) | Accessed on April 25, 2022. | Yes |
| `Zimbabwe.csv` | [ZimboKitchen](https://www.zimbokitchen.com/) | Accessed on July 3, 2022. | Yes |


## Instructions for Replicators

New users should follow these steps to run the package successfully:
- Users must first have access to all data files if they are not included in the reproducibility package. They should go to the mentioned links, download the listed files, and place them in the data folder.
- Update the following files with your directory paths

  - `main_dofile.do`
- Ensure all required software and dependencies are installed as listed in the [Requirements](#requirements) section.

- Run the `main_dofile.do` file.

## List of Exhibits

Clearly identify and document the tables and figures as they appear in the manuscript by their corresponding numbers. If file names do not correspond to exhibit numbers, provide detailed explanations.

If not all data is provided in the reproducibility package, as described in the data section, then the list of tables should clearly indicate which tables, figures, and in-text numbers can be reproduced with the public material provided.

Example template for exhibit identification:

The provided code reproduces:

- [ ] All numbers provided in text in the paper
- [ ] All tables and figures in the paper
- [ ] Selected tables and figures in the paper, as explained and justified below

| Exhibit name | Output filename | Script | Note |
|--------------|-----------------|--------|------|
| Figure I | map_ancestral_vs_cookpad.png | | |
| Table I | summary_table_recipe.tex, descriptive_gender.tex | | |
| Table II | reg_index_ols_1_cook.tex, reg_index_ols_2_cook.tex, reg_index_ols_0_cook.tex, reg_index_ols_3_cook.tex | | |
| Table III | reg_index_iv_1_cook.tex, reg_index_iv_2_cook.tex, reg_index_iv_0_cook.tex, reg_index_iv_3_cook.tex | | |
| Table IV | rfulltime_index_iv_1_cook.tex, rfulltime_index_iv_2_cook.tex, rfullemployee_index_iv_1_cook.tex, rfullemployee_index_iv_2_cook.tex | | |
| Table V | rmeals_index_iv_2_cook.tex, rmeals_index_iv_3_cook.tex, rspousecook_index_iv_2_cook.tex, rspousecook_index_iv_3_cook.tex | | |
| Figure B1 | binscatter_female_learning.png | | |
| Table B1 | | | |
| Table B2 | reg_index_fs_1_cook.tex, reg_index_fs_2_cook.tex, reg_index_fs_0_cook.tex, reg_index_fs_3_cook.tex | | |
| Table B3 | reg_index_iv_1_cook_robust.tex, reg_index_iv_2_cook_robust.tex, reg_index_iv_0_cook_robust.tex, reg_index_iv_3_cook_robust.tex | | |
| Table B4 | reg_index_fs_1_cook_robust.tex, reg_index_fs_2_cook_robust.tex, reg_index_fs_0_cook_robust.tex, reg_index_fs_3_cook_robust.tex | | |
| Table B5 | reg_index_iv_1_cook_24_55.tex, reg_index_iv_2_cook_24_55.tex, reg_index_iv_0_cook_24_55.tex, reg_index_iv_3_cook_24_55.tex | | |
| Table B6 | reg_index_ols_gap_5_cook.tex, reg_index_ols_gap_4_cook.tex | | |

## Requirements

### Computational Requirements

In this section, specify operating system requirements, software dependencies, environment setup instructions, and any other relevant information essential for replicating the results. Each of these factors plays an important role in ensuring successful replication.

### Software Requirements

List all software requirements, including versions, dependencies, libraries, environment setup, and packages installed. Using different versions of the same software could lead to variations in results. If multiple software are used, include details for all.

Example:

- **Stata version 15**

  - estout
  
  - rdrobust
  
- **Python 3.6.4**

  - pandas 0.24.2
  
  - numpy 1.16.4

### Memory and Runtime and Storage Requirements

Provide consistent information about memory resources for reliable computation. Include runtime information for replicators to assess processing times and detect potential issues with the code. It would be best to describe how much storage is required in addition to the space visible in the typical repository, for instance, because data will be unzipped, data downloaded, or temporary files written.

## Code Description 

Give an overview of the program files and their purposes. Remove redundant or obsolete files from the replication archive. For example, main.do sets file paths, installs necessary ADO packages, and executes all other dofiles. Meanwhile, cleaning.do loads data, handles missing values, and analysis.do performs basic statistical analysis and generate visualizations. 

Make sure to also include any crucial information that replicators should be aware of to facilitate a one-click run of the code.

## Folder Structure

Details about folder structure are crucial because a well-organized layout enables replicators to navigate quickly to the desired files or directories without searching through cluttered or disorganized folders. Include only the files necessary for replication and delete any unnecessary files.

An ideal folder structure for a reproducibility package should look something like this:

```
Data
  ├── Raw
  └── Cleaned
Code
  ├── Main_dofile.do
  ├── 01_cleaning.do
  └── 02_analysis.do
Outputs
  ├── Main
  │   ├── Tables
  │   └── Figures
  └── Annex
      ├── Tables
      └── Manuscript
```
