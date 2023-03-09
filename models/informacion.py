# -*- coding: utf-8 -*-
import os

from odoo import models, fields, api
from odoo.exceptions import ValidationError, RedirectWarning


class informacion(models.Model):
    _name = 'odoo_basico.informacion'
    _description = 'Exemplo para informacion'
    _sql_constraints = [('nomeUnico', 'unique(name)', 'Non se pode repetir o Título')]
    _order = "descripcion desc"

    name = fields.Char(string="Título:")
    descripcion = fields.Text(string="A descripción:")
    peso = fields.Float(string="Peso en KGs.",default=4.3,digits=(6,2))
    sexo_traducido = fields.Selection([('Mujer','Muller'),('Hombre','Home'),('Otros','Outros')],string="Sexo")
    autorizado = fields.Boolean(string="¿Autorizado?", default=True)
    alto_en_cms = fields.Integer(string="Alto en Cms:")
    ancho_en_cms = fields.Integer(string="Ancho en Cms:")
    longo_en_cms = fields.Integer(string="Longo en Cms:")
    volume = fields.Float(compute="_volume",string="Volume en Metros Cúbicos",digits=(6,6), store=True)
    densidade = fields.Float(compute="_densidade",string="Densidade en Kgs/Metros Cúbicos", store=True)
    literal = fields.Char(store=False)
    foto = fields.Binary(string='Foto')
    adxunto_nome = fields.Char(string="Nome Adxunto")
    adxunto = fields.Binary(string="Arquivo adxunto")
    moeda_id = fields.Many2one('res.currency', domain="[('position','=','after')]")
    moeda_euro_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', "EUR")],limit=1))
    moeda_en_texto = fields.Char(related="moeda_id.currency_unit_label",string="Moeda en formato texto",store=True)

    creador_da_moeda = fields.Char(related="moeda_id.create_uid.login",
                                   string="Usuario creador da moeda", store=True)

    gasto_en_euros = fields.Monetary("Gasto en euros", 'moeda_euro_id')
    data = fields.Date(string="Data", default=lambda self: fields.Date.today())
    data_hora = fields.Datetime(string="Data e Hora", default=lambda self: fields.Datetime.now())
    hora_utc = fields.Char(compute="_hora_utc", string="Hora UTC", size=15, store=True)
    hora_actual = fields.Char(compute="_hora_actual", string="Hora Actual", size=15, store=True)
    hora_timezone_usuario = fields.Char(compute="_hora_timezone_usuario", string="Hora Timezone do Usuario", size=15,
                                        store=True)
    mes_castelan = fields.Char(compute="_mes_castelan", size=15, string="Mes castelán", store=True)
    mes_galego = fields.Char(compute="_mes_galego", size=15, string="Mes galego", store=True)
    mes_frances = fields.Char(compute="_mes_frances", size=15, string="Mes francés", store=True)
    mes_ingles = fields.Char(compute="_mes_ingles", size=15, string="Mes inglés", store=True)
    @api.depends('alto_en_cms', 'longo_en_cms', 'ancho_en_cms')
    def _volume(self):
      for rexistro in self:
          rexistro.volume =  (float(rexistro.alto_en_cms) * float(rexistro.longo_en_cms) *
                              float(rexistro.ancho_en_cms))/1000000
    @api.depends('peso', 'volume')
    def _densidade(self):
        for rexistro in self:
            if rexistro.volume != 0:
                rexistro.densidade = (float(rexistro.peso) / float(rexistro.volume))
            else:
                rexistro.densidade = 0
    @api.onchange('alto_en_cms')
    def _avisoAlto(self):
        for rexistro in self:
            if rexistro.alto_en_cms > 7:
                rexistro.literal = 'O alto ten un valor posiblemente excesivo %s é maior que 7' % rexistro.alto_en_cms
            else:
                rexistro.literal = ""

    @api.constrains('peso')  # Ao usar ValidationError temos que importar a libreria ValidationError
    def _constrain_peso(self):  # from odoo.exceptions import ValidationError
        for rexistro in self:
            if rexistro.peso < 1 or rexistro.peso > 6:
                raise ValidationError('Os peso de %s ten que ser entre 1 e 6 ' % rexistro.name)

    def _cambia_campo_sexo(self, rexistro):
        rexistro.sexo_traducido = "Hombre"

    def ver_contexto(self):  # Este método é chamado dende un botón de informacion.xml
        for rexistro in self:
            # Para visualizar a mensaxe podemos utilizar ValidationError ou RedirectWarning

            # ValidationError
            # Ao usar warning temos que importar a libreria mediante from odoo.exceptions import Warning
            # Importamos tamén a libreria os mediante import os
            # raise ValidationError(
            #     'Contexto: %s Ruta: %s Contido %s' % (rexistro.env.context, os.getcwd(), os.listdir(os.getcwd())))
            # env.context é un diccionario  https://www.w3schools.com/python/python_dictionaries.asp

            #RedirectWarning
            # vemos o id externo da acción no ficheiro informacion.xml na definición da acción model="ir.actions.act_window"
            action = self.env.ref('odoo_basico.informacion_list_action')
            # env.context é un diccionario  https://www.w3schools.com/python/python_dictionaries.asp
            contexto = rexistro.env.context
            msg = 'Contexto: %s Ruta: %s Contido %s' % (contexto, os.getcwd(), os.listdir(os.getcwd()))
            # Importamos a libreria os mediante import os
            raise RedirectWarning(msg, action.id, ('Aceptar'))
            # Ao usar RedirectWarning temos que importar a libreria mediante from odoo.exceptions import RedirectWarning
        return True

    @api.depends('data_hora')
    def _hora_utc(self):
        for rexistro in self:  # A hora se almacena na BD en horario UTC (2 horas menos no verán, 1 hora menos no inverno)
            rexistro.hora_utc = rexistro.data_hora.strftime("%H:%M:%S")

    def actualiza_hora_actual_UTC(
            self):  # Esta función é chamada dende un boton de informacion.xml e dende _hora_actual
        for rexistro in self:
            rexistro.hora_actual = fields.Datetime.now().strftime("%H:%M:%S")
        # Grava a hora en UTC, se quixesemos poderiamos usar a función  _convirte_data_hora_de_utc_a_timezone_do_usuario

    @api.depends('data_hora')
    def _hora_actual(self):
        for rexistro in self:
            rexistro.actualiza_hora_actual_UTC()
        # Esta función será chamada dende a función actualiza_hora_timezone_usuario_dende_boton_e_apidepends e
        #  dende pedido.py (Cando insertamos os valores do template self.env.user.tz non ten o timezone do usuario por iso se carga coa hora UTC,
        #  o botón en pedido.py é para actualizar todos os rexistros masivamente dende outro modelo)

    def convirte_data_hora_de_utc_a_timezone_do_usuario(self,
                                                        data_hora_utc_object):  # recibe a data hora en formato object
        usuario_timezone = pytz.timezone(
            self.env.user.tz or 'UTC')  # obter a zona horaria do usuario. Ollo!!! nas preferencias do usuario ten que estar ben configurada a zona horaria
        return pytz.UTC.localize(data_hora_utc_object).astimezone(
            usuario_timezone)  # hora co horario do usuario en formato object
        # para usar  pytz temos que facer  import pytz

    def actualiza_hora_timezone_usuario(self, obxeto_rexistro):
        obxeto_rexistro.hora_timezone_usuario = self.convirte_data_hora_de_utc_a_timezone_do_usuario(
            obxeto_rexistro.data_hora).strftime("%H:%M:%S")  # Convertimos a hora de UTC a hora do timezone do usuario

    def actualiza_hora_timezone_usuario_dende_boton_e_apidepends(
            self):  # Esta función é chamada dende un boton de informacion.xml e dende @api.depends _hora_timezone_usuario
        self.actualiza_hora_timezone_usuario(
            self)  # leva self como parametro por que actualiza_hora_timezone_usuario ten 2 parametros
        # porque usamos tamén actualiza_hora_timezone_usuario dende outro modelo (pedido.py) e lle pasamos como parámetro o obxeto_rexistro

    @api.depends('data_hora')
    def _hora_timezone_usuario(self):
        for rexistro in self:
            rexistro.actualiza_hora_timezone_usuario_dende_boton_e_apidepends()

    # Podemos  configurar locales a nivel de sistema con dpkg-reconfigure locales poñendo un por defecto.
    # apt-get install locales
    # dpkg-reconfigure locales (podemos configurar varios)
    # locale (ver o locale por defecto)
    # locale -a (ver os dispoñibles)

    @api.depends('data')
    def _mes_castelan(self):
        # O idioma por defecto é o configurado en locale na máquina onde se executa odoo.
        # Podemos cambialo con locale.setlocale, os idiomas teñen que estar instalados na máquina onde se executa odoo.
        # Lista onde podemos ver os distintos valores: https://docs.moodle.org/dev/Table_of_locales#Table
        # Definimos en miñasUtilidades un método para asignar o distinto literal que ten o idioma en función da plataforma Windows ou GNULinux
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('Spanish_Spain.1252', 'es_ES.utf8'))
        for rexistro in self:
            rexistro.mes_castelan = rexistro.data.strftime("%B")  # strftime https://strftime.org/

    @api.depends('data')
    def _mes_galego(self):
        # O idioma por defecto é o configurado en locale na máquina onde se executa odoo.
        # Podemos cambialo con locale.setlocale, os idiomas teñen que estar instalados na máquina onde se executa odoo.
        # Lista onde podemos ver os distintos valores: https://docs.moodle.org/dev/Table_of_locales#Table
        # Definimos en miñasUtilidades un método para asignar o distinto literal que ten o idioma en función da plataforma Windows ou GNULinux
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('Galician_Spain.1252', 'gl_ES.utf8'))
        for rexistro in self:
            rexistro.mes_galego = rexistro.data.strftime("%B")
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('Spanish_Spain.1252', 'es_ES.utf8'))

    @api.depends('data')
    def _mes_frances(self):
        # O idioma por defecto é o configurado en locale na máquina onde se executa odoo.
        # Podemos cambialo con locale.setlocale, os idiomas teñen que estar instalados na máquina onde se executa odoo.
        # Lista onde podemos ver os distintos valores: https://docs.moodle.org/dev/Table_of_locales#Table
        # Definimos en miñasUtilidades un método para asignar o distinto literal que ten o idioma en función da plataforma Windows ou GNULinux
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('French_France.1252', 'fr_FR.utf8'))
        for rexistro in self:
            rexistro.mes_frances = rexistro.data.strftime("%B")
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('Spanish_Spain.1252', 'es_ES.utf8'))

    @api.depends('data')
    def _mes_ingles(self):
        # O idioma por defecto é o configurado en locale na máquina onde se executa odoo.
        # Podemos cambialo con locale.setlocale, os idiomas teñen que estar instalados na máquina onde se executa odoo.
        # Lista onde podemos ver os distintos valores: https://docs.moodle.org/dev/Table_of_locales#Table
        # Definimos en miñasUtilidades un método para asignar o distinto literal que ten o idioma en función da plataforma Windows ou GNULinux
        locale.setlocale(locale.LC_TIME,
                         miñasUtilidades.cadeaTextoSegunPlataforma('English_Australia.1252', 'en_US.utf8'))
        for rexistro in self:
            rexistro.mes_ingles = rexistro.data.strftime("%B")
        locale.setlocale(locale.LC_TIME, miñasUtilidades.cadeaTextoSegunPlataforma('Spanish_Spain.1252', 'es_ES.utf8'))

    def envio_email(self):
        meu_usuario = self.env.user
        # mail_de     Odoo pon o email que configuramos en gmail para facer o envio
        mail_reply_to = meu_usuario.partner_id.email  # o enderezo email que ten asociado o noso usuario
        mail_para = 'antoniocrespo@edu.xunta.gal'  # o enderezo email de destino
        mail_valores = {
            'subject': 'Aquí iría o asunto do email ',
            'author_id': meu_usuario.id,
            'email_from': mail_reply_to,
            'email_to': mail_para,
            'message_type': 'email',
            'body_html': 'Aquí iría o corpo do email cos datos por exemplo de "%s" ' % self.descripcion,
        }
        mail_id = self.env['mail.mail'].create(mail_valores)
        mail_id.sudo().send()
        return True