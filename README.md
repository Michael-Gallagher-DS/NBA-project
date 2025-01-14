# NBA-project

## NBA Stats GUI
Designed a GUI for NBA player statistics using Python and the nba-api library. The application presents comprehensive player data and game logs in a clean, intuitive design inspired by leading sport platforms. The tool provides advanced metrics and insights tailored for making improved betting decisions. 

## NBA Scoring Predication Models
Implemented Random Forest and Gradient Boosting regression models using scikit-learn to predict points scored by NBA players. The workflow involves two key steps:
1. Extracting a list of the top 200 scorers for the current NBA season, aggregating their statistics across multiple seasons then enriching the aggregated dataset with custom features. 
2. In the last stage of processing, the target variable (what we are looking to predict, in this case, points scored) is identified and stored, and any irrelevant features are removed from the dataset.  Lastly, the dataset is split into training and testing sets. Finally, both models are fitted and evaluated for accuracy using MAE, R^2 and other metrics.
