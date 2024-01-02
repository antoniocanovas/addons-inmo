from odoo import _, api, fields, models


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

    def crear_recibos_de_inquilinos(self):
        for record in self:
            din = self.env.company.pnt_journal_inquilino_id
            subscriptions = self.env['sale.order'].search([
                ('sale_order_template_id.journal_id','=', din.id),
                ('state','in',['sale']),
                ('is_subscription','=',True),
                ('order_line','!=',False)
            ])
            for sub in subscriptions:
                nothing_to_do = False
                aml = env['account.move.line'].search([('subscription_id', '=', sub.id)])
                for li in aml:
                    if li.parent_state == 'draft':
                        nothing_to_do = True
                if nothing_to_do == False:
                    sub._cron_recurring_create_invoice()

