from odoo import _, api, fields, models
from datetime import datetime

class ProductProduct(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        result = []
        for order in self:
            name = order.name
            if order.client_order_ref:
                name += ' - ' + order.client_order_ref
            result.append((order.id, name))
        return result


    def inmopolt_create_subscription_invoices(self):
        # Crear y confirmar recibos de inquilinos hasta fecha hoy y los de otros diarios dejar en borrador:
        diarioinquilinos = self.env.company.pnt_journal_inquilino_id

        # Suscripciones con líneas, en vigor, con renovación de hoy o anterior de cualquier diario:
        subscriptions = self.env['sale.order'].search([
            ('is_subscription', '=', True),
            #  ('sale_order_template_id.journal_id','=',diarioinquilinos.id),
            ('state', '=', 'sale'),
            ('stage_category', '=', 'progress'),
            ('next_invoice_date', '!=', False),
            ('next_invoice_date', '<', datetime.now()),
            ('order_line', '!=', False),
            ('amount_untaxed', '>', 0)
        ])

        # Crear facturas de las suscripciones que no tienen facturas en "borrador" (el estándar corta si existen ya que no puede calcular el periodo):
        for sub in subscriptions:
            aml_draft = self.env['account.move.line'].search(
                [('subscription_id', '=', sub.id), ('parent_state', '=', 'draft')])
            if not (aml_draft.ids):
                sub.action_invoice_subscription()

        # Confirmar las facturas de inquilinos:
        invoices = self.env['account.move'].search(
            [('state', '=', 'draft'), ('journal_id', '=', diarioinquilinos.id), ('move_type', '=', 'out_invoice')])
        for factura in invoices:
            factura.action_post()
