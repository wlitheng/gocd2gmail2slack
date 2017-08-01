import unittest
import pdb

from messages_git import (
    get_subject,
    # is_gocd_pattern,
    # get_gocd_details,
    get_timestamp,
    get_id,
    get_body,
    get_changeset_url,
    get_changeset_id,
    get_changeset_comment,
    get_changeset_author,
    get_changeset_info,
)

from fixtures.gmail_message_detail_1_git import (
    MESSAGE1,
    CHANGESET_MSG_ON_INDIVIDUAL_LINE,
    CHANGESET_MSG_INLINE_WITH_REVISION,
    CHANGESET_MSG_INLINE_WITH_REVISION_AND_AFFECTED_FILE,
)


class MessageDetailsTests(unittest.TestCase):

    def test_get_subject(self):
        actual = get_subject(MESSAGE1)
        expected = 'FW: Stage [product.branch.CI/100/Package/1] passed'
        self.assertEqual(expected, actual)

    def test_get_internal_date_returns_utc_timestamp(self):
        actual = get_timestamp(MESSAGE1)
        self.assertEqual('1452243312000', actual)

    def test_get_id(self):
        actual = get_id(MESSAGE1)
        self.assertEqual('1522072655d6e615', actual)

    def test_get_body(self):
        actual = get_body(MESSAGE1)
        self.assertIn('CHECK-INS', actual)


class MessageBodyTests(unittest.TestCase):

    def test_get_changeset_url(self):
        body = get_body(MESSAGE1)
        actual = get_changeset_url(body)
        expected = 'https://code@code.domain.com/product/_git/repository/commit/49af92bdc06d2ccb3b193e96fd76c78a6ad4554b'
        self.assertEqual(expected, actual)

    def test_get_changeset_id(self):
        body = get_body(MESSAGE1)
        actual = get_changeset_id(body)
        self.assertEqual('49af92bdc06d2ccb3b193e96fd76c78a6ad4554b', actual)

    def test_get_changeset_comment_from_individual_line(self):
        body = get_body(CHANGESET_MSG_ON_INDIVIDUAL_LINE)
        actual = get_changeset_comment(body)
        self.assertEqual('cloud config changes', actual)

    def test_get_changeset_comment_inline_with_revision(self):
        body = get_body(CHANGESET_MSG_INLINE_WITH_REVISION)
        actual = get_changeset_comment(body)
        self.assertEqual('cloud config changes', actual)

    def test_get_changeset_comment_inline_with_revision_affected_file(self):
        body = get_body(CHANGESET_MSG_INLINE_WITH_REVISION_AND_AFFECTED_FILE)
        actual = get_changeset_comment(body)
        self.assertEqual('cloud config changes', actual)

    def test_get_changeset_author(self):
        body = get_body(MESSAGE1)
        actual = get_changeset_author(body)
        self.assertEqual('committer', actual)

    def test_get_changeset_info(self):
        body = get_body(MESSAGE1)
        expected = {'id': '49af92bdc06d2ccb3b193e96fd76c78a6ad4554b', 'author': 'committer',
                    'comment': 'cloud config changes',
                    'url': 'https://code@code.domain.com/product/_git/repository/commit/49af92bdc06d2ccb3b193e96fd76c78a6ad4554b'}
        actual = get_changeset_info(body)
        self.assertDictEqual(expected, actual)