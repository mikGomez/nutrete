# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class Cliente(models.Model):
    _name = 'nutrete.cliente'
    _description = 'Cliente de Nutrete'

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI")
    foto = fields.Binary(string="Foto")
    historial = fields.Text(string="Historial")
    motivo_consulta = fields.Text(string="Motivo de Consulta")
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento")
    peso = fields.Float(string="Peso")
    altura = fields.Float(string="Altura")
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)

    @api.depends('peso', 'altura')
    def _compute_imc(self):
        for cliente in self:
            if cliente.peso and cliente.altura:
                cliente.imc = cliente.peso / (cliente.altura * cliente.altura)
            else:
                cliente.imc = 0.0

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        today = datetime.today()
        for cliente in self:
            if cliente.fecha_nacimiento:
                fecha_nacimiento_str = cliente.fecha_nacimiento.strftime("%Y-%m-%d")
                born = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d")
                cliente.edad = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                cliente.edad = 0

class Dietista(models.Model):
    _name = 'nutrete.dietista'
    _description = 'Dietista de Nutrete'

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI")
    foto = fields.Binary(string="Foto")
    especialidad = fields.Selection([('vegetariana', 'Dieta Vegetariana'),
                                     ('paleo', 'Dieta Paleo'),
                                     ('detox', 'Dieta Detox'),
                                     ('hipocalorica', 'Dieta Hipocalórica'),
                                     ('proteica', 'Dieta Proteica')],
                                    string="Especialidad")


class Nutricionista(models.Model):
    _name = 'nutrete.nutricionista'
    _description = 'Nutricionista de Nutrete'

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI")
    foto = fields.Binary(string="Foto")
    especialidad = fields.Selection([('deportiva', 'Nutrición Deportiva'),
                                     ('pediatrica', 'Nutrición Pediátrica'),
                                     ('clinica', 'Nutrición Clínica')],
                                    string="Especialidad")


class Dieta(models.Model):
    _name = 'nutrete.dieta'
    _description = 'Dieta de Nutrete'

    cliente_id = fields.Many2one('nutrete.cliente', string="Cliente")
    nutricionista_id = fields.Many2one('nutrete.nutricionista', string="Nutricionista")
    dietista_id = fields.Many2one('nutrete.dietista', string="Dietista")
    revision_ids = fields.One2many('nutrete.revision', 'dieta_id', string="Revisiones")

    @api.model
    def create(self, vals):
        if 'dietista_id' in vals:
            dietista = self.env['nutrete.dietista'].browse(vals['dietista_id'])
            if dietista:
                vals['nutricionista_id'] = dietista.nutricionista_id.id
        return super(Dieta, self).create(vals)


class Revision(models.Model):
    _name = 'nutrete.revision'
    _description = 'Revisión de Dieta'

    fecha = fields.Date(string="Fecha")
    hora = fields.Float(string="Hora")
    dieta_id = fields.Many2one('nutrete.dieta', string="Dieta")
    peso = fields.Float(string="Peso")
    comentarios = fields.Text(string="Comentarios")
    evolucion = fields.Selection([('excelente', 'Excelente'),
                                   ('buena', 'Buena'),
                                   ('regular', 'Regular'),
                                   ('mala', 'Mala')],
                                  string="Evolución")
    cliente_id = fields.Many2one('nutrete.cliente', related='dieta_id.cliente_id', store=True)
    imc = fields.Float(string="IMC", compute='_compute_imc', store=True)
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)

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
    cliente_ids = fields.Many2many('nutrete.cliente', string="Clientes")
    link = fields.Char(string="Enlace")

