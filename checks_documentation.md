# Requirements Import/Export Checks Documentation

## Overview
This documentation explains the validation checks implemented in `ChecksPPE.py`, `ChecksSSP.py`, and `ChecksSDV01.py`. These checks ensure data integrity and consistency in requirement files during import and export operations.

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

#### 10. Status Bosch PPx 015 with BRS Status Not Abgestimmt
**Method**: `check_status_bosch_ppx_015_and_brs_status_not_abgestimmt`
- **Purpose**: Ensures that when 'Status_Bosch_PPx' is '015', the 'BRS-1Box_Status_Hersteller_Bosch_PPx' is set to 'abgestimmt'.
- **Conditions**:
  - 'Status_Bosch_PPx' is '015' (trailing commas and whitespace are ignored)
  - 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'abgestimmt' (trailing commas and whitespace are ignored)
- **Finding Trigger**: Any row where 'Status_Bosch_PPx' is '015' and 'BRS-1Box_Status_Hersteller_Bosch_PPx' is not 'abgestimmt'.
- **Report Format**:
  ```
  Object ID: [object_id]
  Typ: [typ]
  ---------------
         File Name: [filename]
         Status_Bosch_PPx: [normalized_status_bosch_ppx]
         BRS-1Box_Status_Hersteller_Bosch_PPx: [normalized_brs_status]
  ```
  - Object ID and Typ are included for traceability
  - All values are normalized (trailing commas/whitespace removed)
  - Clearly sections the information for easy review

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

#### 11. RB Update Detection for Changed Requirements
**Method**: `check_rb_update_for_changed_requirements`
- **Purpose**: Detects whether a Bosch update (RB update) is required based on differences in key attributes between the customer file and the Bosch reference file. The findings are used to generate a separate TSV file listing affected Object IDs with an `RB_Update_detected = Yes` flag.
- **Attributes Compared** (all comparisons are by `Object ID`):
  | Customer Attribute | Bosch Attribute |
  |---|---|
  | `ReqIF.Text` | `Object Text` |
  | `English_Translation` | `Object Text English` |
  | `Typ` / `Type` | `Typ` |
- **Flexible Execution**:
  - Only attributes present in both files are compared; missing attributes are silently skipped
  - `Type` (customer) is mapped to `Typ` semantics: `Folder → Überschrift`, `Requirement → Anforderung`, `Information → Information`
  - Skips the check entirely if none of the three attribute pairs are available
- **Text Normalization**:
  - Applies `HelperFunctions.normalize_symbols`, `clean_ole_object_text`, and `normalize_text`
  - Hyphens are removed and text is lowercased before comparison
- **Finding Trigger**: At least one of the three attribute pairs differs for a given `Object ID`
- **Deduplication**: Only one finding per `Object ID` is generated even if the same ID appears in multiple rows
- **Report Format**:
  ```
  Object ID: [object_id]
  ---------------
         Customer File Name: [filename]
         Customer ReqIF.Text: [value]
         Customer Object Text English: [value]
         Customer Typ: [value]
  ---------------
         Bosch File Name: [filename]
         Bosch Object Text: [value]
         Bosch Object Text English: [value]
         Bosch Typ: [value]
  ---------------
         RB_Update_detected: Yes
  ```
- **Additional Output**: A `_rb_update.tsv` file is generated alongside the HTML report, containing one row per affected `Object ID` with column `RB_Update_detected = Yes`.

---

#### 12. Missing Object IDs from Bosch File
**Method**: `check_missing_object_ids_from_bosch`
- **Purpose**: Detects `Object ID`s that are present in the Bosch reference file (for the matching module) but are absent from the customer file. This check prevents the accidental deletion of requirements in customer files.
- **Background**: When a customer file is exported and re-imported, requirements can be inadvertently deleted. This check acts as a safety net by cross-referencing every Bosch `Object ID` — scoped to the relevant module — against the customer file.

##### Module Identification
The customer file's module is identified by parsing its filename using the pattern:
```
<ModuleName>_<8-hex-chars>_local_conversion.xlsx
```
The extracted `<ModuleName>` is then matched against the `Modulename` column in the Bosch file using **two-tier fuzzy matching**:

