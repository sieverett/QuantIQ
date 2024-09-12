

import sys
# import os
# import streamlit as st
# from openai import OpenAI
# from docx import Document
# from markdown_pdf import MarkdownPdf, Section
# import pandas as pd
# import zipfile
# import pdfkit
import re


text = "```lots of text and other stuff``` and the more stuff"

# Extract the text between ```
match = re.search(r"```(.*?)```", text)

if match:
    extracted_text = match.group(1)
    print(extracted_text)
else:
    print("No match found")

string = """```html\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Financial Analysis Report | EcoLeather Recyclers Pvt. Ltd.</title>\n    <style>\n        body { font-family: Arial, sans-serif; line-height: 1.6; }\n        h1, h2, h3 { color: #333; }\n        table { width: 100%; border-collapse: collapse; margin: 20px 0; }\n        table, th, td { border: 1px solid #ddd; }\n        th, td { padding: 8px; text-align: left; }\n        th { background-color: #f4f4f4; }\n    </style>\n</head>\n<body>\n    <h1>Financial Analysis Report | EcoLeather Recyclers Pvt. Ltd.</h1>\n    \n    <h2>Company Overview</h2>\n    <p>EcoLeather Recyclers Pvt. Ltd. operates in the leather recycling industry in India, focusing on collecting, processing, and repurposing leather from old coats and garments. The company sources discarded leather from individuals, factories, and clothing retailers, transforming it into new products such as handbags, shoes, and furniture upholstery. EcoLeather Recyclers works closely with local artisans and follows sustainable practices to reduce the environmental impact of leather waste.</p>\n    <h3>Key Challenges Faced in 2023</h3>\n    <ul>\n        <li><strong>Supply Chain Disruptions:</strong> Due to fluctuating leather collection rates and transportation strikes, EcoLeather Recyclers faced significant supply chain disruptions. This led to delays in production and a reduction in raw material availability, forcing the company to scale back on production capacity.</li>\n        <li><strong>Regulatory Hurdles:</strong> New environmental regulations introduced in late 2023 required the company to upgrade its processing facilities to meet stricter standards for waste management and emissions. This led to unexpected capital expenditures and impacted the company’s cash flow.</li>\n    </ul>\n    \n    <h2>Management Discussion and Analysis (MD&A) Summary</h2>\n    <h3>Profitability and Revenue Trends</h3>\n    <p>Despite the challenges, EcoLeather Recyclers managed to maintain steady revenue through the sale of recycled leather products. However, increased costs due to regulatory compliance and supply chain disruptions led to a drop in net income.</p>\n    <h3>Market Competition and Positioning</h3>\n    <p>EcoLeather Recyclers positions itself as a leader in sustainable leather recycling, leveraging close collaborations with local artisans and sustainable practices to differentiate from competitors.</p>\n    <h3>Strategic Initiatives and Investments</h3>\n    <p>In response to regulatory changes, the company invested heavily in new recycling equipment to meet stricter standards. These investments are expected to enhance operational efficiency and compliance in the long term.</p>\n    <h3>Future Outlook and Risks</h3>\n    <p>The company anticipates continued regulatory pressure and potential supply chain volatility. However, strategic investments in technology and processes are expected to mitigate these risks and support sustainable growth.</p>\n    \n    <h2>Balance Sheet Retrieval</h2>\n    <table>\n        <tr>\n            <th>Category</th>\n            <th>Amount (INR)</th>\n        </tr>\n        <tr>\n            <td>Cash and Cash Equivalents</td>\n            <td>₹1,200,000</td>\n        </tr>\n        <tr>\n            <td>Accounts Receivable</td>\n            <td>₹500,000</td>\n        </tr>\n        <tr>\n            <td>Inventory</td>\n            <td>₹2,500,000</td>\n        </tr>\n        <tr>\n            <td>Property and Equipment</td>\n            <td>₹3,000,000</td>\n        </tr>\n        <tr>\n            <td>Accounts Payable</td>\n            <td>₹900,000</td>\n        </tr>\n        <tr>\n            <td>Bank Loans</td>\n            <td>₹1,500,000</td>\n        </tr>\n        <tr>\n            <td>Total Liabilities</td>\n            <td>₹2,550,000</td>\n        </tr>\n        <tr>\n            <td>Owner’s Equity</td>\n            <td>₹4,650,000</td>\n        </tr>\n    </table>\n    \n    <h2>Balance Sheet Trend Analysis</h2>\n    <table>\n        <tr>\n            <th>Category</th>\n            <th>Beginning of Year (Amount)</th>\n            <th>End of Year (Amount)</th>\n            <th>Change (Amount)</th>\n            <th>Percentage Change</th>\n        </tr>\n        <tr>\n            <td>Cash and Cash Equivalents</td>\n            <td>₹1,700,000</td>\n            <td>₹1,200,000</td>\n            <td>₹-500,000</td>\n            <td>-29.41%</td>\n        </tr>\n        <tr>\n            <td>Accounts Receivable</td>\n            <td>₹600,000</td>\n            <td>₹500,000</td>\n            <td>₹-100,000</td>\n            <td>-16.67%</td>\n        </tr>\n        <tr>\n            <td>Inventory</td>\n            <td>₹2,200,000</td>\n            <td>₹2,500,000</td>\n            <td>₹300,000</td>\n            <td>13.64%</td>\n        </tr>\n        <tr>\n            <td>Total Assets</td>\n            <td>₹7,500,000</td>\n            <td>₹7,200,000</td>\n            <td>₹-300,000</td>\n            <td>-4.00%</td>\n        </tr>\n        <tr>\n            <td>Accounts Payable</td>\n            <td>₹1,000,000</td>\n            <td>₹900,000</td>\n            <td>₹-100,000</td>\n            <td>-10.00%</td>\n        </tr>\n        <tr>\n            <td>Bank Loans</td>\n            <td>₹1,200,000</td>\n            <td>₹1,500,000</td>\n            <td>₹300,000</td>\n            <td>25.00%</td>\n        </tr>\n        <tr>\n            <td>Total Liabilities</td>\n            <td>₹2,500,000</td>\n            <td>₹2,550,000</td>\n            <td>₹50,000</td>\n            <td>2.00%</td>\n        </tr>\n        <tr>\n            <td>Owner’s Equity</td>\n            <td>₹5,000,000</td>\n            <td>₹4,650,000</td>\n            <td>₹-350,000</td>\n            <td>-7.00%</td>\n        </tr>\n    </table>\n    \n    <h2>Cash Flow Statement Retrieval</h2>\n    <table>\n        <tr>\n            <th>Activity</th>\n            <th>Amount (INR)</th>\n        </tr>\n        <tr>\n            <td>Net Cash from Operating Activities</td>\n            <td>₹1,200,000</td>\n        </tr>\n        <tr>\n            <td>Net Cash Used in Investing Activities</td>\n            <td>₹-1,400,000</td>\n        </tr>\n        <tr>\n            <td>Net Cash Used in Financing Activities</td>\n            <td>₹-300,000</td>\n        </tr>\n        <tr>\n            <td>Net Decrease in Cash</td>\n            <td>₹-500,000</td>\n        </tr>\n        <tr>\n            <td>Cash at Beginning of Year</td>\n            <td>₹1,700,000</td>\n        </tr>\n        <tr>\n            <td>Cash at End of Year</td>\n            <td>₹1,200,000</td>\n        </tr>\n    </table>\n    \n    <h2>Cash Flow Trend Analysis</h2>\n    <table>\n        <tr>\n            <th>Cash Flow Category</th>\n            <th>Beginning of Year</th>\n            <th>End of Year</th>\n            <th>Change</th>\n            <th>Notes on Change</th>\n        </tr>\n        <tr>\n            <td>Net Cash from Operating Activities</td>\n            <td>₹1,000,000</td>\n            <td>₹1,200,000</td>\n            <td>₹200,000</td>\n            <td>Improved operational efficiency despite challenges.</td>\n        </tr>\n        <tr>\n            <td>Net Cash Used in Investing Activities</td>\n            <td>₹-500,000</td>\n            <td>₹-1,400,000</td>\n            <td>₹-900,000</td>\n            <td>Heavy investments in new equipment and regulatory upgrades.</td>\n        </tr>\n        <tr>\n            <td>Net Cash Used in Financing Activities</td>\n            <td>₹-200,000</td>\n            <td>₹-300,000</td>\n            <td>₹-100,000</td>\n            <td>Increased loan repayments and interest expenses.</td>\n        </tr>\n        <tr>\n            <td>Net Increase/Decrease in Cash</td>\n            <td>₹300,000</td>\n            <td>₹-500,000</td>\n            <td>₹-800,000</td>\n            <td>Overall decrease due to significant investing activities.</td>\n        </tr>\n    </table>\n    \n    <h2>Income Statement Retrieval</h2>\n    <table>\n        <tr>\n            <th>Category</th>\n            <th>Amount (INR)</th>\n        </tr>\n        <tr>\n            <td>Total Revenue</td>\n            <td>₹7,700,000</td>\n        </tr>\n        <tr>\n            <td>Total Expenses</td>\n            <td>₹6,850,000</td>\n        </tr>\n        <tr>\n            <td>Net Income (before taxes)</td>\n            <td>₹850,000</td>\n        </tr>\n    </table>\n    \n    <h2>Income Statement Trend Analysis</h2>\n    <table>\n        <tr>\n            <th>Income Statement Category</th>\n            <th>Beginning of Year</th>\n            <th>End of Year</th>\n            <th>Change</th>\n            <th>Percentage Change</th>\n            <th>Notes</th>\n        </tr>\n        <tr>\n            <td>Total Revenue</td>\n            <td>₹7,500,000</td>\n            <td>₹7,700,000</td>\n            <td>₹200,000</td>\n            <td>2.67%</td>\n            <td>Steady revenue despite supply chain issues.</td>\n        </tr>\n        <tr>\n            <td>Total Expenses</td>\n            <td>₹6,300,000</td>\n            <td>₹6,850,000</td>\n            <td>₹550,000</td>\n            <td>8.73%</td>\n            <td>Increased due to regulatory compliance costs.</td>\n        </tr>\n        <tr>\n            <td>Net Income</td>\n            <td>₹1,200,000</td>\n            <td>₹850,000</td>\n            <td>₹-350,000</td>\n            <td>-29.17%</td>\n            <td>Reduced profitability due to higher expenses.</td>\n        </tr>\n    </table>\n    \n    <h2>Ratio Analysis</h2>\n    <table>\n        <tr>\n            <th>Ratio Name</th>\n            <th>Formula</th>\n            <th>2023 Value</th>\n        </tr>\n        <tr>\n            <td>Return on Assets (ROA)</td>\n            <td>Net Income / Total Assets</td>\n            <td>₹850,000 / ₹7,200,000 = 11.81%</td>\n        </tr>\n        <tr>\n            <td>Return on Equity (ROE)</td>\n            <td>Net Income / Owner’s Equity</td>\n            <td>₹850,000 / ₹4,650,000 = 18.28%</td>\n        </tr>\n        <tr>\n            <td>Gross Margin</td>\n            <td>(Revenue - COGS) / Revenue</td>\n            <td>Not Provided</td>\n        </tr>\n        <tr>\n            <td>Operating Profit Margin</td>\n            <td>Operating Income / Revenue</td>\n            <td>Not Provided</td>\n        </tr>\n        <tr>\n          
  <td>Current Ratio</td>\n            <td>Current Assets / Current Liabilities</td>\n            <td>Not Provided</td>\n        </tr>\n        <tr>\n            <td>Quick Ratio</td>\n            <td>(Cash + Receivables) / Current Liabilities</td>\n            <td>Not Provided</td>\n        </tr>\n        <tr>\n            <td>Debt-to-Equity Ratio</td>\n            <td>Total Liabilities / Owner’s Equity</td>\n            <td>₹2,550,000 / ₹4,650,000 = 0.55</td>\n        </tr>\n        <tr>\n            <td>Total Liabilities/Total Assets</td>\n            <td>Total Liabilities / Total Assets</td>\n            <td>₹2,550,000 / ₹7,200,000 = 0.35</td>\n        </tr>\n        <tr>\n            <td>Asset Turnover</td>\n            <td>Revenue / Total Assets</td>\n            <td>₹7,700,000 / ₹7,200,000 = 1.07</td>\n        </tr>\n        <tr>\n            <td>Inventory Turnover</td>\n            <td>COGS / Inventory</td>\n            <td>Not Provided</td>\n        </tr>\n        <tr>\n            <td>Receivables Turnover</td>\n            <td>Revenue / Accounts Receivable</td>\n            <td>₹7,700,000 / ₹500,000 = 15.40</td>\n        </tr>\n    </table>\n    \n    <h2>Financial Health Assessment</h2>\n    <h3>Profitability</h3>\n    <p>EcoLeather Recyclers maintains decent profitability with a ROA of 11.81% and ROE of 18.28%. However, profitability has declined due to increased expenses.</p>\n    <h3>Liquidity</h3>\n    <p>Details not provided in the available data. However, cash flow analysis indicates a net decrease in cash, suggesting potential liquidity concerns.</p>\n    <h3>Solvency</h3>\n    <p>The debt-to-equity ratio is at a manageable level of 0.55, indicating the company is not overly leveraged.</p>\n    <h3>Efficiency</h3>\n    <p>The company demonstrates efficient asset use with an asset turnover ratio of 1.07 and a high receivables turnover ratio of 15.40.</p>\n    \n    <h2>Comprehensive Financial Review</h2>\n    <p>EcoLeather Recyclers faced several challenges in 2023, including supply chain disruptions and regulatory hurdles, which impacted its financial performance. Despite these challenges, the company maintained steady revenue but saw a decline in net income due to increased expenses. The balance sheet shows a strong asset base but also increased liabilities due to new loans. Cash flow analysis reveals significant investments in new equipment, leading to a net decrease in cash. Overall, the company\'s profitability remains decent, solvency is stable, but liquidity may be a concern.</p>\n    \n    <h2>EPS Forecast</h2>\n    <p>Based on the financial analysis, it is expected that the company’s Earnings Per Share (EPS) may experience slight improvement in the next reporting period. This expectation is based on anticipated benefits from strategic investments and improved operational efficiencies, although regulatory and supply chain risks remain.</p>\n    \n    <h2>Follow-up Questions for Management</h2>\n    <ol>\n        <li>Can you provide more details on the measures being taken to mitigate future supply chain disruptions?</li>\n        <li>What specific upgrades have been made to the processing facilities to meet the new regulatory standards?</li>\n        <li>How do you plan to improve the company’s liquidity position moving forward?</li>\n        <li>Are there any new strategic partnerships or market expansions planned for the coming year?</li>\n        <li>What is the expected timeline for seeing the benefits of recent investments in new recycling equipment?</li>\n    </ol>\n</body>\n</html>\n```\n\nThis report provides a comprehensive financial analysis of EcoLeather Recyclers Pvt. Ltd., including an overview, detailed financial statement analyses, and focused follow-up questions for the management team. The data and figures have been extracted from the provided financial statement document[0].')"""


