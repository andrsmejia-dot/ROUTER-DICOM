# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 16:37:31 2020

@author: Carlos Jose Munoz
Asociación con Echo SCP
"""
import pydicom
from pynetdicom import AE, debug_logger #importa la clase 

debug_logger()
filename="1.3.6.1.4.1.5962.99.1.2786334768.1849416866.1385765836848.149.0.dcm"

dataset=pydicom.dcmread(filename)

ae = AE()#se cra una instancia AE
ae.add_requested_context('1.2.840.10008.5.1.4.1.1.2','1.2.840.10008.1.2.1')#almacenamiento con explicit little endian
#ae.add_requested_context('1.2.840.10008.1.1')#se crea una solicitud de asociación con un contexto de presentación
#assoc = ae.associate('localhost', 11112)#inicio de la negociación de asociación con la IP en el puerto dado
assoc = ae.associate('25.97.88.244', 11112)

if assoc.is_established:
    status=assoc.send_c_store(dataset)#almacenamiento de archivos 
    #status=assoc.send_c_echo()#solicitar el uso de su servicio de verificación
    print('conectado')
    assoc.release()
else:
     # Association rejected, aborted or never connected
     print('Failed to associate')