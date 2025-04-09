import re
import pandas as pd


class HelperFunctions:

    @staticmethod
    def normalize_text(text, ignore_spaces_and_semicolons=True):
        """
        Normalize the given text by removing spaces, semicolons, quotes, and tab characters.
        This is the basic normalization function that preserves case and handles minimal character removal.

        :param text: The text to normalize.
        :param ignore_spaces_and_semicolons: Whether to remove spaces and semicolons.
        :return: The normalized text.
        """
        if not isinstance(text, str):
            return ""

        # Remove spaces, tabs, and semicolons if the option is enabled
        if ignore_spaces_and_semicolons:
            text = re.sub(r'[\s;\'"]', '', text)

        return text.strip()

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
