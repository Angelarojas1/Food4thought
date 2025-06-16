# Homecare burden and female labor force participation
## Code 

Introduction
In this paper we look at data for 139 countries to find the relationship between homecare burden and female labor force participation.
| Code                                   | Description |
|----------------------------------------|-------------|
| 1_merge_recipes                       | Merges countrywise recipe datasets |
| 1stage_verification                   | In this code we run 1stage regressions in multiple ways |
| 2_cuisine_variables                   | This dofile organizes time, ingredients and spices variables |
| 3_flfp_clean                          | Cleans female labourforce participation dataset |
| 4_distance_clean                      | This dofile calculate distance between any two countries in the world using their capitals |
| 5_ciat_clean                          | This dofile merges recipe, region, country dataset |
| 6_suitability_clean                   | This dofile create suitability data for all ingredients |
| 7_common_flavor                       | This dofile creates common flavor files |
| 8_versatility_clean_v2                | This dofile creates files to generate versatility variables |
| 9_native_versatility                  | This dofile creates native versatility files |
| 10_imported_versatility_v2            | This dofile creates imported versatility files |
| 11_geographical_clean                 | This dofile cleans greographical control data |
| 12_cookpad_clean                      | This dofile cleans cookpad database |
| 13_FAO_suitability                    | This dofile cleans FAO information |
| 14_time_use_survey                    | This file merges country recipe dataset |
| 15_cuisine_flfp_rawcorr               | This dofile shows raw correlations of FLFP and cuisine complexity |
| 16_cookpad_flfp_cuisine_reg           | This dofile runs regressions using Cookpad, FLFP and cuisine variables |
| 17_1ststage_best                      | This dofile gets regressions results to identify most accurate one |
| 18_merge_reg                          | This dofile merges all datasets for analysis |
| 19_IV_reg                             | This dofile runs 1st stage, IV and OLS regressions |
| 20_1stage_best_cookpad                | This dofile runs regressions on cookpad data to identify the best one |
| 20_1stage_best_cookpad_1              | This dofile runs regressions on cookpad data to identify the best one |
| 20_1stage_best_cookpad_country_1      | This dofile runs regressions on cookpad data to identify the best one |
| 20_1stage_best_cookpad_country_v2_1   | This dofile runs regressions on cookpad data to identify the best one |
| 20_1stage_best_cookpad_v2_1           | This dofile runs regressions on cookpad data to identify the best one |
| 21_merge_reg_cookpad                  | This dofile merges all databases for analysis |
| 22_cookpad_reg                        | Cookpad regressions for time, spices and ingredients |
| all_regressions_verification          | In this code we run all regressions (1stage, IV, MCO, reduce form) |
| checking_data                         | In this code we are identifying problems in the data |
| 32_composite_versatility_calculation     | Calculating versatility of native-native, native-imported and imported-imported pairs of ingredients |
| cuisine_histograms                    | Exploring recipe data |
| FirstStage_NewVersatility             | First stage results for all different versions of versatility |
| 33_new_versatility_adjWeights            | New (composite) versatility calculation using relative weights |
| 31_old_versatility_calculation_FIXED     | Fixed suitability in old versatility calculation |
| population_clean                      | Cleans population data |
| scatter_ver_time_pop                  | In this code we create scatters x axis is versatility and y axis is time |
| 30_winsorze_totaltime                    | Winsorizing time, ingredients and spices to 99th percentile |
| wvs_data                              | Get gender norms persistence data |
| 34_new_versatility_including_native   | Versatility for native and imported ingredients weighted by suitability |
| 35_cookpad_data                       | Generates cookpad dataset and creates an indicator for cookpad in versatility data |
| 36_cookpad_analysis                   | Regressions of cookpad outcomes on gender data clustered by country  |
| 37_FirstStage_versatility_dataset     | Generates a dataset for versatility first stage regressions  |
| 38_FirstStage_versatility_analysis    | Regressions for testing versatility as an instrument  |


