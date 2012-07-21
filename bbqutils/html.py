from __future__ import unicode_literals

from lxml import etree
import lxml.html

try:
    from io import StringIO
except:
    from StringIO import StringIO


HTML5_XMLDOC = StringIO("""<!DOCTYPE html>
<html>
    <head>
        <meta charset='utf-8'/>
        <title></title>
    </head>
    <body/>
</html>
""")


def create_html5_document(title, head=[], body=[], lang="en"):
    """Creates a HTML5 document."""

    def convert_to_nodes(root, nodels):
        for x in nodels:
            node = None
            if isinstance(x, str):
                node = lxml.html.fragment_fromstring(x)
            elif isinstance(x, (tuple, list)):
                node = etree.Element(x[0], x[1])
                node.text = x[2]
            elif isinstance(x, etree._Element):
                node = x
            if node is not None:
                root.append(node)
    
    doc = etree.parse(HTML5_XMLDOC, etree.XMLParser(remove_blank_text=True))
    doc.getroot().attrib['lang'] = lang
    doc.xpath('/html/head/title')[0].text = title

    convert_to_nodes(doc.xpath('/html/head')[0], head)
    convert_to_nodes(doc.xpath('/html/body')[0], body)

    return doc


def to_html_string(node):
    """convenience method"""

    return etree.tostring(node, method='html', pretty_print=True).decode()
