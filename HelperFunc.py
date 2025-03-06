import re


class HelperFunctions:

    @staticmethod
    def normalize_text(text, ignore_spaces_and_semicolons=True):
        """
        Normalize the given text by removing spaces, semicolons, quotes, and tab characters.

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
