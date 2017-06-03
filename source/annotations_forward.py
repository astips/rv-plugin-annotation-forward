# -*- coding: utf-8 -*-

###########################################################################################
#
# Author: astips (animator.well)
#
# Date: 2016.06
#
# Url: https://github.com/astips
#
# Description: RV Plugin - Copy annotations forward
#     
###########################################################################################
from rv import commands, rvtypes
from rv.commands import NeutralMenuState
import re
import rv


class CopyAnnotations(rvtypes.MinorMode):

    def __init__(self):
        rvtypes.MinorMode.__init__(self)

        menu = [("Annotation", [("Copy Annotations Forward", self.copyForward, "E", lambda: NeutralMenuState),])]
        key = [("key-down--E", self.copyForward, "Copy Annotations to immediate next frame"),]

        self.init("CopyAnnotations", key, None, menu)


    def copyProperty(self, sourcePropertyInfo, targetName):
        typeToGetter = {
            rv.commands.ByteType : rv.commands.getByteProperty,
            rv.commands.FloatType : rv.commands.getFloatProperty,
            rv.commands.HalfType : rv.commands.getHalfProperty,
            rv.commands.IntType : rv.commands.getIntProperty,
            rv.commands.ShortType : rv.commands.getIntProperty,
            rv.commands.StringType : rv.commands.getStringProperty
        }

        typeToSetter = {
            rv.commands.ByteType : rv.commands.setByteProperty,
            rv.commands.FloatType : rv.commands.setFloatProperty,
            rv.commands.HalfType : rv.commands.setHalfProperty,
            rv.commands.IntType : rv.commands.setIntProperty,
            rv.commands.ShortType : rv.commands.setIntProperty,
            rv.commands.StringType : rv.commands.setStringProperty
        }

        dataType = sourcePropertyInfo['type']
        rv.commands.newProperty(targetName, sourcePropertyInfo['type'], sourcePropertyInfo['dimensions'][0])

        typeToSetter[dataType](targetName, typeToGetter[dataType](sourcePropertyInfo['name']), True)

    def copyForward(self, event):
        paintNodesMeta = [p for p in rv.commands.metaEvaluate(rv.commands.frame(), rv.commands.viewNode()) if p['nodeType'] == 'RVPaint']
        for paintNodeMeta in paintNodesMeta:
            self.copyPaintNodeForward(paintNodeMeta['node'], paintNodeMeta['frame'])
        
    def copyPaintNodeForward(self, paintNode, sourceFrame):
        # For this example I am copying the annotations to the next frame, but you can come
        # up with whatever logic here that you would like.
        targetFrames = [sourceFrame+1]
        
        orderProperty = "%s.frame:%d.order" % (paintNode, sourceFrame)
        if not rv.commands.propertyExists(orderProperty):
            # If we don't have an annotation for the current frame, skip this paint node.
            return
            
        if rv.commands.getStringProperty(orderProperty):
            # We know we potentially have annotations on this frame at this point, get them.
            strokeNamesOnThisFrame = rv.commands.getStringProperty(orderProperty)
            allPaintNodeProperties = rv.commands.properties(paintNode)

            strokeInfos = []
            for strokeName in strokeNamesOnThisFrame:
                fullStrokeBaseName = "%s.%s." % (paintNode, strokeName)
                strokeComponents = []
                for paintProp in allPaintNodeProperties:
                    if str(paintProp).startswith(fullStrokeBaseName):
                        strokeComponents.append(rv.commands.propertyInfo(paintProp))
                strokeInfos.append(strokeComponents)
            
            # At this point we have extracted the metadata of each stroke (but not data).
            # We can now start constructing our strokes on target frame(s).
            for targetFrame in targetFrames:
                targetOrderProperty = "%s.frame:%d.order" % (paintNode, targetFrame)

                # If we don't have any annotations on this frame yet, the order property won't exist, so create it.
                if not rv.commands.propertyExists(targetOrderProperty):
                    rv.commands.newProperty(targetOrderProperty, rv.commands.StringType, 1)
                nextIdProperty = "%s.paint.nextId" % (paintNode)
                nextId = rv.commands.getIntProperty(nextIdProperty)[0]
                for strokeInfo in strokeInfos:
                    nextId += 1
                    
                    # Each stroke we need to update the 'order' property for the frame.
                    fim = re.match( r'(?P<paint>[^\.]+)\.(?P<tool>[^:]+):(?P<strokeId>[\d]+):(?P<frame>[\d]+):(?P<user>[^\.]+)\.(?P<component>.*)$', strokeInfo[0]['name'])
                    orderStrokeName = "%s:%s:%s:%s" % (fim.group('tool'), fim.group('strokeId'), fim.group('frame'), fim.group('user'))
                    rv.extra_commands.appendToProp(targetOrderProperty, orderStrokeName)
                    
                    for strokeComponent in strokeInfo:
                        m = re.match( r'(?P<paint>[^\.]+)\.(?P<tool>[^:]+):(?P<strokeId>[\d]+):(?P<frame>[\d]+):(?P<user>[^\.]+)\.(?P<component>.*)$', strokeComponent['name'])
                        if not m:
                            raise Exception("Problem encountered parsing stroke: %s" % (strokeInfo.get("name", strokeInfo)))

                        newPropertyName = "%s.%s:%s:%s:%s.%s" % (m.group('paint'), m.group('tool'), str(nextId), targetFrame, m.group('user'), m.group('component'))
                        self.copyProperty(strokeComponent, newPropertyName)

                    # We update this property slightly more often then necessary so that if one of them fails for an unknown reason
                    # the nextId is still accurate.
                    rv.commands.setIntProperty(nextIdProperty, [nextId])


def createMode():
    return CopyAnnotations()
