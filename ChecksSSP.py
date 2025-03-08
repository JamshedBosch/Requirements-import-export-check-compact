import os
import pandas as pd
from HelperFunc import HelperFunctions
from logger_config import logger


class ProjectCheckerSSP:
    """Import Checks """

    # Check Nr.6
    @staticmethod
    def check_object_text_with_status_oem_zu_lieferant_r(df, compare_df,
                                                           file_path, compare_file_path):
        """
        Compares the 'ReqIF.Text' attribute with 'Object Text' attribute from a compare file.
        If 'Object Text' differs from 'ReqIF.Text', ensure 'Status OEM zu Lieferant R' is 'zu bewerten'.
        Handles cases where the identifier is either 'ReqIF.ForeignID' or 'Object ID'.
        Logs findings if the condition is not met.
        """
        findings = []
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        logger.info(f"Starting text comparison check between {file_path} and {compare_file_path}")
        logger.debug(f"Using identifier columns: {identifier_col} and {compare_identifier_col}")

        required_columns = ['ReqIF.Text', identifier_col,
                            'Status OEM zu Lieferant R']
        compare_required_columns = ['Object Text', compare_identifier_col]

        # Check for missing columns in both DataFrames
        missing_columns = [col for col in required_columns if
                           col not in df.columns]
        missing_compare_columns = [col for col in compare_required_columns if
                                   col not in compare_df.columns]

        # # Ensure required columns exist in both DataFrames
        # required_columns = ['ReqIF.Text', 'ReqIF.ForeignID',
        #                     'Status OEM zu Lieferant R', 'Object Text',
        #                     'ForeignID']
        # missing_columns = [col for col in required_columns[:3] if
        #                    col not in df.columns]
        # missing_compare_columns = [col for col in required_columns[3:] if
        #                            col not in compare_df.columns]

        if missing_columns or missing_compare_columns:
            logger.warning(f"Missing columns in files:")
            if missing_columns:
                logger.warning(f"Customer file: {missing_columns}")
            if missing_compare_columns:
                logger.warning(f"Compare file: {missing_compare_columns}")
            return findings

        # Create a dictionary for quick lookup of 'Object Text' from compare file
        compare_dict = compare_df.set_index(compare_identifier_col)[
            'Object Text'].to_dict()

        # Iterate through rows in the main DataFrame
        for index, row in df.iterrows():
            object_id = row[identifier_col]
            object_text = row['ReqIF.Text']
            oem_status = row.get('Status OEM zu Lieferant R', None)
            if pd.isna(oem_status):
                oem_status = "Empty"

            # Skip rows with missing 'Object ID'
            if pd.isna(object_id):
                continue

            # Check if the 'Object ID' exists in the compare file
            if object_id in compare_dict:
                compare_text = compare_dict[object_id]

                # Convert to string and strip whitespace
                object_text_str = str(object_text) if not pd.isna(
                    object_text) else ""
                compare_text_str = str(compare_text) if not pd.isna(
                    compare_text) else ""
                object_text_str = object_text_str.strip()
                compare_text_str = compare_text_str.strip()

                # Skip only if both texts are empty
                if not object_text_str and not compare_text_str:
                    continue

                # Normalize both object_text and compare_text
                normalized_object_text = HelperFunctions.normalize_text(
                    object_text_str)
                normalized_compare_text = HelperFunctions.normalize_text(
                    compare_text_str)
                if normalized_object_text != normalized_compare_text:
                    if oem_status not in ['zu bewerten,']:
                        findings.append({
                            'Row': index + 2,  # Adjust for Excel row numbering
                            'Attribute': 'ReqIF.Text, Status OEM zu Lieferant R',
                            'Issue': (
                                f"'ReqIF.Text' differs from 'Object Text' but 'Status OEM zu Lieferant R' is not 'zu bewerten'."
                            ),
                            'Value': (
                                f"{identifier_col}: {object_id}\n\n"
                                f"---------------\n"
                                f"       Customer File Name: {os.path.basename(file_path)}\n"
                                f"       Customer File Object Text: {object_text_str}\n"
                                f"---------------\n"
                                f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                                f"       Bosch File Object Text: {compare_text_str}\n"
                                f"---------------\n"
                                f"       Status OEM zu Lieferant R: {oem_status}"
                            )
                        })

        return findings

    # Check Nr.8
    @staticmethod
    def check_multiple_attributes_with_status_oem_zu_lieferant_r(df,
                                                                 compare_df,
                                                                 file_path,
                                                                 compare_file_path):
        """
        Compares multiple attributes between customer file and Bosch file:
        - 'ReqIF.Category' with 'Category'
        - 'ASIL' with 'RB_ASIL'
        - 'Reifegrad' with 'Reifegrad'
        - 'Feature' with 'Feature'
        - 'Sonstige-Varianten' with 'Sonstige-Varianten'

        If any of these attributes differ, ensures 'Status OEM zu Lieferant R' is 'zu bewerten'.
        Handles cases where the identifier is either 'ReqIF.ForeignID' or 'Object ID'.
        Thoroughly normalizes text by replacing commas with spaces, removing extra spaces,
        and comparing the same items regardless of order or separator style.
        Logs findings if the condition is not met with a simplified format showing only differing attributes.
        """
        findings = []
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        # Define attribute pairs to compare (customer file attribute, Bosch file attribute)
        attribute_pairs = [
            ('ReqIF.Category', 'Category'),
            # Switched ASIL vs RB_ASIL OFF since they are empty at the moment, later will be switched ON
            # ('ASIL', 'RB_ASIL'),
            ('Reifegrad', 'Reifegrad'),
            ('Feature', 'Feature'),
            ('Sonstige-Varianten', 'Sonstige-Varianten')
        ]

        # Validate all required columns exist in customer file
        customer_required_cols = [identifier_col,
                                  'Status OEM zu Lieferant R'] + [pair[0] for
                                                                  pair in
                                                                  attribute_pairs]
        missing_customer_cols = [col for col in customer_required_cols if
                                 col not in df.columns]

        # Validate all required columns exist in Bosch file
        bosch_required_cols = [compare_identifier_col] + [pair[1] for pair in
                                                          attribute_pairs]
        missing_bosch_cols = [col for col in bosch_required_cols if
                              col not in compare_df.columns]

        # Handle missing columns
        if missing_customer_cols:
            check_name = __class__.check_multiple_attributes_with_status_oem_zu_lieferant_r.__name__
            print(
                f"Warning: Missing columns in the customer DataFrame: {missing_customer_cols}, in File: {file_path}.\nSkipping check: {check_name}")
            return findings

        if missing_bosch_cols:
            check_name = __class__.check_multiple_attributes_with_status_oem_zu_lieferant_r.__name__
            print(
                f"Warning: Missing columns in the Bosch file: {missing_bosch_cols}.\nSkipping check: {check_name}")
            return findings

        # Create dictionary mappings for each Bosch attribute for quick lookup
        compare_dicts = {}
        for _, bosch_attr in attribute_pairs:
            compare_dicts[bosch_attr] = \
            compare_df.set_index(compare_identifier_col)[bosch_attr].to_dict()

        # Thoroughly normalize text for comparison
        def normalize_for_comparison(text):
            if pd.isna(text) or text is None:
                return set()

            # Convert to string and strip whitespace
            text_str = str(text).strip()
            if not text_str:
                return set()

            # Replace commas with spaces
            text_str = text_str.replace(',', ' ')

            # Replace multiple spaces with a single space
            while '  ' in text_str:
                text_str = text_str.replace('  ', ' ')

            # Split by space, trim each item, and filter out empty strings
            items = [item.strip() for item in text_str.split(' ') if
                     item.strip()]

            # Return as a set for order-independent comparison
            return set(items)

        # Iterate through rows in the customer DataFrame
        for index, row in df.iterrows():
            object_id = row[identifier_col]
            oem_status = row.get('Status OEM zu Lieferant R', None)
            if pd.isna(oem_status):
                oem_status = "Empty"

            # Skip rows with missing identifier
            if pd.isna(object_id):
                continue

            # Check if the object ID exists in the Bosch file
            if object_id in compare_dicts[attribute_pairs[0][
                1]]:  # Check using the first attribute's dictionary
                # Flag to track if any attribute differs
                any_attribute_differs = False
                # Store attribute differences for reporting
                diff_details = []

                # Check each attribute pair
                for customer_attr, bosch_attr in attribute_pairs:
                    customer_value = row.get(customer_attr, None)
                    bosch_value = compare_dicts[bosch_attr].get(object_id,
                                                                None)

                    # Skip comparison if both values are empty
                    if (pd.isna(customer_value) or str(
                            customer_value).strip() == "") and \
                            (pd.isna(bosch_value) or str(
                                bosch_value).strip() == ""):
                        continue

                    # Get original string values for display
                    customer_value_str = str(
                        customer_value).strip() if not pd.isna(
                        customer_value) else ""
                    bosch_value_str = str(bosch_value).strip() if not pd.isna(
                        bosch_value) else ""

                    # Check if values are equivalent after normalization
                    if normalize_for_comparison(
                            customer_value) != normalize_for_comparison(
                            bosch_value):
                        any_attribute_differs = True
                        diff_details.append({
                            'Attribute': customer_attr,
                            'Customer Value': customer_value_str,
                            'Bosch Attribute': bosch_attr,
                            'Bosch Value': bosch_value_str
                        })

                # If any attribute differs and status is not 'zu bewerten', add to findings
                if any_attribute_differs and oem_status not in ['zu bewerten']:
                    # Create differing attributes list for the 'Attribute' field
                    different_attrs = [
                        f"{d['Attribute']} vs {d['Bosch Attribute']}" for d in
                        diff_details]
                    attribute_list = ", ".join(different_attrs)

                    # Create detailed comparison text for only the differing attributes
                    attribute_details = ""
                    for detail in diff_details:
                        attribute_details += (
                            f"       Customer Attribute: {detail['Attribute']}\n"
                            f"       Customer Attribute Value : {detail['Customer Value']}\n\n"
                            f"       Bosch Attribute : {detail['Bosch Attribute']}\n"
                            f"       Bosch Attribute Value : {detail['Bosch Value']}\n\n"
                        )

                    findings.append({
                        'Row': index + 2,  # Adjust for Excel row numbering
                        'Attribute': attribute_list,
                        'Issue': "Attributes differ but 'Status OEM zu Lieferant R' is not 'zu bewerten'.",
                        'Value': (
                            f"{identifier_col}: {object_id}\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"---------------\n"
                            f"Attribute Comparison:\n{attribute_details.rstrip()}\n\n"
                            f"---------------\n"
                            f"       Status OEM zu Lieferant R: {oem_status}\n\n"
                            f"       Expected Status: zu bewerten"
                        )
                    })

        return findings