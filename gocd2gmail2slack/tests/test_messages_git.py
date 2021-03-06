import unittest
import pdb

from messages_git import (
    get_subject,
    is_gocd_pattern,
    get_gocd_details,
    get_timestamp,
    get_id,
    get_body,
    get_changeset_url,
    get_changeset_id,
    get_changeset_comment,
    get_changeset_author,
    get_changeset_info,
    get_changeset_info_multiple,
)

from fixtures.gmail_message_detail_1_git import (
    MESSAGE1,
    CHANGESET_MSG_ON_INDIVIDUAL_LINE,
    CHANGESET_MSG_INLINE_WITH_REVISION,
    CHANGESET_MSG_INLINE_WITH_REVISION_AND_AFFECTED_FILE,
    CHANGESET_MSG_MULTIPLE_COMMITS,
    CHANGESET_MSG_MULTIPLE_COMMITS_WITHMERGE,
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
        expected = 'https://code.domain.com/product/_git/repository/commit/49af92bdc06d2ccb3b193e96fd76c78a6ad4554b'
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
        self.assertEqual('DOMAIN\\\\committer', actual)

    def test_get_changeset_info(self):
        body = get_body(MESSAGE1)
        expected = {'id': '49af92bdc06d2ccb3b193e96fd76c78a6ad4554b', 'author': 'DOMAIN\\\\committer',
                    'comment': 'cloud config changes',
                    'url': 'https://code.domain.com/product/_git/repository/commit/49af92bdc06d2ccb3b193e96fd76c78a6ad4554b'}
        actual = get_changeset_info(body)
        self.assertDictEqual(expected, actual)

    def test_get_changeset_info_multiple(self):
        body = get_body(CHANGESET_MSG_MULTIPLE_COMMITS)
        expected = [{'id': 'a0df2066', 'author': 'Joey JoJo Shabadoo Jr',
                    'comment': 'This is comment #1',
                    'url': 'https://code.domain.com/product/_git/repository/commit/a0df2066abdef4bc29fb17049659577a347aab6a'},
                    {'id': 'a0df2067', 'author': 'DOMAIN\\\\User',
                    'comment': 'This is comment #2',
                    'url': 'https://code.domain.com/product/_git/repository/commit/a0df2067abdef4bc29fb17049659577a347aab6b'},
                    {'id': 'a0df2068', 'author': 'FredNoEmail',
                    'comment': 'This is comment #3',
                    'url': 'https://code.domain.com/product/_git/repository/commit/a0df2068abdef4bc29fb17049659577a347aab6c'}]
        actual = get_changeset_info_multiple(body)
        self.assertListEqual(expected, actual)

    def test_get_changeset_info_multiple_withmerge(self):
        body = get_body(CHANGESET_MSG_MULTIPLE_COMMITS_WITHMERGE)
        expected = [{'id': '1826859c', 'author': 'Fred Bloggs',
                    'comment': 'Merge branch \'hotfix/dostuff\' into develop',
                    'url': 'https://code.domain.com/product/_git/repository/commit/1826859ce5884515e455ab653077b8be104bead3'},
                    {'id': '93c02b5a', 'author': 'Oliver Nutherwun',
                    'comment': 'hotfix to fix stuff that was broken',
                    'url': 'https://code.domain.com/product/_git/repository/commit/93c02b5a8b63179037fd78f02184df6dea52c141'},
                    {'id': '4f7427cd', 'author': 'Brendan Butter',
                    'comment': 'Update Database Storage',
                    'url': 'https://code.domain.com/product/_git/repository/commit/4f7427cdd4181f8a4767481caad6c2529cfc1ee3'}]
        actual = get_changeset_info_multiple(body)
        self.assertListEqual(expected, actual)

class GocdDetailsTests(unittest.TestCase):

    def test_check_gocd_subject_pattern_valid(self):
        subjects = ['FW: Stage [proDuct.branch.CI/100/Package/1] passed',
                    'FW: Stage [product.branch.CI/0/Package/2] is fixed',
                    'Stage [product.braNch.Deploy.Test0/212/Package/1] passed',
                    'Stage [product2.branch2.CI/10999/Package/1] failed',
                    'Stage [prod.bch.Deploy.Test0/212/Package/1] is broken']
        for subject in subjects:
            self.assertTrue(is_gocd_pattern(subject))

    def test_check_gocd_subject_pattern_invalid(self):
        subjects = ['FW: Stage [product.branch.CI/100/Package/1] unknown',
                    'Stage [product.branch.CI/a/Package/1] passed']
        for subject in subjects:
            self.assertFalse(is_gocd_pattern(subject))

    def test_get_gocd_details(self):
        subject = 'FW: Stage [pr0duct5.br4nch.CI/100/Package/1] passed'
        expected = {'pipeline': 'pr0duct5.br4nch.CI',
                    'stage': 'Package',
                    'status': 'passed'}
        self.assertEqual(expected, get_gocd_details(subject))

    def test_get_gocd_details_status_2_words(self):
        subject = 'FW: Stage [pr0duct5.br4nch.CI/0/Package/2] is fixed'
        expected = {'pipeline': 'pr0duct5.br4nch.CI',
                    'stage': 'Package',
                    'status': 'is fixed'}
        self.assertEqual(expected, get_gocd_details(subject))
