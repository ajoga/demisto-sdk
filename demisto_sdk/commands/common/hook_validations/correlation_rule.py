"""
This module is designed to validate the correctness of generic definition entities in content.
"""
import logging

from ruamel.yaml.comments import CommentedSeq

from demisto_sdk.commands.common.errors import Errors
from demisto_sdk.commands.common.hook_validations.base_validator import error_codes
from demisto_sdk.commands.common.hook_validations.content_entity_validator import (
    ContentEntityValidator,
)


class CorrelationRuleValidator(ContentEntityValidator):
    """
    CorrelationRuleValidator is designed to validate the correctness of the file structure we enter to content repo.
    """

    def __init__(
        self,
        structure_validator,
        ignored_errors=None,
        print_as_warnings=False,
        json_file_path=None,
    ):
        super().__init__(
            structure_validator,
            ignored_errors=ignored_errors,
            print_as_warnings=print_as_warnings,
            json_file_path=json_file_path,
        )
        self._is_valid = True

    def is_valid_file(self, validate_rn=True, is_new_file=False, use_git=False):
        """
        Check whether the correlation rule is valid or not
        Note: For now we return True regardless of the item content. More info:
        https://github.com/demisto/etc/issues/48151#issuecomment-1109660727
        """
        logging.debug(
            "Automatically considering XSIAM content item as valid, see issue #48151"
        )

        self.no_leading_hyphen()
        self.is_files_naming_correct()
        return self.is_valid

    def is_valid_version(self):
        """
        May deleted or be edited in the future by the use of XSIAM new content
        """
        pass

    @error_codes("CR100")
    def no_leading_hyphen(self):
        """

        Returns: False if type of current file is CommentSeq, which means the yaml starts with hyphen, True otherwise.

        """
        if isinstance(self.current_file, CommentedSeq):
            error_message, error_code = Errors.correlation_rule_starts_with_hyphen()
            if self.handle_error(error_message, error_code, file_path=self.file_path):
                self.is_valid = False
                return False
        return True

    @error_codes("CR101")
    def is_files_naming_correct(self):
        """
        Validates all file naming is as convention.
        """
        if not self.validate_xsiam_content_item_title(self.file_path):
            error_message, error_code = Errors.correlation_rules_files_naming_error(
                [self.file_path]
            )
            if self.handle_error(error_message, error_code, file_path=self.file_path):
                self._is_valid = False
                return False
        return True
