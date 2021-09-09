## -*- coding: utf-8 -*-
#"""
#Created on Wed Sep 16 16:45:00 2020
#
#@author: Carlos Jose Munoz
#"""
#
#import os
#
#from pydicom.filewriter import write_file_meta_info
from pynetdicom import (
    AE, debug_logger, evt, AllStoragePresentationContexts, #evt contiene todos los eventos 
    ALL_TRANSFER_SYNTAXES
)
#
#debug_logger()
#
#def handle_store(event, storage_dir): #controlador para manejar eventos
    #"""Handle EVT_C_STORE events."""
    #try:
        #os.makedirs(storage_dir, exist_ok=True)
    #except:
        ## No se puede crear el directorio de salida, devuelve el estado de falla
        #return 0xC001
#    
    ## Confiamos en el UID de la solicitud C-STORE en lugar de decodificar
    #fname = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID)
    #with open(fname, 'wb') as f:
        ## escribe el encabezado, prefijo y metainformación del archivo
        #f.write(b'\x00' * 128)
        #f.write(b'DICM')
        #write_file_meta_info(f, event.file_meta)
        ## Escribe los datos codificados sin procesar
        #f.write(event.request.DataSet.getvalue())
#
    #return 0x0000
#
#handlers = [(evt.EVT_C_STORE, handle_store, ['out'])] #se pasa el evento al controlador
#
#ae = AE()
#storage_sop_classes = [
    #cx.abstract_syntax for cx in AllStoragePresentationContexts #contiene todos Los UID
#]
#for uid in storage_sop_classes:
    #ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES) # Agrerar todos los UID y sus syntaxis 
#    
#ae.start_server(('', 11112), block=True, evt_handlers=handlers)#genera la comunicación entre el IP y el puerto
from pynetdicom import AE

ae = AE()
ae.add_requested_context('1.2.840.10008.1.1')
assoc = ae.associate('localhost', 11112)
    if assoc.is_established:
        print('Association established with Echo SCP!')
        assoc.release()
else:
    # Association rejected, aborted or never connected
    print('Failed to associate')