# -*- coding: utf-8 -*-

from odoo import models, fields, api

class lineapedido(models.Model):
    _name = 'odoo_basico.lineapedido'
    _description = 'Exemplo para lineapedido'

    name = fields.Char(required=True, size=20, string="lineapedido")
    descripcion_da_lineapedido= fields.Text(string="A Descripción do lineapedido")  # string é a etiqueta do campo

    pedido_id = fields.Many2one('odoo_basico.pedido', ondelete= "cascade",required=True)

    informacion_ids = fields.Many2many("odoo_basico.informacion",
                                       string="Rexistro de Información",
                                       relation="odoo_basico_lineapedido_informacion",
                                       column1="lineapedido_id", column2="informacion_id")