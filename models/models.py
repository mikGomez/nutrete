# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import logging
import re

class Cliente(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    is_cliente = fields.Boolean()

    dni = fields.Char(string="DNI", required=True)
    historial = fields.Text(string="Historial")
    motivo_consulta = fields.Text(string="Motivo de Consulta")
    fecha_nacimiento = fields.Date( default=datetime(1990, 12, 5),string="Fecha de Nacimiento")
    peso = fields.Float(default=55.00,string="Peso")
    altura = fields.Float(default=1.65,string="Altura")
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)
    sexo = fields.Selection([
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro')
    ], string="Sexo", default='femenino')
    @api.constrains('dni')
    def _check_code(self):
        regex = re.compile('^[0-9]{8}[a-z]$', re.I)
        for clie in self:
            if not regex.match(clie.dni):
                raise ValidationError('Formato de DNI incorrecto')

    _sql_constraints = [('dni_unique', 'unique(dni)', 'DNI ya existente.')]

    @api.constrains('altura')
    def _check_code2(self):
        for alt in self:
            if alt.altura <= 0:
                raise ValidationError(_('Formato altura incorrecto, tiene que ser mayor que 0'))
    @api.constrains('peso')
    def _check_code3(self):
        for pes in self:
            if pes.peso <= 0:
                raise ValidationError(_('Formato Peso incorrecto, tiene que ser mayor que 0'))

    @api.onchange('is_cliente')
    def _onchange_is_cliente(self):
        categories = self.env['res.partner.category'].search([('name','=','Cliente')])
        if len(categories) > 0:
            category = categories[0]
        else:
            category = self.env['res.partner.category'].create({'name':'Cliente'})
        self.category_id = [(4, category.id)] 

    @api.depends('peso', 'altura')
    def _compute_imc(self):
        for cliente in self:
            try:
                if cliente.peso and cliente.altura:
                    cliente.imc = cliente.peso / (cliente.altura * cliente.altura)
                else:
                    cliente.imc = 0.0
            except ZeroDivisionError:
                cliente.imc = 0.0

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        today = datetime.today()
        for cliente in self:
            try:
                if cliente.fecha_nacimiento:
                    fecha_nacimiento_str = cliente.fecha_nacimiento.strftime("%Y-%m-%d")
                    born = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d")
                    cliente.edad = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                else:
                    cliente.edad = 0
            except ValueError:
                cliente.edad = 0

class Dietista(models.Model):
    _name = 'res.partner'
    _description = 'Dietista de Nutrete'
    _inherit = 'res.partner'
    is_dietista = fields.Boolean()

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI", required=True)
    especialidad = fields.Selection([('vegetariana', 'Dieta Vegetariana'),
                                     ('paleo', 'Dieta Paleo'),
                                     ('detox', 'Dieta Detox'),
                                     ('hipocalorica', 'Dieta Hipocalórica'),
                                     ('proteica', 'Dieta Proteica')],
                                    string="Especialidad",default='proteica')
    @api.constrains('especialidad')
    def _check_especialidad(self):
        for diet in self:
            if not diet.especialidad:
                raise ValidationError('La especialidad debe ser seleccionada')
    @api.constrains('dni')
    def _check_code(self):
        regex = re.compile('^[0-9]{8}[a-z]$', re.I)
        for die in self:
            if not regex.match(die.dni):
                raise ValidationError('Formato de DNI incorrecto')
    _sql_constraints = [('dni_unique', 'unique(dni)', 'DNI ya existente.')]
        
    @api.onchange('is_dietista')
    def _onchange_is_dietista(self):
        categories = self.env['res.partner.category'].search([('name','=','Dietista')])
        if len(categories) > 0:
            category = categories[0]
        else:
            category = self.env['res.partner.category'].create({'name':'Dietista'})
        self.category_id = [(4, category.id)] 


