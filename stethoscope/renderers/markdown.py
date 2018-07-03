# This is a renderer factory
# see https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html

from jinja2 import Environment, PackageLoader, select_autoescape
import markdown
import pdb

class MarkdownRenderer:
    JINJA_ENV = Environment(loader=PackageLoader('stethoscope', 'templates'),
                            autoescape=select_autoescape(['html', 'xml']))

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

        inner_html = markdown.markdown(contents)
        html = self.__wrap_with_jinja2_layout(inner_html, system['request'])

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

