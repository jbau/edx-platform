from mock import patch

from django.test.utils import override_settings
from django.core.urlresolvers import reverse

import xmodule.tabs as tabs
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from .helpers import LoginEnrollmentTestCase


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class StaticTabDateTestCase(LoginEnrollmentTestCase, ModuleStoreTestCase):
    """Test cases for Static Tab Dates."""

    def setUp(self):
        self.course = CourseFactory.create()
        self.page = ItemFactory.create(
            category="static_tab", parent_location=self.course.location,
            data="OOGIE BLOOGIE", display_name="new_tab"
        )
        # The following XML course is closed; we're testing that
        # static tabs still appear when the course is already closed
        self.xml_data = "static 463139"
        self.xml_url = "8e4cce2b4aaf4ba28b1220804619e41f"
        self.xml_course_id = 'edX/detached_pages/2014'

    def test_logged_in(self):
        self.setup_user()
        url = reverse('static_tab', args=[self.course.id, 'new_tab'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("OOGIE BLOOGIE", resp.content)

    def test_anonymous_user(self):
        url = reverse('static_tab', args=[self.course.id, 'new_tab'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("OOGIE BLOOGIE", resp.content)

    @patch.dict('django.conf.settings.FEATURES', {'DISABLE_START_DATES': False})
    def test_logged_in_xml(self):
        self.setup_user()
        url = reverse('static_tab', args=[self.xml_course_id, self.xml_url])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.xml_data, resp.content)

    @patch.dict('django.conf.settings.FEATURES', {'DISABLE_START_DATES': False})
    def test_anonymous_user_xml(self):
        url = reverse('static_tab', args=[self.xml_course_id, self.xml_url])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.xml_data, resp.content)


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class DiscussionLinkTestCase(ModuleStoreTestCase):
    """Test cases for discussion link tab."""

    def setUp(self):
        self.tabs_with_discussion = [
            tabs.CoursewareTab(),
            tabs.CourseInfoTab(),
            tabs.DiscussionTab(),
            tabs.TextbookTabs(),
        ]
        self.tabs_without_discussion = [
            tabs.CoursewareTab(),
            tabs.CourseInfoTab(),
            tabs.TextbookTabs(),
        ]

    @staticmethod
    def _patch_reverse(course):
        """Allows tests to override the reverse function"""
        def patched_reverse(viewname, args):
            """Function to override the reverse function"""
            if viewname == "django_comment_client.forum.views.forum_form_discussion" and args == [course.id]:
                return "default_discussion_link"
            else:
                return None
        return patch("xmodule.tabs.reverse", patched_reverse)

    def check_discussion(self, course, expected_discussion_link, expected_can_display_value):
        """Helper function to verify whether the discussion tab exists and can be displayed"""
        discussion = tabs.CourseTabList.get_discussion(course)
        with self._patch_reverse(course):
            self.assertEquals(
                (
                    discussion is not None and
                    discussion.can_display(course, True, True) and
                    (discussion.link_func(course) == expected_discussion_link)
                ),
                expected_can_display_value
            )

    @patch.dict("django.conf.settings.FEATURES", {"ENABLE_DISCUSSION_SERVICE": False})
    def test_explicit_discussion_link(self):
        """Test that setting discussion_link overrides everything else"""
        self.check_discussion(
            CourseFactory.create(discussion_link="other_discussion_link", tabs=self.tabs_with_discussion),
            expected_discussion_link="other_discussion_link",
            expected_can_display_value=True
        )

    @patch.dict("django.conf.settings.FEATURES", {"ENABLE_DISCUSSION_SERVICE": False})
    def test_discussions_disabled(self):
        """Test that other cases return None with discussions disabled"""
        for i, tab_list in enumerate([[], self.tabs_with_discussion, self.tabs_without_discussion]):
            self.check_discussion(
                CourseFactory.create(tabs=tab_list, number=str(i)),
                expected_discussion_link=not None,
                expected_can_display_value=False,
            )

    @patch.dict("django.conf.settings.FEATURES", {"ENABLE_DISCUSSION_SERVICE": True})
    def test_no_tabs(self):
        """Test a course without tabs configured"""
        self.check_discussion(
            CourseFactory.create(),
            expected_discussion_link="default_discussion_link",
            expected_can_display_value=True
        )

    @patch.dict("django.conf.settings.FEATURES", {"ENABLE_DISCUSSION_SERVICE": True})
    def test_tabs_with_discussion(self):
        """Test a course with a discussion tab configured"""
        self.check_discussion(
            CourseFactory.create(tabs=self.tabs_with_discussion),
            expected_discussion_link="default_discussion_link",
            expected_can_display_value=True
        )

    @patch.dict("django.conf.settings.FEATURES", {"ENABLE_DISCUSSION_SERVICE": True})
    def test_tabs_without_discussion(self):
        """Test a course with tabs configured but without a discussion tab"""
        self.check_discussion(
            CourseFactory.create(tabs=self.tabs_without_discussion),
            expected_discussion_link=not None,
            expected_can_display_value=False,
        )
