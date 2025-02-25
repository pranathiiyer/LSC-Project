# Final Project: Retail Investor Sentiment and the S&P 500
Group Members: Val Alvern, Thiyaghessan, Pranathi Iyer, Allison Towey

# Project Scope
In recent years, the emergence of fintech applications like Robinhood have given retail investors with expanded access to the stock market. This has caused an explosion in day trading, with numerous small investors allocating increasing amounts of capital to the stock market. These investors used platforms such as reddit to share research and discuss trading strategies. One such subreddit r/wallstreetbets soon became the most popular forum, featuring millions of users (Aharon et al, 2021). 

In early 2021, members of r/wallstreetbets observed that several hedge funds were holding large short positions against GameStop Corp, a consumer electronics and video game retailer. This meant that these financial firms were betting that the stock price would go down and these bets were exerting downward pressure on GameStop's stock price. Retail traders on r/wallstreetbets felt that this was an unfair evaluation of GameStop's business model. Several users figured out that if they drove the price of the stock up by buying shares in it, the hedge funds shorting Gamestop would be forced to pay up for their bets thus creating a feedback loop of upward price pressure. Through a combination of memes and detailed reddit discussions, millions of r/wallstreebets users simultaneously promoted and executed this strategy. The results were successful and came as a shock to institutional actors who had long dismissed the effect retail investors had on the market (Hasso et al, 2022).

To better understand the influence ordinary investors have on the stock market currently, this research project explores the sentiment of posts within r/wallstreetbets to determine if it correlates with shifts in the S&P 500. We selected r/wallstreetbets due to its large userbase of over 12 million members and proximity to recent stock market activity as illustrated by the GameStop short squeeze. Our project scrapes the 100 most popular posts each day over a period of one year. We chose data from the past year to evaluate the subreddit in the post-Gamestop era (Umar et al, 2021). 

We then host our scraped data on an API for other researchers to access it. For our analysis, we perform sentiment analysis on the text of each post before correlating it with the closing price and changes in the S&P500. Additionally, we also implement an LDA topic modelling algorithm to identify possible themes that guide investor sentiment. Finally, we generate interactive Holoviews/Bokeh plots to capture this information.

Answering this question has important implications for current scholarship on behavioural economics and behavioural finance. It provides insight into how the manifest emotions of day traders can exert an influence on markets. Additionally, it also provides a measure of the magnitude of this influence. Beyond its findings, this project offers scholars with a repository of reddit posts from r/wallstreetbets and a parallelized framework to use when analyzing the data. For example, the scraper can be used to retrieve posts across a longer time frame for an extended analysis.

# Scraping Posts From r/wallstreetbets
I scrape posts from reddit using the Pushift Reddit API that provides users with full functionality for parsing through reddit submissions and comments. Our timeframe for scraping spans 370 days which requires our scraper to access data from 370 unique Pushift URLs. Each API call returns data from about 100 posts in a JSON format, resulting in over 37,000 records for our scraper to parsethrough. A serial implementation is likely to take an excessive amount of time. Thus, I implement an embarassingly parallel solution using a stepfunction to split a batch of urls across 10 lambda workers. Each worker then iterates through its allocated portion of reddit posts and extracts those which possess a body of text valid for sentiment analysis. The data collected from each reddit post is its url, author, user-defined category, text of post, popularity, number of comments and number of upvotes.

The data is stored in an AWS RDS. I chose an RDS because I also want to host the contents of the dataset with a Flask API. RDS are most suited for performing multiple small and fast queries. Hence, multiple users can open connections with the database to read in the necessary rows. RDS makes this possible through its prioritization of consistency. Aside from RDS, I also output the results into a csv file which I then upload to an S3 bucket for the rest of the team to access.

My scraper ends up returning about 10,000 posts. This means that over 27,000 potential posts were not scraped because they did not containt text. Their content could come in the form of videos or images. Although our earlier proposal wanted to perform an image analysis of the images used, our findings did not reveal anything particularly interesting. Thus we switched to analysing the text content instead. Each of these posts contain a large amount of text sometimes spanning thousands of words resulting in a fairly large corpus that would be time-consuming to analyse via serial computation methods. Due to size constraints we could not upload the csv file here but have left the RDS up and running if you'd like to parse through it. 

