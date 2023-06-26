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
Start: [Enter Search Query]
End: [Enter Search Query] Execution time - 0m:15s:375ms
Start: [Set Filters]
Unknown filters:  ['Something']
End: [Set Filters] Execution time - 0m:2s:83ms
No section filters provided
Start: [Set Date Range]
End: [Set Date Range] Execution time - 0m:4s:212ms
Start: [Sort By Newest]
End: [Sort By Newest] Execution time - 0m:0s:354ms
Start: [Expand And Get All Articles]
No more Show Button - Element with locator 'css:[data-testid="search-show-more-button"]' not found.
All articles count: 310
Unique articles count: 230
End: [Expand And Get All Articles] Execution time - 0m:24s:634ms
Start: [Parse Articles Data]
End: [Parse Articles Data] Execution time - 0m:16s:188ms
Start: [Export Articles to Excel File]
End: [Export Articles to Excel File] Execution time - 0m:0s:31ms
Start: [Download Pictures]
No picture found for: Corrections: June 24, 2023
No picture found for: Debris From Russian Missile Kills Three in Kyiv Apartment Building
No picture found for: Understanding Ukraine’s Counteroffensive
No picture found for: Corrections: June 22, 2023
No picture found for: The Re-Militarization of Germany
No picture found for: Quotation of the Day: Hidden Horrors of Russian Treatment of P.O.W.s
No picture found for: Corrections: June 20, 2023
No picture found for: Transcript: Ezra Klein Interviews Jon Favreau
No picture found for: Quotation of the Day: Every Block Is Another Battle for ‘the Cyborgs’ in Ukraine’s East
No picture found for: Despite Calls for Protests, Trump Arraignment Draws Only Colorful Crowds
No picture found for: A U.S. Citizen Has Been Arrested in Russia, State Department Says
End: [Download Pictures] Execution time - 2m:9s:77ms
End
```

## Output
Upon successful execution, the automation will generate an Excel file named `articles.xlsx` in the `output` directory. This file will contain the extracted news data, including the title, date, description, picture filename, search phrase count, and money presence indicator.

Additionally, the news article images will be downloaded and saved in the output/images directory.

## Error Handling
If any errors occur during the execution of the automation, error messages will be displayed on the console, indicating the nature of the issue. Please refer to these error messages for troubleshooting and resolving any potential problems.







