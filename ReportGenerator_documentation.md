# ReportGenerator Documentation

## Overview
The `ReportGenerator` class is responsible for generating various types of reports from validation findings. It supports multiple report formats including HTML, Excel, and CSV, with specific handling for translation requirements. The class is designed to be flexible and extensible, allowing for different types of reports to be generated from the same set of validation findings.

## Class Structure
The class consists of static methods only, making it a utility class that doesn't require instantiation. This design allows for easy access to report generation functionality without maintaining state.

## Class Methods

### `generate_report_old(file_path, report_folder, findings)`
**Static Method**
- **Purpose**: Generates a structured text report for findings (legacy method)
- **Parameters**:
  - `file_path`: Path to the input file being validated
  - `report_folder`: Directory where the report will be saved
  - `findings`: List of dictionaries containing validation findings
- **Returns**: Path to the generated report file
- **Output Format**: Text file with markdown-style formatting
- **Details**:
  - Creates a report with a summary section showing total findings
  - Each finding is formatted with clear section headers
  - Multi-line text blocks are formatted in code blocks
  - Includes file name and timestamp information
  - Uses markdown formatting for better readability

### `get_html_style()`
**Static Method**
- **Purpose**: Returns CSS styles for HTML reports
- **Returns**: String containing CSS styles
- **Features**:
  - Defines styling for report container, headers, issues, code blocks
  - Includes specific styles for diff highlighting
  - Provides responsive design elements