| Tier | Strategy | Example match |
|---|---|---|
| 1 — Full prefix | Normalized source name is a prefix of normalized target key | `LAH.5G0.042.F_DynamometerOperationMode` → `AS_064_LAH.5G0.042.F_DynamometerOperationMode` |
| 2 — LAH ID only | Only the LAH code (e.g. `LAH.000.900.CM`) is matched | `LAH.000.900.CM_ECU Standard...` → `AS_122_LAH.000.900.CM Standard Eigendiagnose...` |

**Normalization rules** (applied to both sides before comparison):
- Spaces, underscores (`_`), and dots (`.`) are treated as equivalent
- Multiple consecutive separators are collapsed into one
- Comparison is case-insensitive
- The leading `AS_<NNN>_` prefix is stripped from the target's last path segment

##### Logic
1. Extract module name from the customer filename
2. Filter all Bosch rows whose `Modulename` matches the extracted module (fuzzy)
3. Collect all non-empty `Object ID` values from the filtered Bosch rows
4. Collect all non-empty `Object ID` values from the customer file
5. Compute: `missing = bosch_ids − customer_ids`
6. Generate one finding per missing `Object ID`

##### Required Columns
| File | Required Columns |
|---|---|
| Customer file | `Object ID` |
| Bosch file | `Object ID`, `Modulename` |

##### Special Cases
- **`Object ID` column entirely missing from customer file**: A finding is generated indicating that the column itself is absent. The action text requests written clarification from the customer as to why the column was removed.
- **No matching module found in Bosch file**: The check is silently skipped with a warning log entry.
- **Filename does not match expected pattern**: The check is silently skipped with a warning log entry.

##### Finding Trigger
Any `Object ID` present in the Bosch file (for the matched module) that cannot be found in the customer file.

##### Report Format
```
Object ID: [missing_object_id]

---------------
       Customer File Name: [filename]
       Status: Object ID NOT FOUND in customer file   ← highlighted in yellow
---------------
       Bosch File Name: [filename]
       Bosch Module: [extracted_module_name]
       Bosch Object Text: [object_text_from_bosch | N/A]
---------------
       Action Required: Verify if this Object ID was intentionally deleted.
```

- The **`Status`** line is rendered with a **yellow highlight** in the HTML report for immediate visual attention
- `Bosch Object Text` provides context about the deleted requirement (shown as `N/A` if the Bosch file has no `Object Text` column)
- `Row` is reported as `N/A` since the Object ID is absent from the customer file and has no corresponding row

---

## ChecksSDV01.py
The `ProjectCheckerSDV01` class implements checks for SDV01 requirements.

### Import Checks

#### 1. Empty Object ID with Forbidden CR Status
**Method**: `check_empty_object_id_with_forbidden_cr_status`
- **Purpose**: Validates that rows with empty Object IDs don't have forbidden CR status values
- **Conditions**:
  - Checks if 'Object ID' is empty
  - Checks if 'CR-Status_Bosch_SDV0.1' is in forbidden values: ['014,', '031,', '100,']
- **Finding Trigger**: Empty Object ID combined with a forbidden status

#### 2. CR Status Bosch SDV0.1 Conditions
**Method**: `check_cr_status_bosch_sdv01_conditions`
- **Purpose**: Validates consistency between CR status, CR ID, and BRS status
- **Conditions**:
  - 'CR-Status_Bosch_SDV0.1' is empty or '---'
  - 'CR-ID_Bosch_SDV0.1' is not empty
  - 'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'verworfen'
- **Finding Trigger**: All conditions are true simultaneously

#### 3. Missing Release for Verworfen Status
**Method**: `check_missing_release_for_verworfen_status`
- **Purpose**: Ensures release fields are filled for requirements that are not rejected
- **Checks**:
  - EntfallRelease and ErsteinsatzRelease emptiness
- **Conditions**:
  - 'BRS_Status_Hersteller_Bosch_SDV0.1' != 'verworfen'
  - At least one of 'EntfallRelease' or 'ErsteinsatzRelease' is empty
