# Disable color output before any other imports
import os
os.environ["COLORCLASS_DISABLE"] = "1"
os.environ["NO_COLOR"] = "1"

# Now import other modules
import re
import zipfile
import shutil
import glob
import pyreqif.reqif
import pyreqif.rif
import pyreqif.xlsx
import html
from logger_config import logger



class ReqIF2ExcelProcessor:
    def __init__(self, source_folder, reqif_folder, excel_folder,
                 check_type=0):
        """
        Initialize the ReqIF2Excel Processor with source and destination folders

        Args:
            source_folder (str): Path to source REQIF or XML files
            reqif_folder (str): Path to extract REQIF/XML files
            excel_folder (str): Path to store converted Excel files
            check_type (int, optional): 0 for Import Check, 1 for Export Check. Defaults to 0.
        """
        logger.info(f"Initializing ReqIF2ExcelProcessor")
        logger.debug(f"ReqIF folder: {reqif_folder}")
        logger.debug(f"Extract folder: {source_folder}")
        logger.debug(f"Excel folder: {excel_folder}")
        self.source_folder = source_folder
        self.reqif_folder = reqif_folder
        self.excel_folder = excel_folder
        self.check_type = check_type

    def extract_all_files(self):
        """
        Recursively extract all ZIP and REQIFZ files from source folder
        """
        for root, _, files in os.walk(self.source_folder):
            for file in files:
                if file.endswith('.zip') or file.endswith('.reqifz'):
                    file_path = os.path.join(root, file)
                    self._extract_zip_recursive(file_path)

    def _extract_zip_recursive(self, file_path):
        """
        Recursively extract nested ZIP files

        Args:
            file_path (str): Path to the ZIP file to extract
        """
        try:
            if not zipfile.is_zipfile(file_path):
                print(f"Skipping invalid zip file: {file_path}")
                return

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.reqif_folder)
                for name in zip_ref.namelist():
                    nested_zip_path = os.path.join(self.reqif_folder, name)
                    if nested_zip_path.endswith(
                            '.zip') or nested_zip_path.endswith('.reqifz'):
                        self._extract_zip_recursive(nested_zip_path)

        except zipfile.BadZipFile:
            print(f"Error: {file_path} is not a valid zip file.")
        except Exception as e:
            print(f"Unexpected error with file {file_path}: {e}")

    def prepare_folders(self):
        """
        Delete and recreate destination folders
        """
        for folder in [self.reqif_folder, self.excel_folder]:
            self.delete_folder(folder)
            os.makedirs(folder, exist_ok=True)

    @staticmethod
    def delete_folder(folder_path):
        """
        Delete a folder and its contents

        Args:
            folder_path (str): Path to the folder to delete
        """
        try:
            shutil.rmtree(folder_path)
            print(
                f"Folder '{folder_path}' and all its contents have been successfully deleted.")
        except Exception as e:
            print(f"Error deleting '{folder_path}': {str(e)}")

    def clean_reqif_folder(self):
        """
        Delete files except REQIF and XML
        """
        self.delete_files_except_extensions(self.reqif_folder,
                                            ['reqif', 'xml'])

    @staticmethod
    def delete_files_except_extensions(folder_path, allowed_extensions):
        """
        Delete all files except those with specified extensions

        Args:
            folder_path (str): Folder to clean up
            allowed_extensions (list): List of allowed file extensions
        """
        try:
            all_files = glob.glob(os.path.join(folder_path, "*"))

            for file_path in all_files:
                if os.path.isfile(file_path):
                    if not any(file_path.endswith(f".{ext}") for ext in
                               allowed_extensions):
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")

            print(
                f"All files except {', '.join(allowed_extensions)} files have been deleted.")

        except Exception as e:
            print(
                f"Error deleting files except '{allowed_extensions}': {str(e)}")

    def get_reqif_files(self):
        """
        Find all REQIF and XML files in the extraction folder

        Returns:
            list: Paths to REQIF and XML files
        """
        try:
            files_list = []
            for root, _, files in os.walk(self.reqif_folder):
                for file in files:
                    if file.endswith('.reqif') or file.endswith('.xml'):
                        files_list.append(os.path.join(root, file))

            print(f"Found {len(files_list)} REQIF/XML files")
            return files_list

        except Exception as e:
            print(f"Error searching for files: {str(e)}")
            return []

    def clean_text(self, raw_text):
        """
        Clean the given raw text by removing HTML tags and decoding HTML entities.

        Args:
            raw_text (str): The raw text with HTML tags and encoded entities.

            Returns:
                str: The cleaned text.
        """
        if not raw_text:
            return ""

        # Remove self-closing tags and attributes (like <br/>, <object ... />)
        raw_text = re.sub(r'<[^>]+?/>', '', raw_text)

        # Remove full HTML tags (e.g., <b>...</b>, <div>...</div>)
        raw_text = re.sub(r'<[^>]+>', '', raw_text)

        # Remove multiple consecutive whitespaces
        raw_text = re.sub(r'\s+', ' ', raw_text)

        # Decode HTML entities (e.g., &#196; to Ä)
        cleaned_text = html.unescape(raw_text)

        # Strip leading and trailing whitespace
        return cleaned_text

    def convert_to_excel(self):
        """
        Convert REQIF/XML files to Excel.
        This method performs the following steps:
        1. Changes the current working directory to the Excel folder.
        2. Iterates over the list of REQIF/XML files.
        3. For each file:
            - Loads the REQIF document.
            - Iterates over the requirements in the document.
            - Prints the requirement ID and long name.
            - Iterates over the values of each requirement.
            - Cleans the HTML content of each value.
            - Updates the value with the cleaned content.
            - Dumps the cleaned document to an Excel file.
        4. Changes back to the original working directory.
        """
        original_path = os.getcwd()
        os.chdir(self.excel_folder)

        for file in self.get_reqif_files():
            try:
                base_filename = os.path.splitext(os.path.basename(file))[0]
                reqif_document = pyreqif.reqif.load(file)

                for requirement in reqif_document.requirementList:
                    for value in requirement.values:
                        # Check for content, handling potential None values
                        content = getattr(value, '_content', None)
                        if content is not None:
                            # Decode bytes if necessary
                            if isinstance(content, bytes):
                                content = content.decode('utf-8')
                            # Clean the HTML content
                            cleaned_content = self.clean_text(content)
                            value._content = cleaned_content

                pyreqif.xlsx.dump(reqif_document,
                                  f"{base_filename}_local_conversion.xlsx")

            except Exception as e:
                print(f"Error converting {file}: {e}")

        os.chdir(original_path)

    def process(self):
        """
        Main processing method to orchestrate the entire workflow
        """
        try:
            logger.info("Starting ReqIF to Excel conversion process")
            self.prepare_folders()
            self.extract_all_files()
            self.clean_reqif_folder()
            self.convert_to_excel()
            logger.info("Conversion completed successfully")
        except Exception as e:
            logger.error(f"Error during ReqIF conversion: {str(e)}", exc_info=True)
            raise


