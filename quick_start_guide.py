import webbrowser
import tempfile
import os
from logger_config import logger

def show_quick_start_guide():
    logger.info("Opening Quick Start Guide")
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Import Export Checker - Quick Start Guide</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 0 20px;
                }
                h1 {
                    color: #007bff;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #0056b3;
                    margin-top: 20px;
                }
                .step {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                }
                .important {
                    background-color: #fff3cd;
                    border: 1px solid #ffeeba;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }
                .new-feature {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Import Export Checker - Quick Start Guide</h1>

            <div class="step">
                <h2>Basic Steps</h2>
                <ol>
                    <li>Select your project type (PPE/MLBW or SSP)</li>
                    <li>Choose check type (Import or Export)</li>
                    <li>Select ReqIF folder containing your files</li>
                    <li>Optional: Enable "Select compare file" checkbox and select a reference file</li>
                    <li>Click "Convert" to process ReqIF files</li>
                    <li>Click "Execute Checks" to run the validation</li>
                </ol>
            </div>

            <div class="new-feature">
                <h2>Recent Files Feature</h2>
                <p>The application now remembers your recently used folders and files:</p>
                <ul>
                    <li>Access recent folders and files from the File menu</li>
                    <li>Recent Folders: Quickly access previously used ReqIF folders</li>
                    <li>Recent Files: Quick access to previously used compare files</li>
                    <li>Up to 5 recent items are stored for each type</li>
                    <li>Invalid paths are automatically removed from the list</li>
                </ul>
            </div>

            <div class="step">
                <h2>Compare File Option</h2>
                <ol>
                    <li>Enable "Select compare file" checkbox if needed</li>
                    <li>Browse or select from recent files</li>
                    <li>Recent files can only be selected when the checkbox is enabled</li>
                </ol>
            </div>

            <div class="step">
                <h2>Report Options</h2>
                <p>Choose your preferred report format:</p>
                <ul>
                    <li>HTML: Interactive web-based report</li>
                    <li>Excel: Spreadsheet format report</li>
                </ul>
            </div>

            <div class="important">
                <h2>Important Notes</h2>
                <ul>
                    <li>All folders and log file are created in the same directory as the application</li>
                    <li>Make sure you have write permissions in the application folder</li>
                    <li>Check output.log for detailed operation logs and error messages</li>
                    <li>Previous reports are cleared when executing new checks</li>
                </ul>
            </div>

            <div class="step">
                <h2>Application Folders</h2>
                <p>The following folders are automatically created in the application directory:</p>
                <ul>
                    <li><strong>extract/</strong>: Contains extracted ReqIF data</li>
                    <li><strong>excel/</strong>: Stores converted Excel files</li>
                    <li><strong>report/</strong>: Contains generated check reports</li>
                    <li><strong>output.log</strong>: Records application logs and debug information</li>
                </ul>
            </div>
        </body>
        </html>
        """

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
            logger.debug(f"Created temporary guide file: {temp_path}")

        # Open the temporary file in the default browser
        webbrowser.open('file://' + temp_path)
        logger.info("Quick Start Guide opened in browser")
        
    except Exception as e:
        logger.error(f"Error showing Quick Start Guide: {str(e)}", exc_info=True)
        raise 