- **Style Details**:
  - Container: White background with shadow and rounded corners
  - Headers: Blue color scheme (#003366)
  - Issues: Red border with light red background
  - Code blocks: Dark background with monospace font
  - Diff highlighting: Green for additions, red for deletions
  - Responsive design: Adapts to different screen sizes

### `highlight_differences(text1, text2)`
**Static Method**
- **Purpose**: Highlights differences between two texts using HTML spans
- **Parameters**:
  - `text1`: First text to compare
  - `text2`: Second text to compare
- **Returns**: Tuple of two strings with HTML-formatted differences
- **Features**:
  - Handles empty text cases
  - Uses different colors for additions and deletions
  - Preserves whitespace and formatting
- **Implementation Details**:
  - Uses difflib.SequenceMatcher for text comparison
  - Wraps differences in HTML spans with specific classes
  - Handles special cases like empty strings
  - Preserves original text formatting
  - Returns both texts with highlighted differences

### `generate_html_content(file_name, total_issues, issues_content)`
**Static Method**
- **Purpose**: Generates the complete HTML content for the report
- **Parameters**:
  - `file_name`: Name of the file being analyzed
  - `total_issues`: Total number of issues found
  - `issues_content`: HTML content for all issues
- **Returns**: Complete HTML document as a string
- **Features**:
  - Includes responsive meta tags
  - Truncates long filenames
  - Adds timestamp and footer
- **HTML Structure**:
  - DOCTYPE and HTML5 meta tags
  - Embedded CSS styles
  - Responsive viewport settings
  - Structured content sections
  - Footer with generation timestamp

### `format_issue(finding)`
**Static Method**
- **Purpose**: Formats a single issue for the HTML report
- **Parameters**:
  - `finding`: Dictionary containing issue details
- **Returns**: HTML-formatted string for the issue
- **Features**:
  - Extracts and highlights text differences
  - Formats issue details in a structured way
  - Includes row number, attributes, and detailed information
- **Format Details**:
  - Issue container with warning icon
  - Structured display of row number and attributes
  - Code block for detailed information
  - Highlighted text differences
  - Clear visual separation between issues

### `generate_excel_report(file_path, report_folder, findings)`
**Static Method**
- **Purpose**: Generates an Excel report from findings
- **Parameters**:
  - `file_path`: Path to the input file
  - `report_folder`: Directory where the report will be saved
  - `findings`: List of dictionaries containing validation findings
- **Returns**: Path to the generated Excel file
- **Features**:
  - Renames 'Value' column to 'Details'
  - Preserves all finding information
  - Handles errors with logging
- **Excel Format**:
  - Clean column headers
  - Preserved formatting
  - All findings in a single sheet
  - Easy to filter and sort

### `_generate_html_report(file_path, report_folder, findings)`
**Static Method**
- **Purpose**: Internal method to generate HTML report
- **Parameters**:
  - `file_path`: Path to the input file
  - `report_folder`: Directory where the report will be saved
  - `findings`: List of dictionaries containing validation findings
- **Returns**: Path to the generated HTML file
- **Features**:
  - Creates formatted HTML content
  - Includes error handling and logging
  - Uses UTF-8 encoding
- **Implementation Details**:
  - Creates report filename based on input file
  - Generates issues content using format_issue
  - Wraps content in HTML structure
  - Handles file writing with proper encoding
  - Includes comprehensive error handling

### `generate_translation_csv(file_path, report_folder, findings)`
**Static Method**
- **Purpose**: Generates a CSV file for translation requirements
- **Parameters**:
  - `file_path`: Path to the input file
  - `report_folder`: Directory where the report will be saved
  - `findings`: List of dictionaries containing validation findings
- **Returns**: Path to the generated CSV file or None if no translations needed
- **Features**:
  - Creates different columns based on identifier type:
    - For ForeignID: 'ForeignID' and 'English_Translation'
    - For Object ID: 'Object ID' and 'Object Text English'
  - Skips empty or invalid cases
  - Handles OLE Object cases
  - Includes detailed logging
  - Marks translations as "Translation required"
- **Processing Details**:
  - Identifies identifier type (ForeignID or Object ID)
  - Filters out empty or invalid cases
  - Handles special OLE Object cases
  - Creates appropriate column structure
  - Generates CSV with proper formatting
  - Includes comprehensive logging

### `generate_report(file_path, report_folder, report_type, findings)`
**Static Method**
- **Purpose**: Main method to generate reports based on specified type
- **Parameters**:
  - `file_path`: Path to the input file
  - `report_folder`: Directory where the report will be saved
  - `report_type`: Type of report to generate ('excel' or 'html')
  - `findings`: List of dictionaries containing validation findings
- **Returns**: List of paths to generated report files
- **Features**:
  - Supports multiple report types
  - Automatically generates translation CSV for Check Nr. 10 findings
  - Includes error handling and logging
  - Returns list of all generated report files
- **Report Types**:
  - HTML: Interactive report with highlighted differences
  - Excel: Tabular format for easy analysis
  - CSV: Translation requirements in structured format

## Usage Examples

### Basic Usage
```python
# Generate an HTML report with translation CSV
report_files = ReportGenerator.generate_report(
    file_path="input.xlsx",
    report_folder="reports",
    report_type="html",
    findings=validation_findings
)
```

### Advanced Usage
```python
# Generate specific report types
# HTML Report
html_report = ReportGenerator._generate_html_report(
    file_path="input.xlsx",
    report_folder="reports",
    findings=validation_findings
)

# Excel Report
excel_report = ReportGenerator.generate_excel_report(
    file_path="input.xlsx",
    report_folder="reports",
    findings=validation_findings
)

# Translation CSV
translation_csv = ReportGenerator.generate_translation_csv(
    file_path="input.xlsx",
    report_folder="reports",
    findings=validation_findings
)
```

## Error Handling
- All methods include try-except blocks
- Errors are logged using the logger
- Detailed error messages are provided
- Stack traces are included in logs for debugging
- Specific error handling for:
  - File operations
  - Data processing
  - Report generation
  - CSV/Excel operations

## Logging
- Comprehensive logging throughout the class
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Detailed context in log messages
- Stack traces for errors
- Performance metrics where applicable

## Dependencies
- pandas: For DataFrame operations and CSV/Excel file handling
- datetime: For timestamp generation
- difflib: For text comparison and difference highlighting
- os: For file path operations
- logger_config: For logging functionality

## Best Practices
1. Always use the main `generate_report` method for standard use cases
2. Use specific report generation methods for custom requirements
3. Check return values for None in case of errors
4. Monitor log files for detailed operation information
5. Handle file paths appropriately for cross-platform compatibility

## Performance Considerations
- HTML reports may be larger due to styling and formatting
- Excel reports are efficient for large datasets
- CSV generation is optimized for translation requirements
- Memory usage scales with the number of findings
- File operations are buffered for better performance 