def main(check_type):
    # Ping: Von Kunde --> Bosch (Import Check)
    if check_type == 0:
        print("\nImport Checks Active")
        source_folder = r"D:\AUDI\Test\1_LAHs_import_FROM_AUDI\2024-11-06_18-17-44-174_export"
        reqif_folder = r"D:\AUDI\Import_Reqif_Extracted"
        excel_folder = r"D:\AUDI\Import_Reqif2Excel_Converted"
        print(f"Source Folder: {source_folder}"
              f"\nreqif folder: {reqif_folder}"
              f"\nExcel storage folder: {excel_folder}"
              f"\n")

        processor_import = ReqIF2ExcelProcessor(
            source_folder=source_folder,
            reqif_folder=reqif_folder,
            excel_folder=excel_folder,
            check_type=check_type
        )
        processor_import.process()
    else:
        print("\nExport Checks Active\n")
        # PONG: Von Bosch --> Kunde (Export Check)
        source_folder = r"D:\AUDI\LAHs_Export_TO_AUDI\Export 20240620"
        reqif_folder = r"D:\AUDI\Export_Reqif_Extracted"
        excel_folder = r"D:\AUDI\Export_Reqif2Excel_Converted"
        print(f"Source Folder: {source_folder}"
              f"\nreqif folder: {reqif_folder}"
              f"\nExcel storage folder: {excel_folder}"
              f"\n")
        processor_export = ReqIF2ExcelProcessor(
            source_folder=source_folder,
            reqif_folder=reqif_folder,
            excel_folder=excel_folder,
            check_type=check_type
        )
        processor_export.process()


if __name__ == "__main__":
    # 0 Import, 1 for Export
    checkType = 0
    main(checkType)
