# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
# matplotlib.use('Agg')
import logging
from matplotlib import font_manager
import os
import arabic_reshaper
from bidi.algorithm import get_display
from odoo.tools import is_html_empty
_logger = logging.getLogger(__name__)


class ReportProjectStatus(models.AbstractModel):
    _name = 'report.project_base.project_status_qweb_report'
    _description = 'Project Status QWeb Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        projects = self.env['project.project'].browse(docids)
        chart_map = {}

        for project in projects:
            try:
                chart = self._get_chart_image(project)
            except Exception as e:
                _logger.error(f"Chart error for project {project.id}: {str(e)}")
                chart = False

            chart_map[project.id] = chart

        return {
            'doc_ids': docids,
            'doc_model': 'project.project',
            'docs': projects,
            'chart_map': chart_map,
            'is_html_empty': is_html_empty,
        }

    def get_all_fonts_paths(self):
        font_extensions = ('.ttf')
        # '.otf', '.woff', '.woff2'
        fonts_dict = {}

        installed_modules = self.env['ir.module.module'].sudo().search([('state', '=', 'installed')]).mapped('name')
        installed_modules_set = set(installed_modules)

        from odoo.tools import config
        addons_paths = config.get('addons_path', '').split(',')

        for addons_path in addons_paths:
            if not addons_path:
                continue
            addons_path = addons_path.strip()
            if not os.path.exists(addons_path):
                continue
            for module_name in os.listdir(addons_path):
                module_path = os.path.join(addons_path, module_name)
                if os.path.isdir(module_path) and module_name in installed_modules_set:
                    for root, dirs, files in os.walk(module_path):
                        for file in files:
                            if file.lower().endswith(font_extensions):
                                full_path = os.path.join(root, file)
                                font_name = os.path.splitext(file)[0].lower()  # Lowercase
                                fonts_dict[font_name] = full_path

        return fonts_dict

    def _get_chart_image(self, project):
        task_data = {
            'new': project.task_count_new or 0,
            'in_progress': project.task_count_inprogress or 0,
            'done': project.task_count_finished or 0,
        }

        if sum(task_data.values()) == 0:
            task_data = {'new': 1, 'in_progress': 1, 'done': 1}

        fig = plt.figure(figsize=(5, 4))
        fonts = self.get_all_fonts_paths()
        prop = None
        company_font_name = self.env.company.sudo().font

        if company_font_name:
            font_path = None
            for font_name, path in fonts.items():
                if font_name.startswith(company_font_name.lower()):
                    font_path = path
                    break

            if font_path:
                font_manager.fontManager.addfont(font_path)
                prop = font_manager.FontProperties(fname=font_path)

        def format_arabic(text):
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text

        arabicLabels = ['جديد', 'قيد التنفيذ', 'تم']
        labels = [format_arabic(label) for label in arabicLabels]
        sizes = [task_data['new'], task_data['in_progress'], task_data['done']]
        colors = ['#f0312e', '#add8e6', '#90ee90']

        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontproperties': prop, 'fontsize': 12} if prop else {'fontsize': 12}
        )
        for autotext in autotexts:
            autotext.set_fontsize(12)
            if hasattr(autotext, 'set_fontproperties'):
                autotext.set_fontproperties(None)

        plt.axis('equal')
        plt.rcParams['font.size'] = 12
        title_text = format_arabic('احصائيات المهام')
        plt.title(title_text, fontproperties=prop, fontsize=16) if prop else plt.title(title_text)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close('all')

        chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        _logger.info(f"Generated chart image with base64 length: {len(chart_image)}")

        return chart_image
