# import RPA modules
from RPA.Excel.Files import Files
# import system modules
import os
# import custom modules
from common.Decorators import step_logger_decorator


@step_logger_decorator("Export Articles to Excel File")
def export_articles_to_excel_file(articles):
    """
    Exports a list of articles to an Excel file.

    Parameters:
        `articles (list)`: A list of article objects.
    """
    try:
        excel_lib = Files()
        excel_lib.create_workbook(
            path=os.path.join('output', 'articles.xlsx'), fmt="xlsx", sheet_name="NYT")
        data = []
        for article in articles:
            # Create and append article data row
            row = article.make_excel_row()
            data.append(row)
    except Exception as e:
        print("Error while exporting articles data", e)
    finally:
        # Save file
        excel_lib.append_rows_to_worksheet(data, header=True)
        excel_lib.save_workbook()
