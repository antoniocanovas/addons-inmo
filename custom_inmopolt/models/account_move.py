from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'


    def inmopolt_auto_reconcile_paid_invoices(self):
        # Marcar como pagadas los recibos y facturas si la deuda es nula (evitar reconciliar con el banco):
        for record in self:
            if (record.move_type in ['in_invoice','in_refund','out_invoice','out_refund']) and
                (record.payment_state == 'in_payment') and
                (record.amount_residual == 0):
                    record['payment_state'] = 'paid'