- **Finding Trigger**: `EntfallRelease` OR `ErsteinsatzRelease` is empty while BRS status is not 'verworfen'

#### 4. CR ID and BRS Status Comparison
**Method**: `compare_cr_id_and_brs_status_by_object_id`
- **Purpose**: Compares CR-ID and BRS Status between customer and Bosch files
- **Conditions**:
  - Matches rows by 'Object ID'
  - Only checks rows where 'Typ' is 'Anforderung' (with or without trailing comma)
  - Compares 'CR-ID_Bosch_SDV0.1' and 'BRS_Status_Hersteller_Bosch_SDV0.1' between files
- **Finding Trigger**: Any difference found in either CR-ID or BRS Status
- **Report Format**:
  ```
  Object ID: [object_id]
  ---------------
  Customer File Name: [filename]
  Customer CR-ID_Bosch_SDV0.1: [value]
  Customer BRS_Status_Hersteller_Bosch_SDV0.1: [value]
  Customer CR-Status_Bosch_SDV0.1: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch CR-ID_Bosch_SDV0.1: [value]
  Bosch BRS_Status_Hersteller_Bosch_SDV0.1: [value]
  Bosch CR-Status_Bosch_SDV0.1: [value]
  ```
  - Shows both customer and Bosch values for comparison
  - CR-Status is shown for context but not compared

#### 5. ReqIF.Text with Status Hersteller Bosch SDV0.1
**Method**: `check_reqif_text_with_status_hersteller_bosch_sdv01`
- **Purpose**: Compares ReqIF.Text with Object Text and validates status
- **Conditions**:
  - Compares 'ReqIF.Text' (customer) with 'Object Text' (Bosch reference) by 'Object ID'
  - Text differs between files
  - 'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'neu/geändert' (with or without trailing comma)
- **Text Comparison**:
  - Uses text normalization for consistent comparison
  - Skips comparison if Object ID not found in reference file
- **Finding Trigger**: Text differences without appropriate status
- **Report Format**:
  ```
  Object ID: [object_id]
  ---------------
  Customer File Name: [filename]
  Customer File ReqIF.Text: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch File Object Text: [value]
  ---------------
  BRS_Status_Hersteller_Bosch_SDV0.1: [status]
  Expected Status: neu/geändert
  ```

#### 6. Object Text with RB AS Status
**Method**: `check_object_text_with_rb_as_status`
- **Purpose**: Validates Object Text changes against RB AS Status
- **Conditions**:
  - Compares 'Object Text' between customer (Audi ReqIF) and Bosch files by 'Object ID'
  - Object Text differs between files
  - 'RB_AS_Status' (from Bosch file) is in ['accepted', 'no_req', 'canceled_closed']
- **Finding Trigger**: Text differences with prohibited status values
- **Report Format**:
  ```
  Object ID: [object_id]
  ---------------
  Bosch File Name: [filename]
  Bosch File Object Text: [value]
  ---------------
  Customer File Name: [filename]
  Customer File Object Text: [value]
  ---------------
  RB_AS_Status: [status]
  ```

#### 7. Required Attributes Not Empty
**Method**: `check_required_attributes_not_empty`
- **Purpose**: Ensures critical attributes are not empty when requirement is active
- **Required Attributes**:
  - Object ID
  - Object Text
  - Technikvariante
  - Typ
