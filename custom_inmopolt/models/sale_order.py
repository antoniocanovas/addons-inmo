from odoo import _, api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _rec_name = 'display_name'  # Esto le dice a Odoo que use display_name por defecto

    @api.depends('client_order_ref')
    def _compute_display_name(self):
        # Primero ejecutamos el súper para mantener el comportamiento estándar de Odoo
        super()._compute_display_name()

        for order in self:
            # Si el pedido tiene referencia de cliente, modificamos su display_name
            if order.client_order_ref:
                order.display_name = f"{order.name} - {order.client_order_ref}"


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
            ('next_invoice_date', '<=', date.today()),
            ('order_line', '!=', False),
            ('amount_untaxed', '>', 0),
        ])

        # Crear facturas de las suscripciones que no tienen facturas en "borrador" (el estándar corta si existen ya que no puede calcular el periodo):
        for sub in subscriptions:
            aml_draft = self.env['account.move.line'].search(
                [('subscription_id', '=', sub.id), ('parent_state', '=', 'draft')])
            if not (aml_draft.ids):
                # Para resolver incidencia 04/11/24 de un contrato con fecha de fin pero en vigor, corta el proceso:
                if not (sub.end_date) or (sub.end_date >= sub.next_invoice_date):
                    sub.action_invoice_subscription()

        # Confirmar las facturas de inquilinos:
        invoices = self.env['account.move'].search(
            [('partner_id','!=',False), ('state', '=', 'draft'), ('journal_id', '=', diarioinquilinos.id), ('move_type', '=', 'out_invoice')])
        for factura in invoices:
            if factura.invoice_line_ids.ids:
                factura.action_post()