Although the scrapers only returned 10,000 valid posts our code should not have an issue scraping larger volumes of data. All that is required is for the user to change the date range in the jupyter notebook. Our analytical workflows should also not have a problem scaling up to accomodate a larger volume of data. 

Jupter Notebook for scraping: [LSC_Final_Project_Scraper.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Final_Project_Scraper.ipynb) <br>
Lambda Function for scraping: [wsb_lambda.py](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/wsb_lambda.py) <br>
Step Function for scraping: [wsb_sfn.py](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/wsb_sfn.py) <br>

# Hosting RDS Using Flask API
After storing the relevant data, I create an API using Flask and host it using an AWS EBS Cluster. Detailed instructions for accessing the API are provided in the attached notebooks. The aim of making the dataset accessible via API is to provide other researchers with a  means of working with relevant subsections of our data. For example, our API allows a user to index rows by date, author or category. This provides an easy format for other researchers to navigate r/wallstreetbets posts that contain text in their body. Our scraper has already filtered out non-text posts and deleted posts so the results from our dataset are much cleaner than the results from the Reddit API. Instructions on how to use the API can be found on its homepage using the index.html template. Although I have terminated the EBS cluster the code used is available in this repository.

Python Script for API: [LSC_Final_Project_API.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Final_Project_API.py) <br>
Zip File for AWS EBS: [LSC_Final_Project_API.zip](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Final_Project_API.zip) <br>

![LSC_Final_Project_API_ss.png](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Final_Project_API_ss.png)

# Topic Modelling
We perform LDA topic modelling on the data to identify the core themes that guide the evolution of the subreddit and potentially reveal drivers of retail investor sentiment. To implement this algorithm we use Pyspark NLP in an AWS EMR cluster that performs topic modelling on a series of unigrams and trigrams. We also use POS tagging to filter out uninformative sequences of words before fitting the topic model on the combined set of unigrams and trigrams. Our POS tagger uses a pretrained neural network to identify tags.

The results of the topic models largely reference various market activites relevant to the buying and selling of stock. The most interesting topic is topic 6 with words like "elon", "buy", "uranium" and "shib". "Shib" references the Shiba Inu, the dog that is the face of Doge Coin. This coupled with the mentioning of Elon Musk and the nonsensical use of uranium (It is not accessible as a commodity to be traded) suggests that there is a possible strong element of humour amongst users of the subreddit. This is inline with qualitative explorations of r/wallstreetbets where users often create posts as a form of satire.

Additionally, there are also several clear favourite stock picks amongst users such as "gme" (Gamestop) and blackberry. The former reveals that the early events of 2021 continue to exert an influence on discourse within the subreddit. The latter suggests that users on the forumn do promote specific companies and this could be a part of efforts to inflate the share price of certain companies. The success of these efforts can be evaluated in further research.

The fact that the rest of the topics center around market activities also suggests that retail traders are as capable of performing dedicated research as their institutional counterparts. A common criticism of retail investors by financial institutions is their relative unsophistication and irrationality. However, our results suggest that retail traders do use the approrpriate vocabulary when discussing the markets and are focused on valid metrics. This does call into question assumptions of incompetence institutional actors and scholars have often held when studying retail investors. The results are shown below: <br>
![Final_Project_LDA.png](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/Final_Project_LDA.png)

Pyspark Notebook for Topic Modelling: [LSC_Final_Project_LDA.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Final_Project_LDA.ipynb) <br>

# Sentiment Analysis
We implement a sentiment analysis model from John Snow labs to facilitate further statistical analysis of the individual reddit posts. The model in question was a pre-trained BERT model, first trained on a wikipedia corpus before then being fine-tuned to identify sentiment in financial statements. Specifically, the encodings are sentence embeddings from the Bert model. After importing the scraped data from Thiya's S3 bucket, we isolate the 'text' column in the csv before preprocessing the text, removing URLs, long strings of numbers and special characters. 

![Post Processed Text.png](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/Post%20processed%20text.png) 

In the process of preprocessing, one data point was removed. Thus, we had to remove the corresponding datapoint in the original dataframe to be able to easily match each result to its date. The preprocessed text is then put through the sentiment analysis model. The results from the model is then concatenated with the corresponding date to facilitate the time-series statistical analysis by Pranathi. 