- **Conditions**:
  - 'BRS_Status_Hersteller_Bosch_SDV0.1' is not 'verworfen'
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
  Issue: [attribute_name] is/are empty while BRS_Status_Hersteller_Bosch_SDV0.1 is not 'verworfen'.
  Details:
  Object ID: [id_value] (if available)
  Empty Attributes: [list_of_empty_columns]
  BRS_Status_Hersteller_Bosch_SDV0.1: [status_value]
  ```
  - Object ID is included in details when available for easy requirement tracing
  - Multiple empty attributes are listed under Empty Attributes
  - Grammar adapts to single/multiple empty attributes ("is"/"are")

#### 8. New Requirements Without CR-ID
**Method**: `check_new_requirements_without_cr_id`
- **Purpose**: Ensures new requirements have a CR-ID assigned
- **Conditions**:
  - 'Object ID' exists in customer file but not in Bosch reference file
  - 'CR-ID_Bosch_SDV0.1' is empty
- **Finding Trigger**: New requirement without CR-ID assignment
- **Report Format**:
  ```
  Object ID: [object_id]
  Typ: [typ_value]
  ---------------
  Customer File Name: [filename]
  Customer CR-ID_Bosch_SDV0.1: Empty
  ---------------
  Bosch File Name: [filename]
  Bosch Object ID: Not found
  ```
  - Includes hint that all new requirements should have a CR-ID assigned

#### 9. New CR Exists for Rejected Requirements
**Method**: `check_new_cr_exists_for_rejected_requirements`
- **Purpose**: Ensures a rejected requirement in the customer file comes with a *new* CR (i.e., CR-ID must not remain the same as in Bosch)
- **Reference File**:
  - Requires a Bosch reference file
  - Matches rows by `Object ID`
- **Conditions** (all must be true):
  - `BRS_Status_Hersteller_Bosch_SDV0.1` (Customer) == `verworfen`
  - `BRS_Status_Hersteller_Bosch_SDV0.1` (Bosch) != `verworfen`
  - `CR-ID_Bosch_SDV0.1` (Customer) == `CR-ID_Bosch_SDV0.1` (Bosch) (normalized)
- **Finding Trigger**: Customer rejects a requirement but the CR-ID is unchanged compared to Bosch (no new CR)
- **Erklärung**:
  - Wenn der Kunde eine Anforderung verwirft, darf dieser nicht ohne einen neuen CR erfolgen
  - Eine verworfene Anforderung muss mit einem CR bei Bosch kommen
- **Report Format**:
  ```
  Row: [row_number]
  Attribute: CR-ID_Bosch_SDV0.1, BRS_Status_Hersteller_Bosch_SDV0.1
  Issue: Customer is 'verworfen' while Bosch is not, and CR-ID is unchanged
  Value:
  Object ID: [object_id]
  ---------------
         Customer File Name: [filename]
         Customer CR-ID_Bosch_SDV0.1: [value]
         Customer BRS_Status_Hersteller_Bosch_SDV0.1: verworfen
  ---------------
         Bosch File Name: [filename]
         Bosch CR-ID_Bosch_SDV0.1: [value]
         Bosch BRS_Status_Hersteller_Bosch_SDV0.1: [value != verworfen]
  ```
  - Values are compared after normalization (whitespace/trailing commas ignored where applicable)

#### 10. CR Status Overwrite Protection
**Method**: `check_cr_status_overwrite_protection`
- **Purpose**: Prevents overwriting protected Bosch CR-Status values
- **Conditions**:
  - 'CR-ID_Bosch_SDV0.1' is present in customer and Bosch files
  - Customer 'CR-ID_Bosch_SDV0.1' == Bosch 'CR-ID_Bosch_SDV0.1' (normalized)
  - Bosch file has 'CR-Status_Bosch_SDV0.1' = '100' or '31' (with or without trailing comma)
  - Customer file has a different 'CR-Status_Bosch_SDV0.1' value
- **Finding Trigger**: Attempt to overwrite protected Bosch status (100 or 31) for the *same CR-ID*
- **Erklärung**:
  - Wenn der CR-ID vorhanden ist, und bei Bosch CR-Status 31 oder 100 ist,
  - dann darf der CR-Status nicht mit neuem CR-Status überschrieben werden
- **Report Format**:
  ```
  Object ID: [object_id]
  ---------------
  Customer File Name: [filename]
  Customer CR-ID_Bosch_SDV0.1: [value]
  Customer CR-Status_Bosch_SDV0.1: [value]
  ---------------
  Bosch File Name: [filename]
  Bosch CR-ID_Bosch_SDV0.1: [value]
  Bosch CR-Status_Bosch_SDV0.1: [value]
  ---------------
  Note: Bosch CR-Status '100' or '31' must not be overwritten.
  ```
  - Clearly indicates that protected status values should not be overwritten

### Export Checks
- No export checks implemented yet (placeholder exists)

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