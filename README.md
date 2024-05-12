# Web scraping project for market prices
Web scraping project for getting market datas for inflation rate analysis.
<br /><br />

Project created with python web scraping library scrapy and its integration with web automation library playwright. In this project scrapy-playwright have used to get dynamically loaded content and execute javascript.

## Spiders & Websites
This project contains different spiders for different market websites.
<br/>Spider names can be listed as
- sokmarket ([şok market](https://www.sokmarket.com.tr)) 
- carrefour ([carrefoursa](https://www.carrefoursa.com))
- mopas ([mopaş](https://www.mopas.com.tr))
- marketpaketi ([marketpaketi](https://www.marketpaketi.com.tr))

The scraped data is stored in .csv files and the current date as their names.
## Data Format
The data is then formatted in a specific way so that it can be easily analyzed, accessed and scaled.

|        main_category 	        |        sub_category 	        |         lowest_category 	          |        name 	        |            price 	            |                  high_price 	                  |             in_stock 	             |   product_link 	    |                  page_link                  |              date              |
|:-----------------------------:|:----------------------------:|:----------------------------------:|:--------------------:|:-----------------------------:|:----------------------------------------------:|:----------------------------------:|:-------------------:|:-------------------------------------------:|:------------------------------:|
| main category of the product  | sub category of the product  | lowest sub category of the product | name of the product  | current price of the product  | high price of the product if it is discounted  | stock availability of the product  | URL of the product  | URL of the category page that product is on | date that product was scraped  |
|               	               |              	               |                 	                  |          	           |               	               |                       	                        |                 	                  |          	          |                      	                      |               	                |
|               	               |              	               |                 	                  |          	           |               	               |                       	                        |                 	                  |          	          |                      	                      |               	                |
## Setting Up The Environment
### Clone the repo to your local
```
$ git clone https://github.com/erayalp808/scraping-market-data.git
```
### Go to project directory
```
$ cd scraping-market-data
```
### Create and activate a virtual environment
<span style="color: grey;">To ensure that the needed Python packages do not corrupt the Python packages in your local area</span>
```
$ virtualenv venv
$ source venv/bin/activate
```
### Install the needed Python packages
```
(venv) $ pip install -r requirements.txt
```

### Install the required browsers for playwright
```
playwright install
```

### Run the spiders
```
scrapy crawl <spider name>
```