# Machine Learning to Predict Rent Prices in Regina using Data Scraped off Kijiji

I scraped 800 rent listings off Kijiji, which due to malformatted data or missing crucial information (such as the prices and rent size), I only used about 600 listings. I did this to train a machine learning model to predict rent prices in Regina to quickly calculate the profitability of all real estate listings in Regina on Realtor.

Of the data I had, I first visualized the data with histograms and pie charts using the Matplotlib Python library, and via a map using the Google Maps API to help with cleaning the data as well as better understanding the data. One conclusion I drew for example was that the rent price was significantly higher around downtown and one neighboorhood around the Lifelab.

After, I one-hot encoded all categorical data and proceeded with using a random forest regressor model to predict the rent price with over 30 features. After adjusting some of the data and hyperparameter tuning using SKLearn on Jupyter notebooks, I attained a mean accuracy of 90%!

In the future, I may try logistical regressive algorithms and collect more data from other sites such as rentfaster.ca to improve my model. 
