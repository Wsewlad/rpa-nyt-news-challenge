# Solution for Automating News Data Extraction from NYTimes

This project provides an automation solution for extracting news data from the NYTimes website. It automates the process of searching for news articles based on a given search phrase, applying filters for news categories or sections, and retrieving relevant information such as title, date, description, and image. The data is then stored in an Excel file for further analysis.

## Configuration
Before running the automation, make sure to configure the following variables:

- `Search Phrase`: Specify the search phrase to retrieve relevant news articles.
- `News Category` and/or `Section`: Choose the desired news category or section to filter the search results.
- `Number of Months`: Set the number of months for which you want to retrieve news articles. This determines the time period to search within.

These variables can be configured either through a configuration file or using the Robocorp Cloud Work Items feature.

Example:
```json
{
  "search_phrase": "Ukraine",
  "categories": [
      "Article",
      "Audio",
      "Image Slideshow",
      "Something"
  ],
  "sections": [
      "Opinion"
  ],
  "number_of_month": 0
}
```
> ⚠️ Limitations of Robocorp Cloud Free Plan
Please note that the Robocorp Cloud Free Plan has certain limitations that you need to consider when executing longer processes. One important limitation is the maximum allowed execution time for a single step, which is set to 180 seconds (3 minutes). If a step exceeds this time limit, it will result in a timeout error and the process will be terminated.

> To ensure successful execution within the provided time constraints, it is crucial to carefully consider the input parameters and optimize the automation process accordingly.

## Execution

During execution, the automation will perform the following steps:

- Open the NYTimes website.
- Enter the specified search phrase in the search field.
- Apply the chosen filters for news categories and/or sections.
- Retrieve the title, date, description, and image for each news article within the specified time period.
- Store the extracted data in an Excel file, including additional information such as the count of search phrases in the title and description, and whether the title or description contains any amount of money.
- Download the news article images and include the corresponding file names in the Excel file.

Please note that the automation may take some time to complete, depending on the number of articles and the chosen time period.

## Logging
During the execution of the automation, detailed logs will be displayed in the console to provide visibility into the progress and actions taken. The logging statements help track the steps performed and provide useful information for debugging and troubleshooting.

The logs include the following:

- Start and end messages for each major step in the automation process.
- Execution time for each step, indicating the time taken to complete the operation.
- Error messages, if any, with relevant details about the encountered issue.

Example:
```
INFO    [nyt.py:20] - Setup
INFO    [nyt.py:26] - Get work item variables
INFO    [home_page.py:27] - Enter search query
INFO    [search_page.py:65] - Set categories
WARNING [search_page.py:105] - Unknown categories: ['something']
INFO    [search_page.py:65] - Set sections
INFO    [search_page.py:18] - Set date range
INFO    [search_page.py:120] - Sort by newest
INFO    [search_page.py:136] - Expand all articles
INFO    [search_page.py:151] - No more Show Button
INFO    [search_page.py:161] - All articles count: 34
INFO    [search_page.py:178] - Unique articles count: 34
INFO    [search_page.py:182] - Parse articles data
INFO    [nyt.py:51] - Export articles to excel file
INFO    [nyt.py:63] - Download pictures
INFO    [nyt.py:91] - Complete
INFO    [nyt.py:97] - Capture page screenshot
```

## Output
Upon successful execution, the automation will generate an Excel file named `articles.xlsx` in the `output` directory. This file will contain the extracted news data, including the title, date, description, picture filename, search phrase count, and money presence indicator.

Additionally, the news article images will be downloaded and saved in the output/images directory.

## Error Handling
If any errors occur during the execution of the automation, error messages will be displayed on the console, indicating the nature of the issue. Please refer to these error messages for troubleshooting and resolving any potential problems.







