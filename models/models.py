# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Cliente(models.Model):
    _name = 'nutrete.cliente'
    _description = 'Cliente de Nutrete'

    name = fields.Char(string="Nombre")
    dni = fields.Char(string="DNI")
    foto = fields.Binary(string="Foto")
    historial = fields.Text(string="Historial")
    motivo_consulta = fields.Text(string="Motivo de Consulta")


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

