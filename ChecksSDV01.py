import os
import pandas as pd
from HelperFunc import HelperFunctions
from logger_config import logger


class ProjectCheckerSDV01:
    """
    Placeholder checker class for SDV01 project.

    The structure mirrors ProjectCheckerPPE / ProjectCheckerSSP:
    - Static methods per check
    - Each method returns a list of finding dicts:
      { 'Row': int, 'Attribute': str, 'Issue': str, 'Value': str }
    """

    # Import Checks

    # Check Nr.1
    @staticmethod
    def check_empty_object_id_with_forbidden_cr_status(df: pd.DataFrame, file_path: str) -> list[dict]:
        """
        Checks if 'Object ID' is empty and 'CR-Status_Bosch_SDV0.1' has forbidden values (014, 031, or 100).
        Returns findings as a list of dictionaries.
        """
        findings: list[dict] = []
        # Check for required columns
        required_columns = ['Object ID', 'CR-Status_Bosch_SDV0.1']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns in file {file_path}: {missing_columns}")
            return findings

        logger.info(f"Starting empty Object ID check (SDV01) for file: {file_path}")
        # Values are stored with a trailing comma in other projects, mirror that here.
        forbidden_status = ['014,', '031,', '100,']
        for index, row in df.iterrows():
            if pd.isna(row['Object ID']) and row['CR-Status_Bosch_SDV0.1'] in forbidden_status:
                logger.debug(
                    f"Found issue at row {index + 2}: Empty Object ID with forbidden status "
                    f"{row['CR-Status_Bosch_SDV0.1']}"
                )
                object_id = "Empty"
                findings.append({
                    'Row': index + 2,  # Excel rows start at 1; +2 accounts for header row
                    'Attribute': 'Object ID, CR-Status_Bosch_SDV0.1',
                    'Issue': (
                        "Empty 'Object ID' with forbidden 'CR-Status_Bosch_SDV0.1' value "
                        "(014, 031 or 100 are not allowed with empty Object ID)."
                    ),
                    'Value': (
                        f"Object ID: {object_id}, "
                        f"CR-Status_Bosch_SDV0.1: {row['CR-Status_Bosch_SDV0.1']}"
                    )
                })
        logger.info(f"Completed empty Object ID check (SDV01). Found {len(findings)} issues.")
        return findings
    
    # Check Nr.2
    @staticmethod
    def check_cr_status_bosch_sdv01_conditions(df: pd.DataFrame, file_path: str) -> list[dict]:
        """
        Checks if 'CR-Status_Bosch_SDV0.1' is empty or '---' while:
        - 'CR-ID_Bosch_SDV0.1' is not empty, and
        - 'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'verworfen'.
        Returns findings as a list of dictionaries.
        """
        findings: list[dict] = []

        required_columns = [
            'CR-Status_Bosch_SDV0.1',
            'CR-ID_Bosch_SDV0.1',
            'BRS_Status_Hersteller_Bosch_SDV0.1',
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            check_name = __class__.check_cr_status_bosch_sdv01_conditions.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}.\nSkipping check: {check_name}"
            )
            return findings

        for index, row in df.iterrows():
            cr_status_raw = row['CR-Status_Bosch_SDV0.1']
            cr_id_raw = row['CR-ID_Bosch_SDV0.1']
            brs_status_raw = row['BRS_Status_Hersteller_Bosch_SDV0.1']

            # Normalize BRS status for comparison (strip trailing comma)
            if pd.isna(brs_status_raw) or str(brs_status_raw).strip() == "":
                brs_status_norm = "Empty"
            else:
                brs_status_norm = str(brs_status_raw).strip().rstrip(',')

            # Determine if CR-ID is present
            cr_id_present = not (pd.isna(cr_id_raw) or str(cr_id_raw).strip() == "")

            # CR status is invalid if empty OR exactly '---' (allow comma variants via rstrip)
            if pd.isna(cr_status_raw) or str(cr_status_raw).strip() == "":
                cr_status_invalid = True
                cr_status_display = "Empty"
            else:
                cr_status_clean = str(cr_status_raw).strip().rstrip(',')
                cr_status_invalid = cr_status_clean == "---"
                cr_status_display = cr_status_raw

            if cr_status_invalid and cr_id_present and brs_status_norm != "verworfen":
                findings.append({
                    'Row': index + 2,
                    'Attribute': (
                        'CR-Status_Bosch_SDV0.1, CR-ID_Bosch_SDV0.1, '
                        'BRS_Status_Hersteller_Bosch_SDV0.1'
                    ),
                    'Issue': (
                        "'CR-Status_Bosch_SDV0.1' is empty/'---' whereas 'CR-ID_Bosch_SDV0.1' "
                        "is not empty and 'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'verworfen'."
                    ),
                    'Value': (
                        f"CR-Status_Bosch_SDV0.1: {cr_status_display}, "
                        f"CR-ID_Bosch_SDV0.1: {cr_id_raw}, "
                        f"BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status_norm}"
                    )
                })

        return findings

    # Check Nr.3
    @staticmethod
    def check_missing_release_for_verworfen_status(df: pd.DataFrame, file_path: str) -> list[dict]:
        """
        Checks rows where:
        - 'Object ID' is filled
        - 'BRS_Status_Hersteller_Bosch_SDV0.1' == 'verworfen'
        - and at least one of 'EntfallRelease' or 'ErsteinsatzRelease' is empty.

        A finding is created listing which release attributes are empty.
        """
        findings: list[dict] = []

        required_columns = [
            'Object ID',
            'BRS_Status_Hersteller_Bosch_SDV0.1',
            'EntfallRelease',
            'ErsteinsatzRelease',
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            check_name = __class__.check_missing_release_for_verworfen_status.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}.\nSkipping check: {check_name}"
            )
            return findings

        for index, row in df.iterrows():
            object_id = row['Object ID']
            brs_status_raw = row['BRS_Status_Hersteller_Bosch_SDV0.1']

            # Only consider rows with filled Object ID
            if pd.isna(object_id) or str(object_id).strip() == "":
                continue

            # Normalize BRS status
            if pd.isna(brs_status_raw) or str(brs_status_raw).strip() == "":
                brs_status_norm = "Empty"
            else:
                brs_status_norm = str(brs_status_raw).strip().rstrip(',')

            if brs_status_norm != "verworfen":
                continue

            entfall = row['EntfallRelease']
            ersteinsatz = row['ErsteinsatzRelease']

            missing_attrs = []
            if pd.isna(entfall) or str(entfall).strip() == "":
                missing_attrs.append('EntfallRelease')
            if pd.isna(ersteinsatz) or str(ersteinsatz).strip() == "":
                missing_attrs.append('ErsteinsatzRelease')

            if not missing_attrs:
                continue

            findings.append({
                'Row': index + 2,
                'Attribute': ', '.join(missing_attrs),
                'Issue': (
                    f"{', '.join(missing_attrs)} is empty while "
                    "'Object ID' is filled and "
                    "'BRS_Status_Hersteller_Bosch_SDV0.1' is 'verworfen'."
                ),
                'Value': (
                    f"Object ID: {object_id}\n"
                    f"BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status_norm}\n"
                    f"EntfallRelease: {entfall if not pd.isna(entfall) else 'Empty'}\n"
                    f"ErsteinsatzRelease: {ersteinsatz if not pd.isna(ersteinsatz) else 'Empty'}"
                )
            })

        return findings

    # Check Nr.4
    @staticmethod
    def compare_cr_id_and_brs_status_by_object_id(df: pd.DataFrame,
                                                  compare_df: pd.DataFrame,
                                                  file_path: str,
                                                  compare_file_path: str) -> list[dict]:
        """
        Compares 'CR-ID_Bosch_SDV0.1' and 'BRS_Status_Hersteller_Bosch_SDV0.1'
        between the main file (customer ReqIF) and a reference Bosch Doors export,
        matching rows by 'Object ID'.

        For each row in the main file where 'Typ' is 'Anforderung' (with or without a trailing comma):
        - Finds all rows in the reference file with the same 'Object ID'.
        - Normalizes and compares 'CR-ID_Bosch_SDV0.1' and
          'BRS_Status_Hersteller_Bosch_SDV0.1' between the two files.
        - If any difference is found in either attribute, a finding is reported.
        - 'CR-Status_Bosch_SDV0.1' is shown in the report for context but is not compared.
        """
        findings: list[dict] = []
        required_columns = [
            'Object ID',
            'CR-ID_Bosch_SDV0.1',
            'BRS_Status_Hersteller_Bosch_SDV0.1',
            'CR-Status_Bosch_SDV0.1',
            'Typ',
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_reference_columns = [col for col in required_columns if col not in compare_df.columns]

        if missing_columns:
            check_name = __class__.compare_cr_id_and_brs_status_by_object_id.__name__
            logger.warning(
                f"Warning: Missing columns in the customer DataFrame: {missing_columns}, "
                f"in File: {file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        if missing_reference_columns:
            check_name = __class__.compare_cr_id_and_brs_status_by_object_id.__name__
            logger.warning(
                f"Warning: Missing columns in the reference file: {missing_reference_columns}, "
                f"in File: {compare_file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        for index, row in df.iterrows():
            object_id = row['Object ID']
            typ_value = str(row['Typ']).rstrip(',')
            if pd.isna(object_id) or typ_value != 'Anforderung':
                continue

            # Find all rows in compare_df with the same Object ID
            ref_matches = compare_df[compare_df['Object ID'] == object_id]
            if ref_matches.empty:
                continue  # No reference to compare

            for _, ref_row in ref_matches.iterrows():
                cr_id = row['CR-ID_Bosch_SDV0.1']
                brs_status = row['BRS_Status_Hersteller_Bosch_SDV0.1']
                cr_status = row['CR-Status_Bosch_SDV0.1']

                ref_cr_id = ref_row['CR-ID_Bosch_SDV0.1']
                ref_brs_status = ref_row['BRS_Status_Hersteller_Bosch_SDV0.1']
                ref_cr_status = ref_row['CR-Status_Bosch_SDV0.1']

                # Convert NaN to 'Empty' for reporting
                cr_id_str = 'Empty' if pd.isna(cr_id) or str(cr_id).strip() == '' else cr_id
                brs_status_str = 'Empty' if pd.isna(brs_status) or str(brs_status).strip() == '' else brs_status
                cr_status_str = 'Empty' if pd.isna(cr_status) or str(cr_status).strip() == '' else cr_status

                ref_cr_id_str = 'Empty' if pd.isna(ref_cr_id) or str(ref_cr_id).strip() == '' else ref_cr_id
                ref_brs_status_str = 'Empty' if pd.isna(ref_brs_status) or str(ref_brs_status).strip() == '' else ref_brs_status
                ref_cr_status_str = 'Empty' if pd.isna(ref_cr_status) or str(ref_cr_status).strip() == '' else ref_cr_status

                # Normalize values for comparison
                norm_cr_id = HelperFunctions.normalize_text(cr_id)
                norm_ref_cr_id = HelperFunctions.normalize_text(ref_cr_id)
                norm_brs_status = str(brs_status).rstrip(',') if not pd.isna(brs_status) else ''
                norm_ref_brs_status = str(ref_brs_status).rstrip(',') if not pd.isna(ref_brs_status) else ''

                if norm_cr_id != norm_ref_cr_id or norm_brs_status != norm_ref_brs_status:
                    findings.append({
                        'Row': index + 2,
                        'Attribute': (
                            'CR-ID_Bosch_SDV0.1, '
                            'BRS_Status_Hersteller_Bosch_SDV0.1, '
                            'CR-Status_Bosch_SDV0.1'
                        ),
                        'Issue': (
                            "'CR-ID_Bosch_SDV0.1' or "
                            "'BRS_Status_Hersteller_Bosch_SDV0.1' "
                            "differs from Bosch reference file."
                        ),
                        'Value': (
                            f"Object ID: {object_id}\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Customer CR-ID_Bosch_SDV0.1: {cr_id_str}\n"
                            f"       Customer BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status_str}\n"
                            f"       Customer CR-Status_Bosch_SDV0.1: {cr_status_str}\n"
                            f"---------------\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"       Bosch CR-ID_Bosch_SDV0.1: {ref_cr_id_str}\n"
                            f"       Bosch BRS_Status_Hersteller_Bosch_SDV0.1: {ref_brs_status_str}\n"
                            f"       Bosch CR-Status_Bosch_SDV0.1: {ref_cr_status_str}"
                        )
                    })

        return findings

    # Check Nr.5
    @staticmethod
    def check_reqif_text_with_status_hersteller_bosch_sdv01(df: pd.DataFrame,
                                                            compare_df: pd.DataFrame,
                                                            file_path: str,
                                                            compare_file_path: str) -> list[dict]:
        """
        Compares the 'ReqIF.Text' attribute (customer ReqIF) with 'Object Text' (Bosch reference)
        based on 'Object ID'.

        If the text differs, 'BRS_Status_Hersteller_Bosch_SDV0.1' must be 'neu/geändert'
        (accepts values with or without trailing comma). If not, a finding is reported.
        """
        findings: list[dict] = []

        required_columns = ['Object ID', 'ReqIF.Text', 'BRS_Status_Hersteller_Bosch_SDV0.1']
        compare_required_columns = ['Object ID', 'Object Text']

        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_compare_columns = [col for col in compare_required_columns if col not in compare_df.columns]

        if missing_columns:
            check_name = __class__.check_reqif_text_with_status_hersteller_bosch_sdv01.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}.\nSkipping check: {check_name}\n\n"
            )
            return findings

        if missing_compare_columns:
            check_name = __class__.check_reqif_text_with_status_hersteller_bosch_sdv01.__name__
            logger.warning(
                f"Warning: Missing columns in the compare file: {missing_compare_columns}, "
                f"in File: {compare_file_path}.\nSkipping check: {check_name}\n\n"
            )
            return findings

        # Create a dictionary for quick lookup of 'Object Text' from compare file
        compare_dict = compare_df.set_index('Object ID')['Object Text'].to_dict()

        for index, row in df.iterrows():
            object_id = row['Object ID']
            reqif_text = row['ReqIF.Text']
            brs_status = row.get('BRS_Status_Hersteller_Bosch_SDV0.1', None)

            if pd.isna(object_id):
                continue

            if object_id not in compare_dict:
                continue

            compare_text = compare_dict[object_id]

            normalized_reqif_text = HelperFunctions.normalize_text(reqif_text)
            normalized_compare_text = HelperFunctions.normalize_text(compare_text)

            if normalized_reqif_text != normalized_compare_text:
                brs_status_clean = str(brs_status).strip().rstrip(',') if not pd.isna(brs_status) else ""
                # If text differs, status must be 'neu/geändert'
                if brs_status_clean != 'neu/geändert':
                    findings.append({
                        'Row': index + 2,
                        'Attribute': 'ReqIF.Text, BRS_Status_Hersteller_Bosch_SDV0.1',
                        'Issue': (
                            "'ReqIF.Text' differs from 'Object Text' but "
                            "'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'neu/geändert'."
                        ),
                        'Value': (
                            f"Object ID: {object_id}\n\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Customer File ReqIF.Text: {reqif_text}\n"
                            f"---------------\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"       Bosch File Object Text: {compare_text}\n"
                            f"---------------\n"
                            f"       BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status if not pd.isna(brs_status) and str(brs_status).strip() != '' else 'Empty'}\n\n"
                            f"       Expected Status: neu/geändert"
                        )
                    })

        return findings

    # Check Nr.6
    @staticmethod
    def check_object_text_with_rb_as_status(df: pd.DataFrame,
                                            compare_df: pd.DataFrame,
                                            file_path: str,
                                            compare_file_path: str) -> list[dict]:
        """
        Compares 'Object Text' in the main (Audi ReqIF) file with the compare (Bosch) file based on 'Object ID'.
        If 'Object Text' differs, 'RB_AS_Status' must NOT be one of:
        - 'accepted', 'no_req', or 'canceled_closed' (case-sensitive as in source data).

        If the text differs and RB_AS_Status is one of these prohibited values, a finding is reported.
        """
        findings: list[dict] = []

        required_columns = ['Object ID', 'Object Text', 'RB_AS_Status']
        missing_columns = [col for col in required_columns if col not in df.columns]

        compare_required_columns = ['Object ID', 'Object Text']
        missing_compare_columns = [col for col in compare_required_columns if col not in compare_df.columns]

        if missing_columns:
            check_name = __class__.check_object_text_with_rb_as_status.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}.\nSkipping check: {check_name}\n\n"
            )
            return findings

        if missing_compare_columns:
            check_name = __class__.check_object_text_with_rb_as_status.__name__
            logger.warning(
                f"Warning: Missing columns in the compare file: {missing_compare_columns}, "
                f"in File: {compare_file_path}.\nSkipping check: {check_name}\n\n"
            )
            return findings

        # Customer (Audi ReqIF) object texts indexed by Object ID
        customer_text_by_id = df.set_index('Object ID')['Object Text'].to_dict()

        # Iterate through rows in the compare (Bosch) file
        for index, row in compare_df.iterrows():
            object_id = row['Object ID']
            bosch_text = row['Object Text']
            rb_as_status = row.get('RB_AS_Status', None)

            if pd.isna(object_id):
                continue

            if object_id not in customer_text_by_id:
                continue

            customer_text = customer_text_by_id[object_id]

            # Normalize both texts
            normalized_customer_text = HelperFunctions.normalize_text(customer_text)
            normalized_bosch_text = HelperFunctions.normalize_text(bosch_text)

            if normalized_customer_text != normalized_bosch_text:
                # Only problematic when RB_AS_Status is in one of these values
                if rb_as_status in ['accepted', 'no_req', 'canceled_closed']:
                    findings.append({
                        'Row': index + 2,
                        'Attribute': 'Object Text, RB_AS_Status',
                        'Issue': (
                            "'Object Text' differs but 'RB_AS_Status' is one of the prohibited values "
                            "('accepted', 'no_req', 'canceled_closed')."
                        ),
                        'Value': (
                            f"Object ID: {object_id}\n"
                            f"---------------\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"       Bosch File Object Text: {bosch_text}\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Customer File Object Text: {customer_text}\n"
                            f"---------------\n"
                            f"       RB_AS_Status: {rb_as_status}"
                        )
                    })

        return findings

    # Check Nr.7
    @staticmethod
    def check_required_attributes_not_empty(df: pd.DataFrame,
                                            file_path: str) -> list[dict]:
        """
        Checks if required attributes are empty where BRS_Status_Hersteller_Bosch_SDV0.1 is not 'verworfen'.

        Required attributes (if present in the file):
        - 'Object ID'
        - 'Object Text'
        - 'Technikvariante'
        - 'Typ'

        The check executes if at least one required attribute is present.
        """
        findings: list[dict] = []

        all_required_columns = ['Object ID', 'Object Text', 'Technikvariante', 'Typ']
        brs_status_column = 'BRS_Status_Hersteller_Bosch_SDV0.1'

        # Which required columns actually exist?
        available_columns = [col for col in all_required_columns if col in df.columns]

        # BRS status must exist
        if brs_status_column not in df.columns:
            logger.warning(f"Missing BRS status column '{brs_status_column}' in file {file_path}")
            return findings

        # At least one required attribute must be present
        if not available_columns:
            logger.warning(
                f"None of the required attributes {all_required_columns} found in file {file_path}"
            )
            return findings

        logger.info(f"Checking available columns for emptiness (SDV01): {available_columns}")

        for index, row in df.iterrows():
            brs_status = row[brs_status_column]
            if pd.isna(brs_status) or str(brs_status).strip() == "":
                brs_status_norm = "Empty"
            else:
                brs_status_norm = str(brs_status).strip().rstrip(',')

            # Only enforce when status is not 'verworfen'
            if brs_status_norm != "verworfen":
                empty_columns = [
                    col for col in available_columns
                    if pd.isna(row[col]) or str(row[col]).strip() == ""
                ]

                if empty_columns:
                    details = []
                    if 'Object ID' in df.columns and not pd.isna(row['Object ID']):
                        details.append(f"Object ID: {row['Object ID']}")
                    details.append(f"Empty Attributes: {', '.join(empty_columns)}")
                    details.append(f"BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status_norm}")

                    findings.append({
                        'Row': index + 2,
                        'Attribute': ', '.join(empty_columns),
                        'Issue': (
                            f"{', '.join(empty_columns)} "
                            f"{'is' if len(empty_columns) == 1 else 'are'} empty while "
                            "BRS_Status_Hersteller_Bosch_SDV0.1 is not 'verworfen'."
                        ),
                        'Value': "\n".join(details)
                    })

        logger.info(
            f"Completed required attributes check (SDV01). "
            f"Found {len(findings)} issues in {len(available_columns)} available columns."
        )
        return findings

    # Check Nr.8
    @staticmethod
    def check_new_requirements_without_cr_id(df: pd.DataFrame,
                                             compare_df: pd.DataFrame,
                                             file_path: str,
                                             compare_file_path: str) -> list[dict]:
        """
        Check Nr.8: Checks for new requirements (Object IDs present in Customer but not in Bosch)
        that do not have a CR-ID assigned.

        Reports a finding for each Object ID in the customer file that:
        - Does not exist in the Bosch reference file, and
        - Has an empty CR-ID_Bosch_SDV0.1

        Parameters:
            df: The main (customer) DataFrame to check.
            compare_df: The reference (Bosch) DataFrame to compare against.
            file_path: Path to the main file (for reporting).
            compare_file_path: Path to the reference file (for reporting).

        Returns:
            list of dict: Each dict describes a finding with row number, Object ID, and details.
        """
        findings: list[dict] = []
        required_columns = ['Object ID', 'CR-ID_Bosch_SDV0.1', 'Typ']
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_reference_columns = ['Object ID'] if 'Object ID' not in compare_df.columns else []

        if missing_columns:
            check_name = __class__.check_new_requirements_without_cr_id.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        if missing_reference_columns:
            check_name = __class__.check_new_requirements_without_cr_id.__name__
            logger.warning(
                f"Warning: Missing columns in the reference file: {missing_reference_columns}, "
                f"in File: {compare_file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        bosch_object_ids = set(compare_df['Object ID'])
        for index, row in df.iterrows():
            object_id = row['Object ID']
            cr_id = row['CR-ID_Bosch_SDV0.1']
            typ = row['Typ'] if 'Typ' in row else ''

            # Check if Object ID is not in Bosch and CR-ID_Bosch_SDV0.1 is empty
            if pd.isna(object_id):
                continue

            if object_id not in bosch_object_ids and (pd.isna(cr_id) or str(cr_id).strip() == ''):
                findings.append({
                    'Row': index + 2,
                    'Attribute': 'Object ID, CR-ID_Bosch_SDV0.1',
                    'Issue': (
                        "New requirement (Object ID) found in Customer document that does not exist "
                        "in Bosch document, and CR-ID_Bosch_SDV0.1 is missing. "
                        "Hint: All new requirements should have a CR-ID assigned."
                    ),
                    'Value': (
                        f"Object ID: {object_id}\n"
                        f"Typ: {'Empty' if pd.isna(typ) or str(typ).strip() == '' else typ}\n"
                        f"---------------\n"
                        f"       Customer File Name: {os.path.basename(file_path)}\n"
                        f"       Customer CR-ID_Bosch_SDV0.1: {'Empty' if pd.isna(cr_id) or str(cr_id).strip() == '' else cr_id}\n"
                        f"---------------\n"
                        f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                        f"       Bosch Object ID: Not found"
                    )
                })

        return findings

    # Check Nr.9
    @staticmethod
    def check_cr_id_must_not_be_empty(df: pd.DataFrame, file_path: str) -> list[dict]:
        """
        Check Nr.9: Ensures CR-ID_Bosch_SDV0.1 is not empty.

        Reports a finding when:
        - CR-ID_Bosch_SDV0.1 is empty, OR
        - BRS_Status_Hersteller_Bosch_SDV0.1 = 'verworfen' AND CR-ID_Bosch_SDV0.1 is empty

        Erklärung:
        CR-ID_Bosch_SDV0.1 darf nicht leer sein.
        Wenn der Kunde eine Anforderung verwirft, darf dieser nicht ohne einen neuen CR erfolgen
        (eine verworfene Anforderung muss mit einem CR bei Bosch kommen).
        """
        findings: list[dict] = []
        required_columns = ['CR-ID_Bosch_SDV0.1', 'BRS_Status_Hersteller_Bosch_SDV0.1']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            check_name = __class__.check_cr_id_must_not_be_empty.__name__
            logger.warning(
                f"Warning: Missing columns in the DataFrame: {missing_columns}, "
                f"in File: {file_path}.\nSkipping check: {check_name}"
            )
            return findings

        for index, row in df.iterrows():
            cr_id = row['CR-ID_Bosch_SDV0.1']
            brs_status_raw = row['BRS_Status_Hersteller_Bosch_SDV0.1']

            # Normalize BRS status
            if pd.isna(brs_status_raw) or str(brs_status_raw).strip() == "":
                brs_status_norm = "Empty"
            else:
                brs_status_norm = str(brs_status_raw).strip().rstrip(',')

            # Check if CR-ID is empty
            cr_id_empty = pd.isna(cr_id) or str(cr_id).strip() == ""

            if cr_id_empty:
                # Determine issue message based on status
                if brs_status_norm == "verworfen":
                    issue_msg = (
                        "CR-ID_Bosch_SDV0.1 is empty and BRS_Status_Hersteller_Bosch_SDV0.1 is 'verworfen'. "
                        "A rejected requirement must come with a CR-ID at Bosch."
                    )
                else:
                    issue_msg = "CR-ID_Bosch_SDV0.1 must not be empty."

                findings.append({
                    'Row': index + 2,
                    'Attribute': 'CR-ID_Bosch_SDV0.1, BRS_Status_Hersteller_Bosch_SDV0.1',
                    'Issue': issue_msg,
                    'Value': (
                        f"CR-ID_Bosch_SDV0.1: Empty\n"
                        f"BRS_Status_Hersteller_Bosch_SDV0.1: {brs_status_norm}"
                    )
                })

        return findings

    # Check Nr.10
    @staticmethod
    def check_cr_status_overwrite_protection(df: pd.DataFrame,
                                             compare_df: pd.DataFrame,
                                             file_path: str,
                                             compare_file_path: str) -> list[dict]:
        """
        Check Nr.10: Prevents overwriting Bosch CR-Status when it is 100 or 31.

        Compares 'CR-Status_Bosch_SDV0.1' between customer and Bosch files (matched by Object ID).
        Reports a finding when:
        - Bosch file has 'CR-Status_Bosch_SDV0.1' = '100' or '31' (with or without trailing comma), and
        - Customer file has a different 'CR-Status_Bosch_SDV0.1' value

        Erklärung:
        Wenn der CR-ID vorhanden ist, und bei Bosch CR-Status 31 oder 100 ist,
        dann darf der CR-Status nicht mit neuem CR-Status überschrieben werden.
        """
        findings: list[dict] = []
        required_columns = ['Object ID', 'CR-Status_Bosch_SDV0.1', 'CR-ID_Bosch_SDV0.1']
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_reference_columns = ['Object ID', 'CR-Status_Bosch_SDV0.1']
        missing_reference_columns = [col for col in missing_reference_columns if col not in compare_df.columns]

        if missing_columns:
            check_name = __class__.check_cr_status_overwrite_protection.__name__
            logger.warning(
                f"Warning: Missing columns in the customer DataFrame: {missing_columns}, "
                f"in File: {file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        if missing_reference_columns:
            check_name = __class__.check_cr_status_overwrite_protection.__name__
            logger.warning(
                f"Warning: Missing columns in the reference file: {missing_reference_columns}, "
                f"in File: {compare_file_path}. Skipping check: {check_name}\n\n"
            )
            return findings

        for index, row in df.iterrows():
            object_id = row['Object ID']
            cr_id = row['CR-ID_Bosch_SDV0.1']
            customer_cr_status = row['CR-Status_Bosch_SDV0.1']

            # Skip if Object ID is empty
            if pd.isna(object_id):
                continue

            # Only check if CR-ID is present (as per explanation)
            if pd.isna(cr_id) or str(cr_id).strip() == "":
                continue

            # Find all rows in compare_df with the same Object ID
            ref_matches = compare_df[compare_df['Object ID'] == object_id]
            if ref_matches.empty:
                continue  # No reference to compare

            for _, ref_row in ref_matches.iterrows():
                bosch_cr_status = ref_row['CR-Status_Bosch_SDV0.1']

                # Normalize Bosch CR-Status (strip trailing comma and whitespace)
                if pd.isna(bosch_cr_status) or str(bosch_cr_status).strip() == "":
                    bosch_cr_status_norm = ""
                else:
                    bosch_cr_status_norm = str(bosch_cr_status).strip().rstrip(',')

                # Check if Bosch status is 100 or 31
                if bosch_cr_status_norm not in ['100', '31']:
                    continue  # Not a protected status, skip

                # Normalize customer CR-Status for comparison
                if pd.isna(customer_cr_status) or str(customer_cr_status).strip() == "":
                    customer_cr_status_norm = ""
                else:
                    customer_cr_status_norm = str(customer_cr_status).strip().rstrip(',')

                # If customer status differs from Bosch status, report finding
                if customer_cr_status_norm != bosch_cr_status_norm:
                    customer_cr_status_str = 'Empty' if pd.isna(customer_cr_status) or str(customer_cr_status).strip() == '' else customer_cr_status
                    bosch_cr_status_str = 'Empty' if pd.isna(bosch_cr_status) or str(bosch_cr_status).strip() == '' else bosch_cr_status

                    findings.append({
                        'Row': index + 2,
                        'Attribute': 'CR-Status_Bosch_SDV0.1',
                        'Issue': (
                            "'CR-Status_Bosch_SDV0.1' differs from Bosch file. "
                            "Bosch CR-Status is '100' or '31' and should not be overwritten."
                        ),
                        'Value': (
                            f"Object ID: {object_id}\n"
                            f"CR-ID_Bosch_SDV0.1: {cr_id}\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Customer CR-Status_Bosch_SDV0.1: {customer_cr_status_str}\n"
                            f"---------------\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"       Bosch CR-Status_Bosch_SDV0.1: {bosch_cr_status_str}\n"
                            f"---------------\n"
                            f"       Note: Bosch CR-Status '100' or '31' must not be overwritten."
                        )
                    })

        return findings

    @staticmethod
    def import_checks(df: pd.DataFrame,
                      file_path: str,
                      compare_df: pd.DataFrame | None = None,
                      compare_file_path: str | None = None) -> list[dict]:
        """
        Entry point for SDV01 import checks.
        Executes all SDV01 import checks and aggregates their findings.
        """
        logger.info(f"Running SDV01 import checks for file: {os.path.basename(file_path)}")
        findings: list[dict] = []

        # Check Nr.1
        findings += ProjectCheckerSDV01.check_empty_object_id_with_forbidden_cr_status(df, file_path)

        # Check Nr.2
        findings += ProjectCheckerSDV01.check_cr_status_bosch_sdv01_conditions(df, file_path)

        # Check Nr.3
        findings += ProjectCheckerSDV01.check_missing_release_for_verworfen_status(df, file_path)

        # Check Nr.4 – requires reference file
        if compare_df is not None and compare_file_path is not None:
            findings += ProjectCheckerSDV01.compare_cr_id_and_brs_status_by_object_id(
                df, compare_df, file_path, compare_file_path
            )

            # Check Nr.5 – requires reference file
            findings += ProjectCheckerSDV01.check_reqif_text_with_status_hersteller_bosch_sdv01(
                df, compare_df, file_path, compare_file_path
            )

            # Check Nr.6 – requires reference file
            findings += ProjectCheckerSDV01.check_object_text_with_rb_as_status(
                df, compare_df, file_path, compare_file_path
            )

            # Check Nr.10 – requires reference file
            findings += ProjectCheckerSDV01.check_cr_status_overwrite_protection(
                df, compare_df, file_path, compare_file_path
            )

        # Check Nr.7 – does not require reference file
        findings += ProjectCheckerSDV01.check_required_attributes_not_empty(df, file_path)

        # Check Nr.8 – requires reference file
        if compare_df is not None and compare_file_path is not None:
            findings += ProjectCheckerSDV01.check_new_requirements_without_cr_id(
                df, compare_df, file_path, compare_file_path
            )

        # Check Nr.9 – does not require reference file
        findings += ProjectCheckerSDV01.check_cr_id_must_not_be_empty(df, file_path)

        return findings

    # Export Checks

    @staticmethod
    def export_checks(df: pd.DataFrame,
                      file_path: str,
                      compare_df: pd.DataFrame | None = None,
                      compare_file_path: str | None = None) -> list[dict]:
        """
        Entry point for SDV01 export checks.
        Currently returns an empty list; real checks will be added later.
        """
        logger.info(f"Running SDV01 export checks for file: {os.path.basename(file_path)}")
        findings: list[dict] = []
        # TODO: implement SDV01 export checks
        return findings

