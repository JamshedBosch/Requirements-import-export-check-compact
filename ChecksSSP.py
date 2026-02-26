import os
import pandas as pd
from HelperFunc import HelperFunctions
from logger_config import logger
import re


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
        Ignores differences in special symbols (e.g., σ vs s, Δ vs ?).
        Ignores items with ReqIF.Category/Typ 'Überschrift' or 'Information'.
        Logs findings if the condition is not met.
        """
        findings = []
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        logger.info(f"[CHECK NR.6 START] Text comparison (ReqIF.Text vs Object Text) | File: {file_path}")
        logger.debug(f"Using identifier columns: {identifier_col} and {compare_identifier_col}")

        # Check which category/type column exists
        category_col = 'ReqIF.Category' if 'ReqIF.Category' in df.columns else 'Typ'

        required_columns = ['ReqIF.Text', identifier_col,
                            'Status OEM zu Lieferant R', category_col]
        compare_required_columns = ['Object Text', compare_identifier_col]

        # Check for missing columns in both DataFrames
        missing_columns = [col for col in required_columns if
                           col not in df.columns]
        missing_compare_columns = [col for col in compare_required_columns if
                                   col not in compare_df.columns]

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
            category = row.get(category_col, None)
            
            if pd.isna(oem_status):
                oem_status = "Empty"
            
            # Skip rows with missing 'Object ID'
            if pd.isna(object_id):
                continue

            # Skip if category is 'Überschrift' or 'Information'
            if not pd.isna(category):
                category = str(category).rstrip(',').strip()
                if category in ['Überschrift', 'Information']:
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

                # Normalize special symbols in both texts
                object_text_str = HelperFunctions.normalize_symbols(object_text_str)
                compare_text_str = HelperFunctions.normalize_symbols(compare_text_str)

                # Clean OLE Object artifacts before strict normalization
                cleaned_object_text = HelperFunctions.clean_ole_object_text(object_text_str)
                cleaned_compare_text = HelperFunctions.clean_ole_object_text(compare_text_str)

                # Normalize both object_text and compare_text
                normalized_object_text = HelperFunctions.normalize_text(cleaned_object_text)
                normalized_compare_text = HelperFunctions.normalize_text(cleaned_compare_text)
                if normalized_object_text != normalized_compare_text:
                    # Strip any trailing comma from oem_status for comparison
                    oem_status_clean = oem_status.rstrip(',')
                    if oem_status_clean not in ['zu bewerten', 'verworfen']:
                        category_str = 'Empty' if pd.isna(category) or str(category).strip() == '' else str(category).rstrip(',')
                        findings.append({
                            'Row': index + 2,  # Adjust for Excel row numbering
                            'Check Number': 'Nr.6',
                            'Object ID': str(object_id),
                            'Attribute': 'ReqIF.Text, Status OEM zu Lieferant R',
                            'Issue': (
                                f"'ReqIF.Text' differs from 'Object Text' but 'Status OEM zu Lieferant R' is not 'zu bewerten."
                            ),
                            'Value': (
                                f"Object ID: {object_id}\n"
                                f"Typ: {category_str}\n"
                                f"\n"
                                f"---------------\n"
                                f"       Customer File Name: {os.path.basename(file_path)}\n"
                                f"       Customer File Object Text: {object_text_str}\n"
                                f"---------------\n"
                                f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                                f"       Bosch File Object Text: {compare_text_str}\n"
                                f"---------------\n"
                                f"       Status OEM zu Lieferant R: {oem_status}\n\n"
                                f"       Expected Status: zu bewerten"

                            )
                        })

        logger.info(f"[CHECK NR.6 END] Found {len(findings)} findings.")
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
        Ignores items with ReqIF.Category/Typ 'Überschrift' or 'Information'.
        Thoroughly normalizes text by replacing commas with spaces, removing extra spaces,
        and comparing the same items regardless of order or separator style.
        Logs findings if the condition is not met with a simplified format showing only differing attributes.
        """
        findings = []
        logger.info(f"[CHECK NR.8 START] Multiple attributes comparison (ReqIF.Category, ASIL, Reifegrad, Typ) | File: {file_path}")
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        # Check which category/type column exists
        category_col = 'ReqIF.Category' if 'ReqIF.Category' in df.columns else 'Typ'

        # Define full attribute pairs for ReqIF.Category files
        full_attribute_pairs = [
            ('Reifegrad', 'Reifegrad'),
            ('Feature', 'Feature'),
            ('Sonstige-Varianten', 'Sonstige-Varianten')
        ]

        # Helper function for ASIL comparison
        def compare_asil_values(customer_asil, bosch_asil):
            # Strip trailing commas and whitespace
            customer_asil = str(customer_asil).rstrip(',').strip() if not pd.isna(customer_asil) else ""
            bosch_asil = str(bosch_asil).rstrip(',').strip() if not pd.isna(bosch_asil) else ""
            
            # Check if customer ASIL is in the special case values
            is_customer_special = customer_asil.lower() in ['n/a', 'qm', 'nein', 'tbd', '']
            # Check if Bosch ASIL is in the allowed values for special case
            is_bosch_allowed = bosch_asil.lower() in ['tbd', 'n/a', 'qm', '']
            
            # No finding needed if customer is special case and Bosch is allowed value
            if is_customer_special and is_bosch_allowed:
                return False
                
            # Finding needed if customer is not special case and values differ
            return not is_customer_special and customer_asil.lower() != bosch_asil.lower()

        # Initialize attribute pairs with ASIL check if columns exist
        attribute_pairs = []
        
        # Add ASIL check if columns exist
        if 'ASIL' in df.columns and 'ASIL' in compare_df.columns:
            attribute_pairs.append(('ASIL', 'ASIL'))
            logger.debug("ASIL check enabled - found ASIL columns in both files")
        else:
            if 'ASIL' not in df.columns:
                logger.warning("ASIL column not found in customer file")
            if 'ASIL' not in compare_df.columns:
                logger.warning("ASIL column not found in Bosch file")

        # Add ReqIF.Category or Typ if they exist
        if 'ReqIF.Category' in df.columns:
            logger.debug("Using ReqIF.Category vs Category comparison with all attributes")
            attribute_pairs.append(('ReqIF.Category', 'Category'))
            # For ReqIF.Category files, add all other attributes
            attribute_pairs.extend(full_attribute_pairs)
        elif 'Typ' in df.columns:
            logger.debug("Using Typ vs Typ comparison only")
            attribute_pairs.append(('Typ', 'Typ'))  # Only check Typ when it's a Typ file
        else:
            logger.warning("Neither 'ReqIF.Category' nor 'Typ' column found in customer file")
            # If neither exists, check remaining attributes
            attribute_pairs.extend(full_attribute_pairs)
        
        if not attribute_pairs:
            logger.warning("No attributes found to check")
            return findings  # Return empty findings only if there are truly no attributes to check

        # Validate all required columns exist in customer file
        customer_required_cols = [identifier_col, 'Status OEM zu Lieferant R', category_col] + [pair[0] for pair in attribute_pairs]
        missing_customer_cols = [col for col in customer_required_cols if col not in df.columns]

        # Validate all required columns exist in Bosch file
        bosch_required_cols = [compare_identifier_col] + [pair[1] for pair in attribute_pairs]
        missing_bosch_cols = [col for col in bosch_required_cols if col not in compare_df.columns]

        # Handle missing required columns
        if missing_customer_cols:
            check_name = __class__.check_multiple_attributes_with_status_oem_zu_lieferant_r.__name__
            logger.warning(
                f"Missing required columns in the customer DataFrame: {missing_customer_cols}, in File: {file_path}.\nSkipping check: {check_name}")
            return findings

        if missing_bosch_cols:
            check_name = __class__.check_multiple_attributes_with_status_oem_zu_lieferant_r.__name__
            logger.warning(
                f"Missing required columns in the Bosch file: {missing_bosch_cols}.\nSkipping check: {check_name}")
            return findings

        # Remove ASIL from attribute pairs if either ASIL column is missing
        if 'ASIL' in missing_customer_cols or 'ASIL' in missing_bosch_cols:
            attribute_pairs = [pair for pair in attribute_pairs if pair != ('ASIL', 'ASIL')]
            logger.warning("ASIL comparison disabled due to missing ASIL columns")

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
            category = row.get(category_col, None)
            
            if pd.isna(oem_status):
                oem_status = "Empty"

            # Skip rows with missing identifier
            if pd.isna(object_id):
                continue

            # Skip if category is 'Überschrift' or 'Information'
            if not pd.isna(category):
                category = str(category).rstrip(',').strip()
                if category in ['Überschrift', 'Information']:
                    continue

            # Clean up oem_status by stripping trailing comma
            oem_status = str(row.get('Status OEM zu Lieferant R', '')).rstrip(',')
            if pd.isna(oem_status) or oem_status == "":
                oem_status = "Empty"

            # Check if the object ID exists in the Bosch file
            if object_id in compare_dicts[attribute_pairs[0][1]]:  # Check using the first attribute's dictionary
                # Flag to track if any attribute differs
                any_attribute_differs = False
                # Store attribute differences for reporting
                diff_details = []

                # Check each attribute pair
                for customer_attr, bosch_attr in attribute_pairs:
                    customer_value = row.get(customer_attr, None)
                    bosch_value = compare_dicts[bosch_attr].get(object_id, None)

                    # Special handling for ASIL comparison
                    if customer_attr == 'ASIL' and bosch_attr == 'ASIL':
                        if compare_asil_values(customer_value, bosch_value):
                            any_attribute_differs = True
                            diff_details.append({
                                'Attribute': customer_attr,
                                'Customer Value': str(customer_value).rstrip(',').strip() if not pd.isna(customer_value) else "",
                                'Bosch Attribute': bosch_attr,
                                'Bosch Value': str(bosch_value).rstrip(',').strip() if not pd.isna(bosch_value) else ""
                            })
                        continue

                    # Skip comparison if both values are empty
                    if (pd.isna(customer_value) or str(customer_value).strip() == "") and \
                            (pd.isna(bosch_value) or str(bosch_value).strip() == ""):
                        continue

                    # Get original string values for display
                    customer_value_str = str(customer_value).strip() if not pd.isna(customer_value) else ""
                    bosch_value_str = str(bosch_value).strip() if not pd.isna(bosch_value) else ""

                    # Check if values are equivalent after normalization
                    if normalize_for_comparison(customer_value) != normalize_for_comparison(bosch_value):
                        any_attribute_differs = True
                        diff_details.append({
                            'Attribute': customer_attr,
                            'Customer Value': customer_value_str,
                            'Bosch Attribute': bosch_attr,
                            'Bosch Value': bosch_value_str
                        })

                # If any attribute differs and status is not 'zu bewerten', add to findings
                if any_attribute_differs and oem_status not in ['zu bewerten', 'verworfen']:
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

                    # Display status as "Empty" if it's nan or empty string
                    display_status = "Empty" if pd.isna(row.get('Status OEM zu Lieferant R')) or str(row.get('Status OEM zu Lieferant R', '')).strip() == "" else oem_status

                    category_str = 'Empty' if pd.isna(category) or str(category).strip() == '' else str(category).rstrip(',')
                    findings.append({
                        'Row': index + 2,  # Adjust for Excel row numbering
                        'Check Number': 'Nr.8',
                        'Object ID': str(object_id),
                        'Attribute': attribute_list,
                        'Issue': "Attributes differ but 'Status OEM zu Lieferant R' is not 'zu bewerten'.",
                        'Value': (
                            f"Object ID: {object_id}\n"
                            f"Typ: {category_str}\n"
                            f"\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"---------------\n"
                            f"Attribute Comparison:\n{attribute_details.rstrip()}\n\n"
                            f"---------------\n"
                            f"       Status OEM zu Lieferant R: {display_status}\n\n"
                            f"       Expected Status: zu bewerten"
                        )
                    })

        logger.info(f"[CHECK NR.8 END] Found {len(findings)} findings.")
        return findings

    # Check Nr.9
    @staticmethod
    def check_quelle_with_status_oem_zu_lieferant_r(df, compare_df, file_path, compare_file_path):
        """
        Compares 'Quelle' attribute between customer and Bosch files.
        If 'Quelle' differs, ensures 'Status OEM zu Lieferant R' is 'zu bewerten'.
        Ignores items with ReqIF.Category/Typ 'Überschrift' or 'Information'.
        Returns findings as a list of dictionaries.
        """
        findings = []
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        # Check which category/type column exists
        category_col = 'ReqIF.Category' if 'ReqIF.Category' in df.columns else 'Typ'

        logger.info(f"[CHECK NR.9 START] Quelle comparison | File: {file_path}")
        logger.debug(f"Using identifier columns: {identifier_col} and {compare_identifier_col}")

        # Check for required columns
        required_columns = ['Quelle', identifier_col, 'Status OEM zu Lieferant R', category_col]
        compare_required_columns = ['Quelle', compare_identifier_col]

        # Check for missing columns in both DataFrames
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_compare_columns = [col for col in compare_required_columns if col not in compare_df.columns]

        if missing_columns or missing_compare_columns:
            logger.warning(f"Missing columns in files:")
            if missing_columns:
                logger.warning(f"Customer file: {missing_columns}")
            if missing_compare_columns:
                logger.warning(f"Compare file: {missing_compare_columns}")
            return findings

        # Create a dictionary for quick lookup of 'Quelle' from compare file
        compare_dict = compare_df.set_index(compare_identifier_col)['Quelle'].to_dict()

        # Iterate through rows in the main DataFrame
        for index, row in df.iterrows():
            object_id = row[identifier_col]
            quelle = row['Quelle']
            oem_status = row.get('Status OEM zu Lieferant R', None)
            category = row.get(category_col, None)
            
            if pd.isna(oem_status):
                oem_status = "Empty"
            else:
                oem_status = str(oem_status).rstrip(',')

            # Skip rows with missing 'Object ID'
            if pd.isna(object_id):
                continue

            # Skip if category is 'Überschrift' or 'Information'
            if not pd.isna(category):
                category = str(category).rstrip(',').strip()
                if category in ['Überschrift', 'Information']:
                    continue

            # Check if the 'Object ID' exists in the compare file
            if object_id in compare_dict:
                compare_quelle = compare_dict[object_id]

                # Convert to string and strip whitespace
                quelle_str = str(quelle) if not pd.isna(quelle) else ""
                compare_quelle_str = str(compare_quelle) if not pd.isna(compare_quelle) else ""
                quelle_str = quelle_str.strip()
                compare_quelle_str = compare_quelle_str.strip()

                # Skip only if both Quelle values are empty
                if not quelle_str and not compare_quelle_str:
                    continue

                # Normalize both Quelle values
                normalized_quelle = HelperFunctions.normalize_text(quelle_str)
                normalized_compare_quelle = HelperFunctions.normalize_text(compare_quelle_str)

                if normalized_quelle != normalized_compare_quelle:
                    if oem_status not in ['zu bewerten,', 'verworfen,']:
                        category_str = 'Empty' if pd.isna(category) or str(category).strip() == '' else str(category).rstrip(',')
                        findings.append({
                            'Row': index + 2,  # Adjust for Excel row numbering
                            'Check Number': 'Nr.9',
                            'Object ID': str(object_id),
                            'Attribute': 'Quelle, Status OEM zu Lieferant R',
                            'Issue': (
                                f"'Quelle' differs between files but 'Status OEM zu Lieferant R' is not 'zu bewerten'."
                            ),
                            'Value': (
                                f"Object ID: {object_id}\n"
                                f"Typ: {category_str}\n"
                                f"\n"
                                f"---------------\n"
                                f"       Customer File Name: {os.path.basename(file_path)}\n"
                                f"       Customer Attribute: Quelle\n"
                                f"          Atrribute Value: {quelle_str}\n"
                                f"---------------\n"
                                f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                                f"       Bosch Attribute: Quelle\n"
                                f"       Attribute Value: {compare_quelle_str}\n"
                                f"---------------\n"
                                f"       Status OEM zu Lieferant R: {oem_status}\n\n"
                                f"       Expected Status: zu bewerten"
                            )
                        })

        logger.info(f"[CHECK NR.9 END] Found {len(findings)} findings.")
        return findings

    # Check Nr.10
    @staticmethod
    def check_text_differences_without_status_validation(df, compare_df, file_path, compare_file_path):
        """
        Compares 'ReqIF.Text' from customer file with 'Object Text' from Bosch file.
        Reports any differences found, regardless of 'Status OEM zu Lieferant R' value.
        Ignores differences in embedded objects (images, .wmf files, etc.).
        Skips findings if 'Status OEM zu Lieferant R' is 'verworfen'.
        Uses the same text normalization as Check Nr. 6.
        Returns findings as a list of dictionaries.
        """
        findings = []
        # Determine the identifier column dynamically
        identifier_col = 'ReqIF.ForeignID' if 'ReqIF.ForeignID' in df.columns else 'Object ID'
        compare_identifier_col = 'ForeignID' if 'ForeignID' in compare_df.columns else 'Object ID'

        # Check which category/type column exists
        category_col = 'ReqIF.Category' if 'ReqIF.Category' in df.columns else 'Typ'

        logger.info(f"[CHECK NR.10 START] Text differences without status validation (ReqIF.Text vs Object Text) | File: {file_path}")
        logger.debug(f"Using identifier columns: {identifier_col} and {compare_identifier_col}")

        # Check for required columns
        required_columns = ['ReqIF.Text', identifier_col, 'Status OEM zu Lieferant R', category_col]
        compare_required_columns = ['Object Text', compare_identifier_col]

        # Check for missing columns in both DataFrames
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_compare_columns = [col for col in compare_required_columns if col not in compare_df.columns]

        if missing_columns or missing_compare_columns:
            logger.warning(f"Missing columns in files:")
            if missing_columns:
                logger.warning(f"Customer file: {missing_columns}")
            if missing_compare_columns:
                logger.warning(f"Compare file: {missing_compare_columns}")
            return findings

        # Create a dictionary for quick lookup of 'Object Text' from compare file
        compare_dict = compare_df.set_index(compare_identifier_col)['Object Text'].to_dict()

        # Function to remove embedded object references
        def remove_embedded_objects(text):
            if not isinstance(text, str):
                return text
            # Remove embedded object references (images, .wmf files, etc.)
            text = re.sub(r'Embedded object:.*?\.(png|wmf|jpg|jpeg|gif)', '', text)
            return text.strip()

        # Iterate through rows in the main DataFrame
        for index, row in df.iterrows():
            object_id = row[identifier_col]
            reqif_text = row['ReqIF.Text']
            oem_status = row.get('Status OEM zu Lieferant R', None)
            category = row.get(category_col, None)
            
            if pd.isna(oem_status):
                oem_status = "Empty"
            else:
                oem_status = str(oem_status).rstrip(',')

            # Skip rows with missing 'Object ID'
            if pd.isna(object_id):
                continue

            # Skip if status is 'verworfen'
            if oem_status == 'verworfen':
                continue

            # Check if the 'Object ID' exists in the compare file
            if object_id in compare_dict:
                compare_text = compare_dict[object_id]

                # Convert to string and strip whitespace
                reqif_text_str = str(reqif_text) if not pd.isna(reqif_text) else ""
                compare_text_str = str(compare_text) if not pd.isna(compare_text) else ""
                reqif_text_str = reqif_text_str.strip()
                compare_text_str = compare_text_str.strip()

                # Skip only if both texts are empty
                if not reqif_text_str and not compare_text_str:
                    continue

                # Remove embedded object references before normalization
                reqif_text_str = remove_embedded_objects(reqif_text_str)
                compare_text_str = remove_embedded_objects(compare_text_str)

                # Normalize special symbols in both texts
                reqif_text_str = HelperFunctions.normalize_symbols(reqif_text_str)
                compare_text_str = HelperFunctions.normalize_symbols(compare_text_str)

                # Clean OLE Object artifacts before strict normalization
                cleaned_reqif_text = HelperFunctions.clean_ole_object_text(reqif_text_str)
                cleaned_compare_text = HelperFunctions.clean_ole_object_text(compare_text_str)

                # Normalize both texts using the same function as Check Nr. 6
                normalized_reqif_text = HelperFunctions.normalize_text(cleaned_reqif_text)
                normalized_compare_text = HelperFunctions.normalize_text(cleaned_compare_text)

                if normalized_reqif_text != normalized_compare_text:
                    category_str = 'Empty' if pd.isna(category) or str(category).strip() == '' else str(category).rstrip(',')
                    findings.append({
                        'Row': index + 2,  # Adjust for Excel row numbering
                        'Check Number': 'Nr.10',
                        'Object ID': str(object_id),
                        'Attribute': 'ReqIF.Text, Object Text',
                        'Issue': (
                            f"'ReqIF.Text' differs from 'Object Text' between files, may be the translation is needed (FOR INTERNAL USE ONLY!)."
                        ),
                        'Value': (
                            f"Object ID: {object_id}\n"
                            f"Typ: {category_str}\n"
                            f"\n"
                            f"---------------\n"
                            f"       Customer File Name: {os.path.basename(file_path)}\n"
                            f"       Customer File Object Text: {reqif_text_str}\n"
                            f"---------------\n"
                            f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                            f"       Bosch File Object Text: {compare_text_str}\n"
                            f"---------------\n"
                            f"       Status OEM zu Lieferant R: {oem_status}"
                        )
                    })

        logger.info(f"[CHECK NR.10 END] Found {len(findings)} findings.")
        return findings

    # Check Nr.11
    @staticmethod
    def check_rb_update_for_changed_requirements(df, compare_df, file_path, compare_file_path):
        """
        Check Nr.11: Detects RB updates when key attributes differ between customer and Bosch files.

        Compares, per Object ID:
        - 'ReqIF.Text' (Customer) vs 'Object Text' (Bosch)
        - 'English_Translation' (Customer) vs 'Object Text English' (Bosch)
        - 'Typ' (Customer) vs 'Typ' (Bosch)

        If any of these attributes differ for a given Object ID, a finding is created.
        These findings are later used to generate a TSV file listing affected Object IDs
        with a column 'RB_Update_detected' set to 'Yes'.

        Hinweis: Beim Vergleich des Objekttexts werden Leerzeichen, Semikolons,
        einfache Anführungszeichen und doppelte Anführungszeichen ignoriert
        (über HelperFunctions.normalize_text).
        """
        findings = []
        logger.info(f"[CHECK NR.11 START] RB update detection (ReqIF.Text, English_Translation, Typ) | File: {file_path}")

        # This check is defined for Object ID based comparison (LAH vs DOORS export)
        # Always require 'Object ID' in both files; other attributes are checked flexibly.
        required_customer_cols = ['Object ID']
        required_bosch_cols = ['Object ID']

        missing_customer = [c for c in required_customer_cols if c not in df.columns]
        missing_bosch = [c for c in required_bosch_cols if c not in compare_df.columns]

        check_name = __class__.check_rb_update_for_changed_requirements.__name__
        if missing_customer:
            logger.warning(
                f"Missing required columns in the customer DataFrame: {missing_customer}, "
                f"in File: {file_path}.\nSkipping check: {check_name}"
            )
            return findings

        if missing_bosch:
            logger.warning(
                f"Missing required columns in the Bosch file: {missing_bosch}, "
                f"in File: {compare_file_path}.\nSkipping check: {check_name}"
            )
            return findings

        # Determine which attributes are available for flexible comparison
        reqif_enabled = 'ReqIF.Text' in df.columns and 'Object Text' in compare_df.columns
        # Compare Object Text English (Bosch) with English_Translation (Customer)
        eng_enabled = 'English_Translation' in df.columns and 'Object Text English' in compare_df.columns

        # Typ can be provided as 'Typ' or 'Type' on the customer side; Bosch side must have 'Typ'
        customer_has_typ = 'Typ' in df.columns
        customer_has_type = 'Type' in df.columns
        bosch_has_typ = 'Typ' in compare_df.columns
        typ_enabled = bosch_has_typ and (customer_has_typ or customer_has_type)

        if not (reqif_enabled or eng_enabled or typ_enabled):
            logger.warning(
                f"No comparable attributes (ReqIF.Text/Object Text, Object Text English, Typ/Type) "
                f"found for Check Nr.11 in files: {file_path} and {compare_file_path}. Skipping check."
            )
            return findings

        # Build quick lookup for Bosch rows by Object ID
        bosch_rows_by_id = {}
        for _, ref_row in compare_df.iterrows():
            ref_object_id = ref_row.get('Object ID', None)
            if pd.isna(ref_object_id) or str(ref_object_id).strip() == "":
                continue
            bosch_rows_by_id.setdefault(str(ref_object_id), []).append(ref_row)

        seen_object_ids = set()

        for index, row in df.iterrows():
            object_id = row.get('Object ID', None)
            if pd.isna(object_id) or str(object_id).strip() == "":
                continue

            object_id_str = str(object_id)

            if object_id_str not in bosch_rows_by_id:
                continue

            # Read customer attributes only if enabled / available
            customer_reqif = row.get('ReqIF.Text', None) if reqif_enabled else None
            # For English, use 'English_Translation' on customer side
            customer_eng = row.get('English_Translation', None) if eng_enabled else None

            # Determine customer "Typ" normalization, with fallback to 'Type' mapping
            customer_typ_norm = ""
            if typ_enabled:
                raw_typ = None
                if customer_has_typ:
                    raw_typ = row.get('Typ', None)
                    customer_typ_norm = "" if pd.isna(raw_typ) else str(raw_typ).rstrip(',').strip()
                elif customer_has_type:
                    raw_typ = row.get('Type', None)
                    # Map Type values to Typ semantics
                    type_str = "" if pd.isna(raw_typ) else str(raw_typ).rstrip(',').strip()
                    type_mapping = {
                        'Folder': 'Überschrift',
                        'Information': 'Information',
                        'Requirement': 'Anforderung',
                    }
                    customer_typ_norm = type_mapping.get(type_str, type_str)

            # Flags for differences
            reqif_diff = False
            eng_diff = False
            typ_diff = False

            # Compare against each Bosch row with same Object ID; one match is enough
            for ref_row in bosch_rows_by_id[object_id_str]:
                bosch_text = ref_row.get('Object Text', None) if reqif_enabled else None
                # For English, use 'Object Text English' on Bosch side
                bosch_eng = ref_row.get('Object Text English', None) if eng_enabled else None
                bosch_typ = ref_row.get('Typ', None) if typ_enabled else None

                # --- ReqIF.Text vs Object Text ---
                if reqif_enabled:
                    customer_reqif_str = "" if pd.isna(customer_reqif) else str(customer_reqif).strip()
                    bosch_text_str = "" if pd.isna(bosch_text) else str(bosch_text).strip()

                    # Normalize special symbols, then clean and normalize for comparison
                    customer_reqif_str = HelperFunctions.normalize_symbols(customer_reqif_str)
                    bosch_text_str = HelperFunctions.normalize_symbols(bosch_text_str)
                    cleaned_reqif = HelperFunctions.clean_ole_object_text(customer_reqif_str)
                    cleaned_bosch_text = HelperFunctions.clean_ole_object_text(bosch_text_str)
                    norm_reqif = HelperFunctions.normalize_text(cleaned_reqif).replace('-', '').lower()
                    norm_bosch_text = HelperFunctions.normalize_text(cleaned_bosch_text).replace('-', '').lower()
                    if norm_reqif != norm_bosch_text:
                        reqif_diff = True

                # --- Object Text English ---
                if eng_enabled:
                    customer_eng_str = "" if pd.isna(customer_eng) else str(customer_eng).strip()
                    bosch_eng_str = "" if pd.isna(bosch_eng) else str(bosch_eng).strip()

                    customer_eng_str = HelperFunctions.normalize_symbols(customer_eng_str)
                    bosch_eng_str = HelperFunctions.normalize_symbols(bosch_eng_str)
                    cleaned_eng_customer = HelperFunctions.clean_ole_object_text(customer_eng_str)
                    cleaned_eng_bosch = HelperFunctions.clean_ole_object_text(bosch_eng_str)
                    norm_eng_customer = HelperFunctions.normalize_text(cleaned_eng_customer).replace('-', '').lower()
                    norm_eng_bosch = HelperFunctions.normalize_text(cleaned_eng_bosch).replace('-', '').lower()
                    if norm_eng_customer != norm_eng_bosch:
                        eng_diff = True

                # --- Typ ---
                if typ_enabled:
                    bosch_typ_norm = "" if pd.isna(bosch_typ) else str(bosch_typ).rstrip(',').strip()
                    if customer_typ_norm != bosch_typ_norm:
                        typ_diff = True

                if reqif_diff or eng_diff or typ_diff:
                    break  # One differing Bosch row is enough

            if not (reqif_diff or eng_diff or typ_diff):
                continue

            # Avoid duplicate findings per Object ID
            if object_id_str in seen_object_ids:
                continue
            seen_object_ids.add(object_id_str)

            changed_attrs = []
            if reqif_diff:
                changed_attrs.append("ReqIF.Text/Object Text")
            if eng_diff:
                changed_attrs.append("Object Text English")
            if typ_diff:
                changed_attrs.append("Typ")

            changed_attrs_str = ", ".join(changed_attrs)

            findings.append({
                'Row': index + 2,  # Excel-style row number
                'Check Number': 'Nr.11',
                'Object ID': object_id_str,
                'Attribute': changed_attrs_str,
                'Issue': (
                    "For the same Object ID, at least one of the following attributes differs "
                    "between the Customer file and the Bosch file: Original text (ReqIF.Text vs Object Text), "
                    "English text (English_Translation vs Object Text English), or Typ."
                ),
                'Value': (
                    f"Object ID: {object_id_str}\n"
                    f"\n"
                    f"---------------\n"
                    f"       Customer File Name: {os.path.basename(file_path)}\n"
                    f"       Customer ReqIF.Text: {customer_reqif if reqif_enabled and not pd.isna(customer_reqif) else 'Empty'}\n"
                    f"       Customer Object Text English: {customer_eng if eng_enabled and not pd.isna(customer_eng) else 'Empty'}\n"
                    f"       Customer Typ: {customer_typ_norm or 'Empty'}\n"
                    f"---------------\n"
                    f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                    f"       Bosch Object Text: {bosch_text_str if reqif_enabled and 'bosch_text_str' in locals() and bosch_text_str else 'Empty'}\n"
                    f"       Bosch Object Text English: {bosch_eng_str if eng_enabled and 'bosch_eng_str' in locals() and bosch_eng_str else 'Empty'}\n"
                    f"       Bosch Typ: {bosch_typ_norm if typ_enabled else 'Empty'}\n"
                    f"---------------\n"
                    f"       RB_Update_detected: Yes"
                )
            })

        logger.info(f"[CHECK NR.11 END] Found {len(findings)} findings.")
        return findings

    # Check Nr.12
    @staticmethod
    def check_missing_object_ids_from_bosch(df, compare_df, file_path, compare_file_path):
        """
        Check Nr.12: Detects Object IDs present in the Bosch file (for the matching module)
        that are missing from the customer file. Purpose: prevent accidental deletion of
        Object IDs in customer files.

        - The customer file's module name is extracted from its filename
          (pattern: <ModuleName>_<8hex>_local_conversion.xlsx).
        - The Bosch file's 'Modulename' column is searched for matching rows using
          fuzzy matching (dots, spaces, underscores treated as equivalent; prefix match
          or LAH-ID-only fallback).
        - For each Object ID present in the matched Bosch rows but absent in the
          customer file, a finding is generated.
        """
        findings = []
        logger.info(f"[CHECK NR.12 START] Missing Object ID detection | File: {file_path}")

        # --- Validate required columns ---
        if 'Object ID' not in df.columns:
            logger.warning(f"[CHECK NR.12] 'Object ID' column not found in customer file: {file_path}.")
            findings.append({
                'Row': 'N/A',
                'Check Number': 'Nr.12',
                'Object ID': 'N/A',
                'Attribute': 'Object ID',
                'Issue': "'Object ID' column is missing entirely from the customer file.",
                'Value': (
                    f"Customer File Name: {os.path.basename(file_path)}\n"
                    f"\n"
                    f"       The 'Object ID' column could not be found in the customer file.\n"
                    f"       All Object IDs from the corresponding Bosch module are therefore unverifiable.\n"
                    f"\n"
                    f"       Action Required:\n"
                    f"       Please discuss with the customer why the 'Object ID' column has been\n"
                    f"       removed from the file and request written clarification. Ensure the\n"
                    f"       file is re-exported correctly before proceeding with further checks."
                )
            })
            return findings
        if 'Object ID' not in compare_df.columns:
            logger.warning(f"[CHECK NR.12] 'Object ID' column not found in Bosch file: {compare_file_path}. Skipping.")
            return findings
        if 'Modulename' not in compare_df.columns:
            logger.warning(f"[CHECK NR.12] 'Modulename' column not found in Bosch file: {compare_file_path}. Skipping.")
            return findings

        # --- Extract module name from customer filename ---
        filename = os.path.basename(file_path)
        _filename_re = re.compile(r'^(?P<base>.+?)_[0-9a-fA-F]{8}_local_conversion\.xlsx$', re.IGNORECASE)
        m = _filename_re.match(filename)
        if not m:
            logger.warning(f"[CHECK NR.12] Filename does not match expected pattern: {filename}. Skipping.")
            return findings
        source_module = m.group('base')
        logger.debug(f"[CHECK NR.12] Extracted module name from filename: {source_module}")

        # --- Fuzzy matching helpers (same logic as find_moduleName.py) ---
        def _norm(s: str) -> str:
            s = s.strip()
            s = re.sub(r'[ _.]', '.', s)
            s = re.sub(r'\.{2,}', '.', s)
            return s.lower()

        def _extract_key(modulename: str) -> str:
            """Take last path segment and strip leading AS_NNN_ prefix."""
            segment = str(modulename).strip().split('/')[-1]
            segment = re.sub(r'^[A-Z]+_\d+_', '', segment)
            return segment.strip()

        src_norm = _norm(source_module)

        # ID-only fallback: just the LAH code (e.g. "LAH.000.900.CM"), stops before first "_"
        _lah_id_re = re.compile(r'^(LAH[A-Za-z0-9.]+)', re.IGNORECASE)
        id_m = _lah_id_re.match(source_module)
        lah_id_norm = (_norm(id_m.group(1)) + '.') if id_m else None

        def _matches_module(modulename) -> bool:
            if pd.isna(modulename):
                return False
            key_norm = _norm(_extract_key(str(modulename)))
            if key_norm.startswith(src_norm):
                return True
            if lah_id_norm and key_norm.startswith(lah_id_norm):
                return True
            return False

        # --- Filter Bosch rows for this module ---
        bosch_module_df = compare_df[compare_df['Modulename'].apply(_matches_module)]

        if bosch_module_df.empty:
            logger.warning(f"[CHECK NR.12] No matching module found in Bosch file for: {source_module}. Skipping.")
            return findings

        logger.debug(f"[CHECK NR.12] {len(bosch_module_df)} Bosch rows matched for module: {source_module}")

        # --- Collect Object IDs from both sides ---
        bosch_object_ids = {
            str(oid).strip()
            for oid in bosch_module_df['Object ID']
            if not pd.isna(oid) and str(oid).strip() != ''
        }
        customer_object_ids = {
            str(oid).strip()
            for oid in df['Object ID']
            if not pd.isna(oid) and str(oid).strip() != ''
        }

        missing_ids = bosch_object_ids - customer_object_ids

        if not missing_ids:
            logger.info(f"[CHECK NR.12 END] No missing Object IDs found.")
            return findings

        # --- Build a lookup for Bosch Object Text (for context in findings) ---
        bosch_text_lookup = {}
        if 'Object Text' in bosch_module_df.columns:
            for _, row in bosch_module_df.iterrows():
                oid = str(row.get('Object ID', '')).strip()
                text = row.get('Object Text', '')
                if oid and oid not in bosch_text_lookup:
                    bosch_text_lookup[oid] = '' if pd.isna(text) else str(text).strip()

        # --- Generate findings ---
        for missing_id in sorted(missing_ids):
            object_text = bosch_text_lookup.get(missing_id, '')
            findings.append({
                'Row': 'N/A',
                'Check Number': 'Nr.12',
                'Object ID': missing_id,
                'Attribute': 'Object ID',
                'Issue': "Object ID exists in Bosch file but is missing in customer file (possible deletion).",
                'Value': (
                    f"Object ID: {missing_id}\n"
                    f"\n"
                    f"---------------\n"
                    f"       Customer File Name: {os.path.basename(file_path)}\n"
                    f"       Status: Object ID NOT FOUND in customer file\n"
                    f"---------------\n"
                    f"       Bosch File Name: {os.path.basename(compare_file_path)}\n"
                    f"       Bosch Module: {source_module}\n"
                    f"       Bosch Object Text: {object_text if object_text else 'N/A'}\n"
                    f"---------------\n"
                    f"       Action Required: Verify if this Object ID was intentionally deleted."
                )
            })

        logger.info(f"[CHECK NR.12 END] Found {len(findings)} missing Object IDs.")
        return findings