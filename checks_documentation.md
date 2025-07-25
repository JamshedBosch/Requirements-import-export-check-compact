# Requirements Import/Export Checks Documentation

## Overview
This documentation explains the validation checks implemented in `ChecksPPE.py` and `ChecksSSP.py`. These checks ensure data integrity and consistency in requirement files during import and export operations.

## ChecksPPE.py
The `ProjectCheckerPPE` class implements various checks for PPE (Product Performance Engineering) requirements.

### Import Checks

#### 1. Empty Object ID with Forbidden CR Status
**Method**: `check_empty_object_id_with_forbidden_cr_status`
- **Purpose**: Validates that rows with empty Object IDs don't have forbidden CR status values
- **Conditions**:
  - Checks if 'Object ID' is empty
  - Checks if 'CR-Status_Bosch_PPx' is in forbidden values: ['014,', '013,', '100,']
- **Finding Trigger**: Empty Object ID combined with a forbidden status

#### 2. CR Status Bosch PPx Conditions
**Method**: `check_cr_status_bosch_ppx_conditions`
- **Purpose**: Validates consistency between CR status, CR ID, and BRS-1Box status
- **Conditions**:
  - 'CR-Status_Bosch_PPx' is '---'
  - 'CR-ID_Bosch_PPx' is not empty
  - 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'verworfen'
- **Finding Trigger**: All conditions are true simultaneously

#### 4. Anlaufkonfiguration Empty Check
**Method**: `check_anlaufkonfiguration_empty`
- **Purpose**: Ensures Anlaufkonfiguration fields are not empty under specific conditions
- **Checks**:
  - Anlaufkonfiguration_01, _02, _03 emptiness
- **Conditions**:
  - 'Object ID' is not empty
  - 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'verworfen'
- **Finding Trigger**: Empty Anlaufkonfiguration fields when conditions are met

#### 5. CR ID Empty for BRS Hersteller Status
**Method**: `check_cr_id_empty_for_brs_hersteller_status`
- **Purpose**: Validates CR ID presence for BRS Hersteller status
- **Condition**: 'CR-ID_Bosch_PPx' is empty
- **Finding Trigger**: Empty CR ID with any BRS Hersteller status

#### 6. Object Text with Status Hersteller Bosch PPx
**Method**: `check_object_text_with_status_hersteller_bosch_ppx`
- **Purpose**: Compares Object Text between files and validates status
- **Conditions**:
  - Object Text differs between files
  - 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'neu/geändert'
- **Finding Trigger**: Different texts without appropriate status

#### 7. Object Text with RB AS Status
**Method**: `check_object_text_with_rb_as_status`
- **Purpose**: Validates Object Text changes against RB AS Status
- **Conditions**:
  - Object Text differs between files
  - 'RB_AS_Status' is in ['accepted', 'no_req', 'canceled_closed']
- **Finding Trigger**: Text differences with prohibited status values

#### 8. Required Attributes Not Empty
**Method**: `check_required_attributes_not_empty`
- **Purpose**: Ensures critical attributes are not empty when requirement is active
- **Required Attributes**:
  - Object ID
  - Object Text
  - Technikvariante
  - Typ
- **Conditions**:
  - 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'verworfen'
  - At least one of the required attributes must be present in the file
- **Flexible Execution**:
  - Check runs if any of the required attributes exists
  - Only validates attributes that are present in the file
  - Skips check if BRS status column is missing
- **Finding Trigger**: Any available required attribute is empty when BRS status is not 'verworfen'
- **Report Format**:
  ```
  Row: [row_number]

  Attribute: [empty_attribute_name]

  Issue: [attribute_name] is empty while BRS-1Box_Status_Hersteller_Bosch_PPx is not 'verworfen'.

  Details:
  Object ID: [id_value] (if available)
  Empty Columns: [list_of_empty_columns]
  BRS-1Box_Status_Hersteller_Bosch_PPx: [status_value]
  ```
  - Object ID is included in details when available for easy requirement tracing
  - Multiple empty attributes are listed under Empty Columns
  - Grammar adapts to single/multiple empty attributes ("is"/"are")

### Export Checks

#### 1. CR ID with Typ and BRS 1Box Status
**Method**: `check_cr_id_with_typ_and_brs_1box_status_zulieferer_bosch_ppx`
- **Purpose**: Validates supplier status for requirements
- **Conditions**:
  - 'CR-ID_Bosch_PPx' is not empty
  - 'Typ' is 'Anforderung'
  - 'BRS-1Box_Status_Zulieferer_Bosch_PPx' must be 'akzeptiert' or 'abgelehnt'
- **Finding Trigger**: Invalid supplier status for requirements

#### 2. Typ with BRS 1Box Status
**Method**: `check_typ_with_brs_1box_status_zulieferer_bosch_ppx`
- **Purpose**: Validates status for specific requirement types
- **Conditions**:
  - 'Typ' is 'Überschrift' or 'Information'
  - 'BRS-1Box_Status_Zulieferer_Bosch_PPx' must be 'n/a'
- **Finding Trigger**: Invalid status for headers or information

## ChecksSSP.py
The `ProjectCheckerSSP` class implements checks for SSP (Scalable System Platform) requirements.

### Import Checks

#### 6. Object Text with Status OEM zu Lieferant R
**Method**: `check_object_text_with_status_oem_zu_lieferant_r`
- **Purpose**: Compares requirement texts and validates OEM status
- **Features**:
  - Supports both 'ReqIF.ForeignID' and 'Object ID' as identifiers
  - Compares 'ReqIF.Text' with 'Object Text'
  - Uses text normalization for consistent comparison
