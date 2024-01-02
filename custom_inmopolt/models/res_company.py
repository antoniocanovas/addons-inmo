# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    pnt_journal_inquilino_id = fields.Many2one('account.journal', string='Diario rec. inquilino', store=True)
    pnt_journal_propietario_id = fields.Many2one('account.journal', string='Diario rec. propietario', store=True)
