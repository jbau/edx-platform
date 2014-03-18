# disable missing docstring
#pylint: disable=C0111

from lettuce import world, step
from nose.tools import assert_in  # pylint: disable=no-name-in-module


@step('I have created a Blank HTML Page$')
def i_created_blank_html_page(step):
    world.create_course_with_unit()
    world.create_component_instance(
        step=step,
        category='html',
        component_type='Text'
    )


@step('I see only the HTML display name setting$')
def i_see_only_the_html_display_name(step):
    world.verify_all_setting_entries([['Display Name', "Text", False]])


@step('I have created an E-text Written in LaTeX$')
def i_created_etext_in_latex(step):
    world.create_course_with_unit()
    step.given('I have enabled latex compiler')
    world.create_component_instance(
        step=step,
        category='html',
        component_type='E-text Written in LaTeX'
    )


@step('I edit the page$')
def i_click_on_edit_icon(step):
    world.edit_component()


@step('I add an image with a static link via the Image Plugin Icon$')
def i_click_on_image_plugin_icon(step):
    # Click on image plugin button
    world.css_click('.mce-i-image')

    # Wait for the editing window to open.
    world.wait_for_visible('.mce-window')

    # Fill in the first field (source).
    world.css_fill('.mce-textbox', '/static/image.jpg', 0)
    # Click OK
    world.css_click('.mce-primary')


@step('the image static link is rewritten to translate the path$')
def image_static_link_is_rewritten(step):
    # Find the TinyMCE iframe within the main window
    with world.browser.get_iframe('mce_0_ifr') as tinymce:
        image = tinymce.find_by_tag('img').first

        # Test onExecCommandHandler set the url to absolute.
        assert_in('c4x/MITx/999/asset/image.jpg', image['src'])