- **Status Handling**:
  - No findings generated if Status OEM zu Lieferant R is:
    * 'zu bewerten' OR
    * 'verworfen'
  - Status comparison is comma-insensitive (handles both with and without trailing comma)
  - Findings generated for all other status values when texts differ
- **Text Comparison**:
  - Normalizes text by removing extra spaces and standardizing formatting
  - Skips comparison if both texts are empty
  - Handles NULL/empty values gracefully
- **Finding Trigger**: Text differences with status not being 'zu bewerten' or 'verworfen'
- **Report Format**:
  ```
  Row: [row_number]
  Attribute: ReqIF.Text, Status OEM zu Lieferant R
  Issue: 'ReqIF.Text' differs from 'Object Text' but 'Status OEM zu Lieferant R' is not 'zu bewerten'.
  Value:
  [identifier]: [value]
  ---------------
  Customer File Name: [filename]
  Customer File Object Text: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch File Object Text: [value]
  ---------------
  Status OEM zu Lieferant R: [status]
  Expected Status: zu bewerten
  ```
  - Includes file names for both customer and Bosch files
  - Shows text values from both files for comparison
  - Displays current and expected status values
  - Maintains consistent formatting with other checks

#### 8. Multiple Attributes with Status OEM zu Lieferant R
**Method**: `check_multiple_attributes_with_status_oem_zu_lieferant_r`
- **Purpose**: Compares multiple attributes between customer and Bosch files
- **Attributes Checked**:
  - 'ReqIF.Category' vs 'Category'
  - 'ASIL' vs 'ASIL'
  - 'Reifegrad' vs 'Reifegrad'
  - 'Feature' vs 'Feature'
  - 'Sonstige-Varianten' vs 'Sonstige-Varianten'
- **ASIL Special Cases**:
  - Customer special values: ['n/a', 'qm', 'nein', 'tbd', ''] (empty)
  - Bosch allowed values: ['tbd', 'n/a', 'qm', ''] (empty)
  - No findings generated when customer has special value and Bosch has allowed value
- **File Type Handling**:
  - For ReqIF.Category files: All attributes are checked
  - For Typ files: Only Typ and ASIL (if present) are checked
- **Status Handling**:
  - No findings generated if Status OEM zu Lieferant R is:
    * 'zu bewerten' OR
    * 'verworfen'
  - Findings generated for all other status values when attributes differ
- **Finding Trigger**: Attribute differences with status not being 'zu bewerten' or 'verworfen'

#### 9. Quelle with Status OEM zu Lieferant R
**Method**: `check_quelle_with_status_oem_zu_lieferant_r`
- **Purpose**: Compares 'Quelle' attribute between customer and Bosch files
- **Features**:
  - Supports both 'ReqIF.ForeignID' and 'Object ID' as identifiers
  - Compares 'Quelle' values between files
- **Status Handling**:
  - No findings generated if Status OEM zu Lieferant R is:
    * 'zu bewerten' OR
    * 'verworfen'
  - Findings generated for all other status values when Quelle differs
- **Finding Trigger**: Quelle differences with status not being 'zu bewerten' or 'verworfen'
- **Report Format**:
  ```
  Row: [row_number]
  Attribute: Quelle, Status OEM zu Lieferant R
  Issue: 'Quelle' differs between files but 'Status OEM zu Lieferant R' is not 'zu bewerten'.
  Value:
  [identifier]: [value]
  ---------------
  Customer File Name: [filename]
  Customer File Quelle: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch File Quelle: [value]
  ---------------
  Status OEM zu Lieferant R: [status]
  Expected Status: zu bewerten
  ```
  - Includes file names for both customer and Bosch files
  - Shows Quelle values from both files for comparison
  - Displays current and expected status values

#### 10. Text Differences Without Status Validation
**Method**: `check_text_differences_without_status_validation`
- **Purpose**: Compares requirement texts between customer and Bosch files without status validation
- **Features**:
  - Supports both 'ReqIF.ForeignID' and 'Object ID' as identifiers
  - Compares 'ReqIF.Text' with 'Object Text'
  - Reports all differences regardless of status
  - Uses the same text normalization as Check Nr. 6
- **Key Differences from Check Nr.6**:
  - No status validation (reports differences for all status values)
  - Focuses purely on text comparison
  - Includes current status in findings for information
- **Finding Trigger**: Any difference between ReqIF.Text and Object Text
- **Report Format**:
  ```
  Row: [row_number]
  Attribute: ReqIF.Text, Object Text
  Issue: 'ReqIF.Text' differs from 'Object Text' between files, may be the translation is needed (FOR INTERNAL USE ONLY!).
  Value:
  [identifier]: [value]
  ---------------
  Customer File Name: [filename]
  Customer File Object Text: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch File Object Text: [value]
  ---------------
  Status OEM zu Lieferant R: [status]
  ```
  - Shows text values from both files for comparison
  - Includes current status for reference
  - Maintains consistent formatting with other checks
  - Indicates potential translation needs in the issue description

## Common Features

### Error Handling
- All checks include column presence validation
- Empty/NULL value handling
- Logging of missing columns and skipped checks

### Data Normalization
- Text normalization using `HelperFunctions.normalize_text`
- Consistent handling of trailing commas
- Empty value standardization

### Reporting
- Detailed findings with row numbers
- Clear issue descriptions
- Value comparisons where relevant
- File path information in reports

## Best Practices
1. Always check for required columns before processing
2. Handle empty/NULL values explicitly
3. Normalize text for consistent comparison
4. Provide detailed context in findings
5. Use appropriate status values for different requirement types 