class Nutricionista(models.Model):
    _name = 'res.partner'
    _description = 'Nutricionista de Nutrete'
    _inherit = 'res.partner'
    is_nutricionista = fields.Boolean()

    name = fields.Char(string="Nombre", required=True)
    dni = fields.Char(string="DNI")
    especialidad = fields.Selection([('deportiva', 'Nutrición Deportiva'),
                                     ('pediatrica', 'Nutrición Pediátrica'),
                                     ('clinica', 'Nutrición Clínica')],
                                    string="Especialidad",default='deportiva')
    @api.constrains('dni')
    def _check_code(self):
        regex = re.compile('^[0-9]{8}[a-z]$', re.I)
        for nutri in self:
            if not regex.match(nutri.dni):
                raise ValidationError('Formato de DNI incorrecto')
    _sql_constraints = [('dni_unique', 'unique(dni)', 'DNI ya existente.')]

    @api.onchange('is_nutricionista')
    def _onchange_is_nutricionista(self):
        categories = self.env['res.partner.category'].search([('name','=','Nutricionista')])
        if len(categories) > 0:
            category = categories[0]
        else:
            category = self.env['res.partner.category'].create({'name':'Nutricionista'})
        self.category_id = [(4, category.id)] 

class Dieta(models.Model):
    _name = 'nutrete.dieta'
    _description = 'Dieta de Nutrete'

    cliente_id = fields.Many2one('res.partner', string="Cliente")
    nutricionista_id = fields.Many2one('res.partner', string="Nutricionista")
    dietista_id = fields.Many2one('res.partner', string="Dietista")
    revision_ids = fields.One2many('nutrete.revision', 'dieta_id', string="Revisiones")


class Revision(models.Model):
    _name = 'nutrete.revision'
    _description = 'Revisión de Dieta'

    fecha = fields.Date(string="Fecha")
    hora = fields.Float(default=17.00,string="Hora")
    dieta_id = fields.Many2one('nutrete.dieta', string="Dieta")
    peso = fields.Float(default=55.00,string="Peso")
    comentarios = fields.Text(string="Comentarios")
    actividad_fisica = fields.Selection([
    ('sedentario', 'Sedentario'),
    ('activo', 'Activo'),
    ('elite', 'Elite')
], string="Actividad Física",default ='activo')
    evolucion = fields.Selection([('excelente', 'Excelente'),
                                   ('buena', 'Buena'),
                                   ('regular', 'Regular'),
                                   ('mala', 'Mala')],
                                  string="Evolución",default='buena')
    cliente_id = fields.Many2one('res.partner', related='dieta_id.cliente_id', store=True)
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)
    calorias_diarias_recomendadas = fields.Integer(string="Calorías Diarias Recomendadas", compute='_compute_calorias_diarias', store=True)

    @api.depends('cliente_id', 'peso', 'actividad_fisica')
    def _compute_calorias_diarias(self):
        for revision in self:
            if revision.cliente_id and revision.peso and revision.actividad_fisica:
                if revision.cliente_id.sexo == 'masculino':
                    bmr = 88.362 + (13.397 * revision.peso) + (4.799 * revision.cliente_id.altura) - (5.677 * revision.edad)
                else:
                    bmr = 447.593 + (9.247 * revision.peso) + (3.098 * revision.cliente_id.altura) - (4.330 * revision.edad)
                
                if revision.actividad_fisica == 'sedentario':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.2)
                elif revision.actividad_fisica == 'activo':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.725)
                elif revision.actividad_fisica == 'elite':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.9)  # Se ajusta el factor para la actividad 'elite'
                else:
                    revision.calorias_diarias_recomendadas = 0
            else:
                revision.calorias_diarias_recomendadas = 0

    @api.depends('peso', 'cliente_id.altura')
    def _compute_imc(self):
        for revision in self:
            if revision.peso and revision.cliente_id.altura:
                revision.imc = revision.peso / (revision.cliente_id.altura * revision.cliente_id.altura)
            else:
                revision.imc = 0.0

    @api.depends('cliente_id.fecha_nacimiento')
    def _compute_edad(self):
        for revision in self:
            if revision.cliente_id.fecha_nacimiento:
                born = revision.cliente_id.fecha_nacimiento
                today = fields.Date.today()
                revision.edad = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                revision.edad = 0


class Taller(models.Model):
    _name = 'nutrete.taller'
    _description = 'Taller de Nutrete'

    name = fields.Char(string="Nombre del Taller")
    fecha = fields.Date(string="Fecha")
    hora = fields.Float(default=16.00,string="Hora")
    nutricionista_id = fields.Many2one('res.partner', string="Nutricionista")
    dietista_id = fields.Many2one('res.partner', string="Dietista")
    cliente_ids = fields.Many2many('res.partner', string="Clientes")
    link = fields.Char(string="Enlace")