def html_to_pdf(html_content, filename, output_dir):
    save_path = os.path.join(output_dir, filename.replace(
        ".pdf", "_quantiq_analysis")+".pdf")
    style = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    color: #333;
                    margin: 40px;
                }
                h1, h2 {
                    text-align: center;
                    font-family: 'Times New Roman', serif;
                    color: #000;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: right;
                }
                th {
                    background-color: #f4f4f4;
                    font-weight: bold;
                }
                .total-row {
                    font-weight: bold;
                    background-color: #eaeaea;
                }
            </style>
                """
    # html_content = parse_html_content(html_content)
    html_content = html_content.split("```")[1]
    print("parsed: ", html_content)
    html_content = html_content.replace("html\n<!DOCTYPE html>\n", "")
    logo = '<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
    html_content = logo+html_content.replace('<html>\n<head>\n', style)

    # Replace with the correct path if running from local
    try:
        path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
        config_pdfkit(path_wkhtmltopdf, html_content)
    except Exception as e:
        print(f"Error configuring pdfkit: {e}")
        path_wkhtmltopdf = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
        config_pdfkit(path_wkhtmltopdf, html_content)


def parse_html_content(html_content):

    match = re.search(r"```(.*?)```", html_content)
    if match:
        extracted_text = match.group(1)
        return extracted_text
    else:
        print("No match found")
        return None


def config_pdfkit(path_wkhtmltopdf, html_content):
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(html_content, 'test.pdf', options={
                       'enable-local-file-access': ''}, configuration=config)


# html_to_pdf(string, 'test.pdf', '.')
# # print(string.split("```")[1])

print(sys.platform.lower())