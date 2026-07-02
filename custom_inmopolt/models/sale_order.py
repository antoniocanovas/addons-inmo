from odoo import _, api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('client_order_ref')
    def _onchange_client_order_ref(self):
        """
        Cada vez que el usuario cambie la referencia en la pantalla,
        el nombre se actualizará automáticamente en tiempo real.
        """
        for order in self:
            if not order.name:
                continue

            # 1. Limpiamos cualquier referencia vieja que ya estuviera en el nombre
            nombre_base = order.name
            if " - " in nombre_base:
                # Separamos por el primer " - " para recuperar el código original (ej: SO001)
                nombre_base = nombre_base.split(" - ", 1)[0]

            # 2. Si hay una nueva referencia, la pegamos. Si la borraron, dejamos el nombre base limpio.
            if order.client_order_ref:
                order.name = f"{nombre_base} - {order.client_order_ref}"
            else:
                order.name = nombre_base

    def inmopolt_create_subscription_invoices(self):
        # Crear y confirmar recibos de inquilinos hasta fecha hoy y los de otros diarios dejar en borrador:
        diarioinquilinos = self.env.company.pnt_journal_inquilino_id

        # Suscripciones con líneas, en vigor, con renovación de hoy o anterior de cualquier diario:
        subscriptions = self.env['sale.order'].search([
            ('is_subscription', '=', True),
            #  ('sale_order_template_id.journal_id','=',diarioinquilinos.id),
            ('state', '=', 'sale'),
            ('subscription_state', '=', '3_progress'),
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
                    sub.order_line._reset_subscription_qty_to_invoice()
                    invoices = sub._create_invoices(final=True)
                    # Confirmar solo las facturas del diario de inquilinos; el resto quedan en borrador:
                    for invoice in invoices.filtered(lambda m: m.journal_id == diarioinquilinos and m.invoice_line_ids):
                        invoice.action_post()