![Model Output](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/BERT%20Output.png)

The final dataframe is then saved onto an S3 bucket for future use. 

![Final Dataframe](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/final_df.png)

PySpark Notebook for Sentiment Analysis: [LSC Project Seniment Classification](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSCProject_sentiment_classification.ipynb)

# Statistical Analysis 
Once having classified sentiments for each post over the year, we collect data for the performace of the S&P Index over the past year from NASDAQ--which has structured historical data of the index. We then use this data and the sentiment of the posts to see if one of them can be used to extrapolate information about the other. Our objective of doing this was to see if and how sentiment of posts of reddit are reflective of real world phenomena in the financial world. A snapshot of the data can be seen below. <br>

![S&P data.png](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/S%26P%20data.png)

We then calculate day-wise change in the index and analyze how this change and the daily closing value of the index are correlated with the average sentiments of the posts per day. While we used dask (with 1 worker) to compute the correlation, we were unable to successfully install scipy using the bootstrap script for launching dask on the EMR cluster, to calculate the significance of the correlations. We therefore used Spark to calculate the p-value of the correlations between the above mentioned fields.

Our results show that while a significant correlation between average sentiment and daily change does not exist, a significant but weak correlation of .14 exists between the closing value of an index on a day and its sentiment. This is not surprising because the closing value of a day is likely to influence the sentiment of the next day if at all, and not so much the same day. This lag effect is potentially not captured by correlation. Moreover, the figure below shows that average sentiment varies much more dynamically as compared to the daily change of the index. This corraborates our finding that there does not seem to exist a significant relation between the two.

![S&P change and sentiment.png](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/S%26P%20change%20and%20sentiment.jpeg)

Finally, in order to account for the lag and lead effect that correlation could not capture, we perform granger's causality test between day-wise change in the index and average sentiment, and daily closing value and average sentiment. We only find a significant predictive relationship between closing value and the average sentiment, with a lag of 1. This means that just the previous day's value (lag = 1) is enough to predict the average sentiment of the posts on WSB the next day. This intuitively makes sense because the discourse and discussion on reddit the day after market closes, could be influenced by the previous day's performance. Of course, larger data and more robust analysis is required to make any claims of this kind with high confidence.

We had to calculate granger-causality locally because we were unable to install statsmodels onto dask using the EMR script, and statsmodels was not compatible with Spark either. However, we felt that understanding causality was an important aspect of this time series analysis, and hence performed the test locally.

The code for corrlelation and causality tests can be found at [LSCProj_Stat_AnalysisPt1.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSCProject_Stat_AnalysisPt1.ipynb), [LSC_Stat_Analysispt1_dask.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSC_Stat_Analysispt1_dask.ipynb)  and [LSCProj_Stat_AnalysisPt2.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/LSCProject_Stat_AnalysisPt2.ipynb) respectively. 

# Creation of Interactive Plots (Allison)
After collecting the meta data and sentiment data from the scraped posts, we are able to visualize the data using Holviews and Bokeh. First, to preprocess the data, we upload the data as a Dask Dataframe and ensure that the datatypes for the variables are correct, changing the 'date' variable to datetime64 and the 'class' variable (denoting the sentiment classification of positve, neutral, and negative) as a categorical variable. We then are able to create classification category dummy variables. Next, we create a function to code the sentiment classifications into integers, with positive being 1, negative beign -1, and neutral being 0.


After these preprocessing steps, we are able to plot the data using Holoviews Bars, Curve, and Scatter as necessary. For the first plot, we compare the number of posts in each sentiment category by summing the dummy variable sentiment categories and using hv.Bars.

