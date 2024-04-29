from flask import Flask, request, render_template, flash
import xml.etree.ElementTree as ET
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        xml_file = request.files['xmlfile']
        if xml_file:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                namespaces = {
                    'cfdi': 'http://www.sat.gob.mx/cfd/3', 
                    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital', 
                    'nomina12': 'http://www.sat.gob.mx/nomina12'
                }
                folio = root.get('Folio')
                nomina = root.find('.//nomina12:Nomina', namespaces)
            except ET.ParseError:
                flash('Error en el formato del archivo XML.', 'error')
                return render_template('upload.html')

            database = os.path.join(os.getcwd(), 'nominas.db')
            conn = sqlite3.connect(database)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nomina_percepciones (
                    tipo_percepcion TEXT,
                    clave_concepto_percepcion TEXT,
                    importe_gravado TEXT,
                    importe_exento TEXT
                )''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nomina_deducciones (
                    tipo_deduccion TEXT,
                    clave_concepto_deduccion TEXT,
                    importe_deduccion TEXT
                )''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nomina (
                    folio TEXT PRIMARY KEY,
                    fecha_pago TEXT,
                    fecha_inicial_pago TEXT,
                    fecha_final_pago TEXT,
                    num_dias_pagados TEXT,
                    total_percepciones TEXT,
                    total_deducciones TEXT,
                    total_otros_pagos TEXT,
                    no_certificado TEXT,
                    receptor_rfc TEXT,
                    receptor_nombre TEXT,
                    version TEXT,
                    tipo_nomina TEXT,
                    tipo_percepcion TEXT,
                    clave_concepto_percepcion TEXT,
                    importe_gravado TEXT,
                    importe_exento TEXT,
                    tipo_deduccion TEXT,
                    clave_concepto_deduccion TEXT,
                    importe_deduccion TEXT,
                    subsidio_causado_importe TEXT
                )''')

            try:
                cursor.execute('''
                    INSERT INTO nomina (
                        folio, fecha_pago, fecha_inicial_pago, fecha_final_pago,
                        num_dias_pagados, total_percepciones, total_deducciones,
                        total_otros_pagos, no_certificado, receptor_rfc,
                        receptor_nombre, version, tipo_nomina, tipo_percepcion,
                        clave_concepto_percepcion, importe_gravado, importe_exento,
                        tipo_deduccion, clave_concepto_deduccion, importe_deduccion,
                        subsidio_causado_importe) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (folio, nomina.get('FechaPago'), nomina.get('FechaInicialPago'),
                     nomina.get('FechaFinalPago'), nomina.get('NumDiasPagados'),
                     nomina.get('TotalPercepciones'), nomina.get('TotalDeducciones'),
                     nomina.get('TotalOtrosPagos'), root.get('NoCertificado'),
                     root.find('.//cfdi:Receptor', namespaces).get('Rfc'), root.find('.//cfdi:Receptor', namespaces).get('Nombre'), root.get('Version'),
                     nomina.get('TipoNomina'), None, None, None,
                     None, None, None, None, None))
                conn.commit()
                flash('Archivo procesado correctamente', 'success')
            except sqlite3.IntegrityError:
                flash('No se puede cargar porque ya existe un registro con ese folio', 'error')

            conn.close()
        else:
            flash('No se subió ningún archivo', 'error')
    return render_template('upload.html')

@app.route('/tabla', methods=['GET'])
def mostrar_tabla():
    database = os.path.join(os.getcwd(), 'nominas.db')
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT folio, fecha_pago, fecha_inicial_pago, fecha_final_pago, num_dias_pagados,
               total_percepciones, total_deducciones, total_otros_pagos, no_certificado,
               receptor_rfc, receptor_nombre, version, tipo_nomina
        FROM nomina
    ''')
    nominas = cursor.fetchall()
    conn.close()
    return render_template('tabla.html', nominas=nominas)


if __name__ == '__main__':
    app.run(debug=False)
