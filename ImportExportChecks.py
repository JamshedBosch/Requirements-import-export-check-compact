import os
import pandas as pd
import shutil
from ReportGenerator import ReportGenerator
from ChecksPPE import ProjectCheckerPPE
from ChecksSSP import  ProjectCheckerSSP
import sys
from utils import get_exe_directory


class CheckConfiguration:
    """Holds configuration and constants for checks."""
    IMPORT_CHECK = 0
    EXPORT_CHECK = 1

    PROJECT = {
        "PPE_MLBW": "PPE/MLBW",
        "SSP": "SSP"
    }

    @staticmethod
    def get_exe_directory():
        return get_exe_directory()

    @classmethod
    def initialize_folders(cls):
        """Initialize all required folders in the executable directory."""
        base_dir = cls.get_exe_directory()
        
        # Define and create all required folders
        cls.EXTRACT_FOLDER = os.path.join(base_dir, "extract")
        cls.EXCEL_FOLDER = os.path.join(base_dir, "excel")
        cls.REPORT_FOLDER = os.path.join(base_dir, "report")

        # Create all folders
        for folder in [cls.EXTRACT_FOLDER, cls.EXCEL_FOLDER, cls.REPORT_FOLDER]:
            os.makedirs(folder, exist_ok=True)
            
        return cls.EXTRACT_FOLDER, cls.EXCEL_FOLDER, cls.REPORT_FOLDER

    IMPORT_FOLDERS = {
        IMPORT_CHECK: r"D:\AUDI\Import_Reqif2Excel_Converted",
        EXPORT_CHECK: r"D:\AUDI\Export_Reqif2Excel_Converted"
    }



class ChecksProcessor:
    """Main processor for Excel file Checks."""

    def __init__(self, project_type, check_type, excel_folder, compare_file=None, report_type="HTML"):
        self.project = project_type
        self.check_type = check_type
        self.report_folder = CheckConfiguration.REPORT_FOLDER
        self.report_type = report_type
        self.folder_path = excel_folder
        self.compare_file = compare_file
        self.compare_df = None  # Dataframe to hold compare file data

        # if compare_file is provided, read it into a DataFrame
        if self.compare_file:
            try:
                self.compare_df = pd.read_excel(self.compare_file,
                                                keep_default_na=False,
                                                na_values=[''])

                print(
                    f"Compare file '{self.compare_file}' loaded successfully.")
            except Exception as e:
                print(f"Error loading compare file '{self.compare_file}': {e}")
                self.compare_df = None

    def process_folder(self):
        """Process all Excel files in the specified folder."""
        # Delete existing report folder
        self._delete_folder(self.report_folder)
        os.makedirs(self.report_folder, exist_ok=True)

        reports = []
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith('.xlsx'):
                file_path = os.path.join(self.folder_path, file_name)
                report = self._process_file(file_path)
                reports.append(report)

        return reports

    def _process_file(self, file_path):
        """Process a single Excel file."""
        # Read Excel file with special handling of missing values:
        #   - keep_default_na=False: Preserves strings like 'n/a', 'N/A', 'NA' as actual strings instead of converting them to NaN
        #   - na_values=['']: Only treats completely empty cells as missing values (NaN)
        # Read Excel file: preserve 'n/a' as string (keep_default_na=False) and only treat empty cells as NaN (na_values=[''])
        df = pd.read_excel(file_path, keep_default_na=False, na_values=[''])
        findings = []

        # Select Project
        if self.project == CheckConfiguration.PROJECT["PPE_MLBW"]:
            # Select checks based on type
            # Import check AUDI ==> BOSCH
            if self.check_type == CheckConfiguration.IMPORT_CHECK:
                findings = (
                        ProjectCheckerPPE.check_empty_object_id_with_forbidden_cr_status(
                            df, file_path) +
                        ProjectCheckerPPE.check_cr_status_bosch_ppx_conditions(
                            df, file_path) +
                        ProjectCheckerPPE.check_anlaufkonfiguration_empty(
                            df, file_path) +
                        ProjectCheckerPPE.check_cr_id_empty_for_brs_hersteller_status(
                            df, file_path) +
                        ProjectCheckerPPE.check_required_attributes_not_empty(
                            df, file_path)
                )
                if self.compare_df is not None:

                    findings += ProjectCheckerPPE.check_object_text_with_status_hersteller_bosch_ppx(
                        df, self.compare_df, file_path, self.compare_file)

                    # Execute check check_object_text_with_rb_as_status and create a separate report
                    rb_as_status_findings = ProjectCheckerPPE.check_object_text_with_rb_as_status(
                        df, self.compare_df, file_path, self.compare_file)

                    # if rb_as_status_findings:
                        # Generate a separate report for this check
                    ReportGenerator.generate_report(
                        self.compare_file,
                        self.report_folder,
                        self.report_type,
                        rb_as_status_findings
                    )

            else:
                # Export check BOSCH ==> AUDI
                findings = (
                        ProjectCheckerPPE.check_cr_id_with_typ_and_brs_1box_status_zulieferer_bosch_ppx(
                            df, file_path)
                        +
                        ProjectCheckerPPE.check_typ_with_brs_1box_status_zulieferer_bosch_ppx(
                            df, file_path)
                )
        elif self.project == CheckConfiguration.PROJECT["SSP"]:
            if self.check_type == CheckConfiguration.IMPORT_CHECK:
                # Here implement check 1 - 5
                if self.compare_df is not None:
                    # check 6
                    findings += ProjectCheckerSSP.check_object_text_with_status_oem_zu_lieferant_r(
                        df, self.compare_df, file_path, self.compare_file)

                    # check 8
                    findings += ProjectCheckerSSP.check_multiple_attributes_with_status_oem_zu_lieferant_r(
                        df, self.compare_df, file_path, self.compare_file)
            else:
                # Export check BOSCH ==> AUDI
                print("[SSP] NO EXPORT CHECKS DEFINED SOFAR")

        # Generate report
        return ReportGenerator.generate_report(file_path, self.report_folder, self.report_type,
                                               findings)

    def _delete_folder(self, folder_path):
        """Delete a folder and its contents."""
        try:
            shutil.rmtree(folder_path, ignore_errors=True)
        except Exception as e:
            print(f"Error deleting '{folder_path}': {str(e)}")




def main():
    # Set the check type: 0 for Import Check, 1 for Export Check
    check_type = CheckConfiguration.IMPORT_CHECK  # Change to EXPORT_CHECK if needed
    compare_file = r"D:\AUDI\comparefile\CCB_Tracking_PPE.xlsx"

    processor = ChecksProcessor(check_type,
                                CheckConfiguration.IMPORT_FOLDERS[check_type],
                                compare_file)
    reports = processor.process_folder()

    print(
        f"Processed {len(reports)} files. Reports are stored in {CheckConfiguration.REPORT_FOLDER}")


if __name__ == "__main__":
    main()
