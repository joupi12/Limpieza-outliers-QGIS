from PyQt5.QtCore import QCoreApplication, QVariant
from PyQt5.QtWidgets import QMessageBox
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsExpression,
                       QgsFeatureRequest,
                       QgsProject,
                       QgsVectorLayer,
                       QgsProcessingParameterField)
from qgis.utils import iface
from statistics import *


class CleanMapAlgorithm(QgsProcessingAlgorithm):
    OUTPUT_BUFFER = 'OUTPUT_BUFFER'
    INPUT_VECTOR = 'INPUT_VECTOR'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CleanMapAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'CleanMap_1.1'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Limpieza de Mapas 1.1')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Cresud')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Cresud'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Plugin para Limpiar estadísticamente mapas de rendimiento (con columna Mapa_de_re). Solo limpia OutLiers")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_VECTOR, "ShapeFile"))
        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_BUFFER, "Salida"))

    def processAlgorithm(self, parameters, context, feedback):
        
        layer = self.parameterAsSource(
            parameters,
            self.INPUT_VECTOR,
            context
        )
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_BUFFER, 
            context,
            layer.fields(),
            layer.wkbType(),
            layer.sourceCrs()            
        )
        
        media_hum=mean([f["Humedad___"] for f in layer.getFeatures()])
        if media_hum>0:
            media_hum=mean([f["Humedad___"] for f in layer.getFeatures()])
            desv_hum=stdev([f["Humedad___"] for f in layer.getFeatures()])
            up_hum=media_hum+(desv_hum*3)
            down_hum=media_hum-(desv_hum*3)
            media_vel=mean([f["Velocidad_"] for f in layer.getFeatures()])
            desv_vel=stdev([f["Velocidad_"] for f in layer.getFeatures()])
            up_vel=media_vel+(desv_vel*3)
            down_vel=media_vel-(desv_vel*3)
            media=mean([f["Masa_de_re"] for f in layer.getFeatures()])
            desv=stdev([f["Masa_de_re"] for f in layer.getFeatures()])
            up=media+(desv*3)
            down=media-(desv*3)

            feats = [feat for feat in layer.getFeatures()]
            epsg=layer.sourceCrs().authid()
            temp="Point?crs=" + str(epsg) 
            mem_layer = QgsVectorLayer(temp,"duplicated_layer", "memory")
            mem_layer_data = mem_layer.dataProvider()
            attr = layer.fields().toList()
            mem_layer_data.addAttributes(attr)
            mem_layer.updateFields()
            mem_layer_data.addFeatures(feats)
            prov = mem_layer.dataProvider() 
            expr = QgsExpression( "\"Masa_de_re\">{} OR \"Masa_de_re\"<{}".format( up, down ) )
            expr_vel = QgsExpression( "\"Velocidad_\">{} OR \"Velocidad_\"<{}".format( up_vel, down_vel ) )
            expr_hum = QgsExpression( "\"Humedad__\">{} OR \"Humedad__\"<{}".format( up_vel, down_vel ) )
            it=mem_layer.getFeatures(QgsFeatureRequest(expr_vel))
            prov.deleteFeatures([i.id() for i in it]) 
            it=mem_layer.getFeatures(QgsFeatureRequest(expr_hum))
            prov.deleteFeatures([i.id() for i in it])            
            it=mem_layer.getFeatures(QgsFeatureRequest(expr))
            prov.deleteFeatures([i.id() for i in it]) 
            #QgsProject.instance().addMapLayer(mem_layer)
            for f in prov.getFeatures():
                sink.addFeature(f)
            results = {}
            results[self.OUTPUT_BUFFER] = sink
            return {self.OUTPUT_BUFFER:results}
        else:
            
            media_vel=mean([f["Velocidad_"] for f in layer.getFeatures()])
            desv_vel=stdev([f["Velocidad_"] for f in layer.getFeatures()])
            up_vel=media_vel+(desv_vel*3)
            down_vel=media_vel-(desv_vel*3)
            media=mean([f["Masa_de_re"] for f in layer.getFeatures()])
            desv=stdev([f["Masa_de_re"] for f in layer.getFeatures()])
            up=media+(desv*3)
            down=media-(desv*3)

            feats = [feat for feat in layer.getFeatures()]
            epsg=layer.sourceCrs().authid()
            temp="Point?crs=" + str(epsg) 
            mem_layer = QgsVectorLayer(temp,"duplicated_layer", "memory")
            mem_layer_data = mem_layer.dataProvider()
            attr = layer.fields().toList()
            mem_layer_data.addAttributes(attr)
            mem_layer.updateFields()
            mem_layer_data.addFeatures(feats)
            prov = mem_layer.dataProvider() 
            expr = QgsExpression( "\"Masa_de_re\">{} OR \"Masa_de_re\"<{}".format( up, down ) )
            expr_vel = QgsExpression( "\"Velocidad_\">{} OR \"Velocidad_\"<{}".format( up_vel, down_vel ) )
            it=mem_layer.getFeatures(QgsFeatureRequest(expr_vel))
            prov.deleteFeatures([i.id() for i in it]) 
            it=mem_layer.getFeatures(QgsFeatureRequest(expr))
            prov.deleteFeatures([i.id() for i in it]) 
            #QgsProject.instance().addMapLayer(mem_layer)
            for f in prov.getFeatures():
                sink.addFeature(f)
            results = {}
            results[self.OUTPUT_BUFFER] = sink
            return {self.OUTPUT_BUFFER:results}
