from datetime import datetime
import os
from typing import Dict, Any, List
import difflib
import pandas as pd
from logger_config import logger


class ReportGenerator:
    """Generates reports from validation findings."""

    @staticmethod
    def generate_report_old(file_path, report_folder, findings):
        """Generate a structured and flexible text report for findings."""
        report_file = os.path.join(report_folder,
                                   f"{os.path.basename(file_path).replace('.xlsx', '')}_report.txt")

        with open(report_file, 'w') as f:
            # Header
            f.write(f"#### Report Summary\n")
            f.write(f"**File Name:** `{os.path.basename(file_path)}`\n")
            f.write(f"**Total Findings:** {len(findings)}\n")
            f.write("\n---\n\n")

            # Detailed Issues
            if findings:
                f.write("### Detailed Issues\n")
                for idx, finding in enumerate(findings, start=1):
                    f.write(f"#### Finding {idx}\n")

                    # Dynamically iterate over all keys in the finding dictionary
                    for key, value in finding.items():
                        # Format multi-line text blocks (like Object Text)
                        if isinstance(value, str) and "\n" in value:
                            f.write(f"- **{key}:**\n")
                            f.write(f"  ```\n{value}\n  ```\n")
                        else:
                            f.write(f"- **{key}:** `{value}`\n")

                    f.write("\n---\n\n")  # Separator between issues
            else:
                f.write("No issues found.\n")

        return report_file

    @staticmethod
    def get_html_style():
        """Return the CSS styles for the report."""
        return """
                   body {
                       font-family: Arial, sans-serif;
                       margin: 20px;
                       padding: 20px;
                       background: #f4f7f9;
                   }
                   .container {
                       max-width: 900px;
                       margin: auto;
                       background: #fff;
                       padding: 20px;
                       border-radius: 10px;
                       box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                   }
                   h1 {
                       color: #003366;
                   }
                   .issue {
                       border-left: 5px solid #ff6b6b;
                       padding: 15px;
                       margin-bottom: 20px;
                       background: #fff3f3;
                       border-radius: 8px;
                   }
                   .issue h2 {
                       color: #d43f3f;
                       margin: 0 0 8px;
                       font-size: 20px;
                   }
                   .issue p {
                       margin: 5px 0;
                       font-size: 14px;
                   }
                   .code-block {
                       background: #1e1e1e;
                       color: #ffffff;
                       padding: 10px;
                       border-radius: 5px;
                       font-family: 'Courier New', monospace;
                       white-space: pre-wrap;
                       overflow-x: auto;
                       border: 1px solid #ccc;
                       font-size: 13px;
                       line-height: 1.5;
                   }
                   .footer {
                       margin-top: 20px;
                       font-size: 12px;
                       color: #666;
                       text-align: center;
                   }
                   .diff-add {
                       background-color: #2da44e;
                       color: white;
                   }
                   .diff-del {
                       background-color: #cf222e;
                       color: white;
                   }
                   .text-block {
                       margin: 10px 0;
                       padding: 10px;
                       background: #2d2d2d;
                       border-radius: 5px;
                   }
               """

    @staticmethod
    def highlight_differences(text1: str, text2: str) -> tuple[str, str]:
        """
        Highlight the differences between two texts using HTML spans.
        If one text is missing, the other text is fully highlighted.
        """

        # Ensure we remove any hidden whitespace or special formatting
        text1 = text1.strip()
        text2 = text2.strip()

        # Debugging: Print the raw input to check if text2 is truly empty
        # print(f"DEBUG - text1: {repr(text1)} | text2: {repr(text2)}")

        # If one of the texts is empty, highlight the other entirely
        if text1 and not text2:
            return f'<span class="diff-del">{text1}</span>', '<span class="diff-add">Empty</span>'
        if text2 and not text1:
            return '<span class="diff-del">Empty</span>', f'<span class="diff-add">{text2}</span>'

        matcher = difflib.SequenceMatcher(None, text1, text2)
        result1, result2 = [], []

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                result1.append(text1[i1:i2])
                result2.append(text2[j1:j2])
            elif op == 'replace':
                result1.append(f'<span class="diff-del">{text1[i1:i2]}</span>')
                result2.append(f'<span class="diff-add">{text2[j1:j2]}</span>')
            elif op == 'insert':
                result2.append(f'<span class="diff-add">{text2[j1:j2]}</span>')
            elif op == 'delete':
                result1.append(f'<span class="diff-del">{text1[i1:i2]}</span>')

        return ''.join(result1), ''.join(result2)



    @staticmethod
    def generate_html_content(file_name, total_issues, issues_content):
        """Generate the complete HTML content."""
        # Truncate the file name if it's too long
        max_filename_length = 50
        truncated_filename = file_name[:max_filename_length] + "..." if len(
            file_name) > max_filename_length else file_name
        return f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Analysis Report - {truncated_filename}</title>
            <style>
                {ReportGenerator.get_html_style()}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📋 Report for the File: {truncated_filename}</h2>
                <p><strong>Total Findings:</strong> {total_issues}</p>
        {issues_content}
                <div class="footer">
                    Generated by Import/Export Checker | Date: {datetime.now().strftime('%Y-%m-%d')}
                </div>
            </div>
        </body>
        </html>"""

    @staticmethod
    def format_issue(finding):
        """Format a single issue for the report."""
        # Extract customer and Bosch texts from the Value string
        value_lines = finding['Value'].split('\n')
        customer_text = ""
        bosch_text = ""

        for i, line in enumerate(value_lines):
            if "Customer File Object Text:" in line:
                customer_text = line.replace("Customer File Object Text:",
                                             "").strip()
            elif "Bosch File Object Text:" in line:
                bosch_text = line.replace("Bosch File Object Text:",
                                          "").strip()

        # Convert None values to empty strings (if needed)
        customer_text = customer_text if customer_text else ""
        bosch_text = bosch_text if bosch_text else ""

        # Debugging output
        # print(f"DEBUG - format_issue called for Row: {finding['Row']}")
        # print(f"DEBUG - Customer Text: {repr(customer_text)}")
        # print(f"DEBUG - Bosch Text: {repr(bosch_text)}")

        # Ensure highlight_differences is always called
        highlighted_customer, highlighted_bosch = ReportGenerator.highlight_differences(
            customer_text, bosch_text)

        # Replace the original texts in value_lines with highlighted versions
        for i, line in enumerate(value_lines):
            if "Customer File Object Text:" in line:
                value_lines[
                    i] = f"       Customer File Object Text: {highlighted_customer}"
            elif "Bosch File Object Text:" in line:
                value_lines[
                    i] = f"       Bosch File Object Text: {highlighted_bosch}"

        formatted_value = "<br>".join(value_lines)

        return f"""        <div class="issue">
                       <h2>⚠️ Row: {finding['Row']}</h2>
                       <p><strong>Attributes:</strong> {finding['Attribute']}</p>
                       <p><strong>Check:</strong> {finding['Issue']}</p>
                       <p><strong>Details:</strong></p>
                       <div class="code-block">{formatted_value}</div>
                   </div>"""

    @staticmethod
    def generate_excel_report(file_path, report_folder, findings):
        logger.debug(f"Generating Excel report with {len(findings)} findings")
        try:
            report_file = os.path.join(report_folder, f"{os.path.basename(file_path).replace('.xlsx', '')}_report.xlsx")
            df = pd.DataFrame(findings)
            df = df.rename(columns={'Value': 'Details'})
            df.to_excel(report_file, index=False)
            return report_file
        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _generate_html_report(file_path, report_folder, findings):
        """Generate HTML report for findings."""
        logger.debug(f"Generating HTML report for {file_path}")
        try:
            # Create report filename
            base_name = os.path.basename(file_path).replace('.xlsx', '')
            report_file = os.path.join(report_folder, f"{base_name}_report.html")

            # Generate issues content
            issues_content = "\n".join(
                ReportGenerator.format_issue(finding) for finding in findings)

            # Generate the complete HTML content
            html_content = ReportGenerator.generate_html_content(
                file_name=os.path.basename(file_path),
                total_issues=len(findings),
                issues_content=issues_content
            )

            # Write the report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.debug(f"HTML report generated successfully: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def generate_report(file_path, report_folder, report_type, findings):
        logger.info(f"Generating {report_type} report for {file_path}")
        
        try:
            report_type = report_type.lower()
            if report_type == 'excel':
                report_file = ReportGenerator.generate_excel_report(file_path, report_folder, findings)
            else:
                report_file = ReportGenerator._generate_html_report(file_path, report_folder, findings)
            
            logger.info(f"Successfully generated report: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            raise
