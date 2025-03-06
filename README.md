# Import Export Checker

A GUI application for checking and validating ReqIF files, specifically designed for PPE/MLBW and SSP projects. The tool provides functionality to convert ReqIF files to Excel format and perform various validation checks.

## Features

### Core Functionality
- Convert ReqIF/REQIFZ files to Excel format
- Support for both PPE/MLBW and SSP projects
- Import and Export check capabilities
- Optional comparison with reference files

### User Interface
- Modern GUI with intuitive controls
- Recent folders and files history
- Status bar for operation feedback
- Quick Start Guide accessible from Help menu

### Report Generation
- HTML reports with highlighted differences
- Excel report option for spreadsheet analysis
- Detailed findings with row-level information

### Project Types
1. PPE/MLBW Checks:
   - Import checks (AUDI → BOSCH)
   - Export checks (BOSCH → AUDI)
   
2. SSP Checks:
   - Import checks with comparison functionality
   - Status validation

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python ImportExportChecksGUI.py
```

### Basic Workflow
1. Select project type (PPE/MLBW or SSP)
2. Choose check type (Import or Export)
3. Select ReqIF folder containing your files
4. (Optional) Enable and select compare file
5. Click "Convert" to process ReqIF files
6. Click "Execute Checks" to run validation

### File Menu Features
- Access recently used ReqIF folders
- Quick access to previously used compare files
- Up to 5 recent items stored for each type

## Project Structure

- `extract/`: Contains extracted ReqIF data
- `excel/`: Stores converted Excel files
- `report/`: Contains generated check reports
- `output.log`: Application logs and debug information

## Requirements

- Python 3.x
- pyreqif
- pandas
- colorclass
- oletools

## Logging

The application maintains detailed logs in `output.log`, capturing:
- Operation progress
- Error messages
- Debug information
- File processing details

## Support

For issues and feature requests, please create an issue in the repository.


