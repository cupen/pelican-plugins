#!/usr/bin/env python
"""Custom reST_ directive for plantuml_ integration.
   Adapted from ditaa_rst plugin.

.. _reST: http://docutils.sourceforge.net/rst.html
.. _plantuml: http://plantuml.sourceforge.net/
"""

import sys
import os

from docutils.nodes import image, literal_block
from docutils.parsers.rst import Directive, directives
from pelican import signals, logger

from .generateUmlDiagram import plantuml_render_to_file, name_with_hash


global_settings = None

def init_settings(settings):
    global global_settings
    global_settings = settings
    pass

class PlantUML_rst(Directive):
    """ reST directive for PlantUML """
    required_arguments = 0
    optional_arguments = 0
    has_content = True

    global global_siteurl

    option_spec = {
        'class' : directives.class_option,
        'alt'   : directives.unchanged,
        'format': directives.unchanged,
        "output": directives.unchanged,
    }

    def run(self):
        site_url = global_settings['SITEURL']
        output_dir = global_settings['OUTPUT_PATH']
        # print(f"output_dir={output_dir}")
        image_dir = os.path.abspath(os.path.join(output_dir, 'images'))
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        nodes = []
        body = '\n'.join(self.content)

        try:
            uml_format = self.options.get('format', 'png')
            fname = name_with_hash(body) + "." + uml_format
            fpath = os.path.join(image_dir, fname) 
            plantuml_render_to_file(body, uml_format, fpath)
            url = site_url +'/images/' + fname
        except Exception as exc:
            error = self.state_machine.reporter.error(
                'Failed to run plantuml: %s' % exc,
                literal_block(self.block_text, self.block_text),
                line=self.lineno)
            nodes.append(error)
        else:
            alt = self.options.get('alt', 'uml diagram')
            classes = self.options.pop('class', ['uml'])
            imgnode = image(uri=url, classes=classes, alt=alt)
            nodes.append(imgnode)

        return nodes

def pelican_init(pelicanobj):
    """ Prepare configurations for the MD plugin """
    init_settings(pelicanobj.settings)
    try:
        import markdown
        from .plantuml_md import PlantUMLMarkdownExtension
    except:
        # Markdown not available
        logger.debug("[plantuml] Markdown support not available")
        return

    # Register the Markdown plugin
    config = { 'siteurl': pelicanobj.settings['SITEURL'] }

    try:
        if 'MD_EXTENSIONS' in pelicanobj.settings.keys(): # pre pelican 3.7.0
            pelicanobj.settings['MD_EXTENSIONS'].append(PlantUMLMarkdownExtension(config))
        elif 'MARKDOWN' in pelicanobj.settings.keys() and \
             not ('extension_configs' in pelicanobj.settings['MARKDOWN']['extension_configs']):  # from pelican 3.7.0
            pelicanobj.settings['MARKDOWN']['extension_configs']['plantuml.plantuml_md'] = config
    except:
        logger.error("[plantuml] Unable to configure plantuml markdown extension")


def register():
    """Plugin registration."""
    signals.initialized.connect(pelican_init)
    directives.register_directive('uml', PlantUML_rst)
