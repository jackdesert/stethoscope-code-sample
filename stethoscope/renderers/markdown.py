# This is a renderer factory
# see https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html

from jinja2 import Environment, PackageLoader, select_autoescape
import markdown
import ipdb
import re

class MarkdownRenderer:
    JINJA_ENV = Environment(loader=PackageLoader('stethoscope', 'templates'),
                            autoescape=select_autoescape(['html', 'xml']))

    TITLE_FROM_FILENAME_REGEX = re.compile('.*\/([a-z_]+)\.md')

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes:

        name (the renderer name),

        package (the package that was 'current' at the time the

        renderer was registered),

        type (the renderer type name),

        registry (the current application registry)

        settings (the deployment settings dictionary). """

    def __call__(self, value, system):
        # `value` is return value from view
        markdown_file = system['renderer_name']
        with open(markdown_file, 'r') as f:
            contents = f.read()

        breadcrumb_html = self.__breadcrumb(markdown_file)
        inner_html = breadcrumb_html + markdown.markdown(contents)
        inner_html_with_col_12 = self.__wrap_with_col_12(inner_html)

        html = self.__wrap_with_jinja2_layout(inner_html_with_col_12, system['request'])

        return html
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).

        * The value is the return value of a view.
        * The system value is a dictionary containing available system values

        (e.g., view, context, and request). """

    def __wrap_with_jinja2_layout(self, inner_html, request):

        # Pass the raw_html through a generic jinja2 template
        # so we can inherit from layout.jinja2
        generic_template = self.JINJA_ENV.get_template('generic.jinja2')
        html = generic_template.render(request=request,
                                       inner_html=inner_html)
        return html

    def __wrap_with_col_12(self, html):
        return(f"<div class='col-12'>\n{html}\n</div>")

    def __breadcrumb(self, markdown_file):
        match = self.TITLE_FROM_FILENAME_REGEX.match(markdown_file)
        if match:
            name = match[1]
            name = name.replace('_', ' ').title()
            return f"<div class='crumb'><a href='/' class='crumb__link'>Home</a> -> API Docs -> {name}"