![bokeh_plot (11)](https://user-images.githubusercontent.com/89881145/171908292-8453a91d-573b-4452-b809-8d1341378d2b.png)

We then can use hv.Curve to plot a time series line graph of the percentage of posts in each setniment category by day. We do so by grouping by day and taking the mean. For legibility purposes, we can smooth the data using a rolling window of 3 in the Dask Dataframe.
![bokeh_plot (12)](https://user-images.githubusercontent.com/89881145/171908771-aac9a2e0-1c3d-4176-8e1d-4ed69cfeda48.png)

To analyze these results using the metadata captured, we first concatenate the metadata and sentiment dask dataframes. Then, we define a function that aggregates the count of posts and average sentiment score for the column specified into a dataframe, grouping by the column name and aggregating count by sum and sentiment score by mean.

First, we create a dataframe aggreagated by date, ensuring that the datatype remains datetime64. After aggregating the data, we can see the number of posts per date and the average sentiment per date. We can graph these features using hv.Curve, smoothing using a rolling window of 3.
![bokeh_plot (17)](https://user-images.githubusercontent.com/89881145/171910050-912e9df0-6b92-4ea6-98fb-47b9f96f79b1.png)
![bokeh_plot (18)](https://user-images.githubusercontent.com/89881145/171910115-fea2b230-202c-4a29-8854-62cf1b252df2.png)


We create another dask dataframe for the metadata variable "category". After sorting the new dataframe from most negative to most positive average sentiment per category, we use hv.Bars to visualize this data.
![bokeh_plot (19)](https://user-images.githubusercontent.com/89881145/171937426-7e6c6f1d-5a2e-4bf1-b74b-8236436f54f6.png)


Also using this category-aggregated dask dataframe, we can plot the number of posts per category using hv.Bars.
![bokeh_plot (20)](https://user-images.githubusercontent.com/89881145/171937475-bb03561b-5dd2-42c9-85b2-b5fadb5853ba.png)


Finally, another metadata category we can visualize is the authors. We create an author-aggregated dask dataframe using the function defined previously, then subset the data by nlargest to get the top 10 authors by count of posts. Using hv.Bars, we can then visualize the average sentiment score for these top 10 authors.
![bokeh_plot (16)](https://user-images.githubusercontent.com/89881145/171909734-a8839a91-75de-4440-8855-42e28c6de0d8.png)

The code for these plots is available here: [Visualization.ipynb](https://github.com/lsc4ss-s22/final-project-wsb/blob/main/Visualization.ipynb)

Please note, the interactive bokeh plots do not render in the github viewer due to a quirk in the upload process. The PNGs in the Visualization_PNG folders are static versions of these plots. 

# Plot Interpretation
Our time-series analysis of user sentiment shows a large spike in positive sentiment on November 2021. It is unclear why this spike occurred although a likely explanation is renewed interest in self-described "meme stocks" such as GME and AMC. We can also see that over time the number of posts has increased but the average sentiment expressed has decreased. This indicates that as the subreddit has become more popular more neutral users have joined in. Initial optimism could thus be a product of self selection as the most optimistic individuals are more willing to engage earlier, with their gains drawing in a larger crowd that is more representative of the general population.

Split by category we can also see that "DD" or Due Diligence type posts are some of the most bullish, whilst companies like Palantir are rated negatively by users. These results could be used to infer biases in favor of certain companies. Interestingly the category with the highest sentiment is Charts, which indicates that visual mediums are primarily being used to convey positive messages. These could come in the form of promoting stock from a particular company, with appealing visuals used to entice audience members. 

Finally, most of the popular authors seem to be neutral in their coverage and thus more measured in their analysis. This could explain their popularity. The next most popular sentiment type is negative, with 3 of the most popular authors having a negative average sentiment. This could mean that more critical perspectives are valued on the subreddit as well, as a counter to the at-times overly exuberant messaging.

# Bibiliography
Aharon, D. Y., Kizys, R., Umar, Z., & Zaremba, A. (2021). Did David win a battle or the war against Goliath? Dynamic return and volatility connectedness between the GameStop stock and the high short interest indices. Dynamic Return and Volatility Connectedness between the GameStop Stock and the High Short Interest Indices (February 18, 2021).

Hasso, T., Müller, D., Pelster, M., & Warkulat, S. (2022). Who participated in the GameStop frenzy? Evidence from brokerage accounts. Finance Research Letters, 45, 102140.

Umar, Z., Gubareva, M., Yousaf, I., & Ali, S. (2021). A tale of company fundamentals vs sentiment driven pricing: The case of GameStop. Journal of Behavioral and Experimental Finance, 30, 100501.
