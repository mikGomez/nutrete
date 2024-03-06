# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import datetime
import logging
import re

class Cliente(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    is_cliente = fields.Boolean()

    dni = fields.Char(string="DNI")
    historial = fields.Text(string="Historial")
    motivo_consulta = fields.Text(string="Motivo de Consulta")
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento")
    peso = fields.Float(string="Peso")
    altura = fields.Float(string="Altura")
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)
    sexo = fields.Selection([
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro')
    ], string="Sexo")
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
            if alt.altura > 0:
                logging.Logger.info('Altura correctamente')
            else:
                raise ValidationError('Formato altura incorrecto')
            
    _sql_constraints = [('dni_unique', 'unique(dni)', 'DNI ya existente.')]
    @api.onchange('is_cliente')
    def _onchange_is_dev(self):
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
        today = datetime.datetime.today()
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
    dni = fields.Char(string="DNI")
    especialidad = fields.Selection([('vegetariana', 'Dieta Vegetariana'),
                                     ('paleo', 'Dieta Paleo'),
                                     ('detox', 'Dieta Detox'),
                                     ('hipocalorica', 'Dieta Hipocalórica'),
                                     ('proteica', 'Dieta Proteica')],
                                    string="Especialidad")
    @api.onchange('is_dietista')
    def _onchange_is_dev(self):
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

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI")
    especialidad = fields.Selection([('deportiva', 'Nutrición Deportiva'),
                                     ('pediatrica', 'Nutrición Pediátrica'),
                                     ('clinica', 'Nutrición Clínica')],
                                    string="Especialidad")
    @api.onchange('is_nutricionista')
    def _onchange_is_dev(self):
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
    nutricionista_id = fields.Many2one('nutrete.nutricionista', string="Nutricionista")
    dietista_id = fields.Many2one('nutrete.dietista', string="Dietista")
    revision_ids = fields.One2many('nutrete.revision', 'dieta_id', string="Revisiones")


class Revision(models.Model):
    _name = 'nutrete.revision'
    _description = 'Revisión de Dieta'

    fecha = fields.Date(string="Fecha")
    hora = fields.Float(string="Hora")
    dieta_id = fields.Many2one('nutrete.dieta', string="Dieta")
    peso = fields.Float(string="Peso")
    comentarios = fields.Text(string="Comentarios")
    actividad_fisica = fields.Selection([('sedentario', 'Sedentario'),
                                        ('ligero', 'Ligero'),
                                        ('moderado', 'Moderado'),
                                        ('activo', 'Activo')],
                                        string="Actividad Física")
    evolucion = fields.Selection([('excelente', 'Excelente'),
                                   ('buena', 'Buena'),
                                   ('regular', 'Regular'),
                                   ('mala', 'Mala')],
                                  string="Evolución")
    cliente_id = fields.Many2one('res.partner', related='dieta_id.cliente_id', store=True)
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)
    calorias_diarias_recomendadas = fields.Integer(string="Calorías Diarias Recomendadas", compute='_compute_calorias_diarias', store=True)

    @api.depends('cliente_id', 'peso', 'actividad_fisica')
    def _compute_calorias_diarias(self):
        for revision in self:
            if revision.cliente_id and revision.peso and revision.actividad_fisica:
                # Cálculo de calorías
                if revision.cliente_id.sexo == 'masculino':
                    bmr = 88.362 + (13.397 * revision.peso) + (4.799 * revision.cliente_id.altura) - (5.677 * revision.edad)
                else:
                    bmr = 447.593 + (9.247 * revision.peso) + (3.098 * revision.cliente_id.altura) - (4.330 * revision.edad)
                
                if revision.actividad_fisica == 'sedentario':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.2)
                elif revision.actividad_fisica == 'ligero':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.375)
                elif revision.actividad_fisica == 'moderado':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.55)
                elif revision.actividad_fisica == 'activo':
                    revision.calorias_diarias_recomendadas = int(bmr * 1.725)
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
    hora = fields.Float(string="Hora")
    nutricionista_id = fields.Many2one('nutrete.nutricionista', string="Nutricionista")
    dietista_id = fields.Many2one('nutrete.dietista', string="Dietista")
    cliente_ids = fields.Many2many('res.partner', string="Clientes")
    link = fields.Char(string="Enlace")

