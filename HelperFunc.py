import re
import pandas as pd


class HelperFunctions:

    @staticmethod
    def normalize_text(text, ignore_spaces_and_semicolons=False):
        """
        Normalize the given text for strict wording comparison.
        Removes all spaces, all types of quotes, and all line breaks, so only wording differences are detected.

        :param text: The text to normalize.
        :param ignore_spaces_and_semicolons: (ignored, always True in this mode)
        :return: The normalized text.
        """
        if not isinstance(text, str):
            return ""

        # Remove all types of quotes
        quotes = [
            '"', "'", '“', '”', '„', '‟', '‹', '›', '‘', '’', '‚', '‛',
            '`', '´', '′', '″', '❝', '❞', '❮', '❯', '❛', '❜', '❟', '＂', '＇'
        ]
        for q in quotes:
            text = text.replace(q, '')

        # Remove all whitespace (spaces, tabs, newlines, non-breaking spaces, etc.)
        text = re.sub(r'\s+', '', text, flags=re.UNICODE)
        text = text.replace('\u00A0', '')  # Non-breaking space

        # Remove invisible / zero-width Unicode characters that \s+ does not match
        # but which can appear in exported documents and cause false differences:
        #   \u00AD  Soft hyphen
        #   \u200B  Zero-width space
        #   \u200C  Zero-width non-joiner
        #   \u200D  Zero-width joiner
        #   \u200E  Left-to-right mark
        #   \u200F  Right-to-left mark
        #   \uFEFF  BOM / Zero-width no-break space
        text = re.sub(r'[\u00AD\u200B-\u200F\uFEFF]', '', text)

        # Remove semicolons
        text = text.replace(';', '')

        # Remove question marks — they appear as encoding artifacts in Bosch DOORS
        # exports when a special character (e.g. →, non-breaking space) cannot be
        # encoded, so a lone '?' between words should not trigger a finding.
        text = text.replace('?', '')

        # Remove other formatting characters if needed (dashes, etc.)
        # text = text.replace('-', '')  # Uncomment if you want to ignore dashes too

        # Replace special characters with standard ones (optional, for wording only)
        text = text.replace('⏐', '|')  # Replace box drawing character
        text = text.replace('½', '|')  # Replace half fraction
        text = text.replace('…', '...')  # Replace ellipsis
        text = text.replace('–', '-')  # Replace en dash
        text = text.replace('—', '-')  # Replace em dash

        return text.strip()

    @staticmethod
    def clean_ole_object_text(text):
        """
        Clean text by removing OLE Object references and normalizing spaces.

        This is used before text comparison so that embedded OLE placeholders
        (e.g. images represented as 'OLE Object') do not count as real wording
        differences.

        Also removes tool-generated error/import-failure messages for embedded
        objects that appear in different forms across files, e.g.:
          - <<ERROR: embedded object file '...' does not exist>>
          - <OR: embedded object '...' could not be imported>>
        """
        # Treat pandas NA / None / empty as empty string
        if pd.isna(text):
            return ""

        text_str = str(text)
        if not text_str:
            return ""

        # Remove various forms of OLE Object references
        text_str = text_str.replace("OLE Object", "")
        text_str = text_str.replace("DOOLE Object", "DO")

        # Remove tool-generated embedded-object error/import-failure placeholders.
        # These appear when an image cannot be rendered as text and take forms like:
        #   <<ERROR: embedded object file '...' does not exist>>
        #   <OR: embedded object '...' could not be imported>>
        text_str = re.sub(r'<{1,2}(?:ERROR|OR):[^>]*>{1,2}', '', text_str)

        # Normalize spaces (replace multiple spaces with single space)
        text_str = ' '.join(text_str.split())

        # Handle special cases with *) and similar patterns
        text_str = text_str.replace("DO*)", "DO *)")
        text_str = text_str.replace("DO )*", "DO *)")

        return text_str.strip()

    @staticmethod
    def normalize_text_advanced(text):
        """
        Advanced text normalization that removes more characters and converts to lowercase.
        This function is more aggressive in normalization compared to normalize_text().

        Key differences from normalize_text():
        1. Character Removal:
           - Removes all spaces between words except for meaningful separators
           - Removes semicolons, commas, and periods
           - Standardizes special characters and their spacing
        2. Case Handling:
           - Converts text to lowercase
        3. Input Handling:
           - Explicitly handles pandas NA values
           - Converts non-string inputs to string
        4. No Configurability:
           - Has fixed behavior with no parameters
           - Always performs all normalization steps

        :param text: The text to normalize.
        :return: The normalized text in lowercase with specified characters removed.
        """
        if pd.isna(text):
            return ""
            
        # Convert to string and strip whitespace
        text_str = str(text).strip()
        
        # Pre-process: standardize some common patterns
        text_str = text_str.replace("Ref.-ID", "refid")  # Standardize Ref.-ID pattern
        text_str = text_str.replace("Ref-ID", "refid")   # Variant
        text_str = text_str.replace("RefID", "refid")    # Variant
        
        # Remove all spaces around special characters and their combinations
        text_str = re.sub(r'\s*([/\-.,;:])\s*', r'\1', text_str)  # Remove spaces around special chars
        text_str = re.sub(r'\s+', ' ', text_str)  # Multiple spaces to single space
        
        # Handle special patterns
        text_str = re.sub(r'/\s*(\w+)\s*/', r'/\1/', text_str)  # Standardize /a/ pattern
        text_str = re.sub(r'(\d+)\s*/\s*(\d+)', r'\1/\2', text_str)  # Handle number/number pattern
        
        # Remove punctuation we want to ignore completely
        text_str = text_str.replace(";", "").replace(",", "").replace(".", "")
        
        # Final cleanup: normalize remaining spaces and convert to lowercase
        text_str = re.sub(r'\s+', ' ', text_str)
        return text_str.lower().strip()

    @staticmethod
    def normalize_symbols(text):
        """
        Normalizes special symbols in text by replacing them with their ASCII equivalents.
        This function can be customized by adding more symbol replacements as needed.
        
        Args:
            text (str): The text to normalize
            
        Returns:
            str: The normalized text with special symbols replaced
            
        Example:
            >>> HelperFunctions.normalize_symbols("σ, Sigma - für eine eindimensionale Normalverteilung")
            "s, Sigma - für eine eindimensionale Normalverteilung"
        """
        if not isinstance(text, str):
            return text
            
        # Dictionary of symbol replacements
        # Add new symbol replacements here as needed
        symbol_replacements = {
            'σ': 's',   # Sigma
            'Δ': '?',   # Delta
            'Ω': '?',   # Omega
            '→': '?',   # Arrow treated like question mark for comparison
            '◊': '?',   # Lozenge / diamond operator (DOORS exports this as '?')
        }
        
        # Replace each symbol with its ASCII equivalent
        for symbol, replacement in symbol_replacements.items():
            text = text.replace(symbol, replacement)
            
        return text
