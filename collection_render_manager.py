bl_info = {
    "name": "Collection Render Manager",
    "author": "Peter",
    "version": (0, 0, 1),
    "blender": (3, 60, 0),
    "location": "3D Viewport > Sidebar > Custom Tools",
    "description": "Collection render manager tool",
    "category": "Development"
}

import bpy

# -------------------------------------------------------------------
#   CRM PropertyGroups
# -------------------------------------------------------------------

class CRMCollectionItem(bpy.types.PropertyGroup):
    collectionName : bpy.props.StringProperty()
    
class CRMCollection(bpy.types.PropertyGroup):
    list : bpy.props.CollectionProperty(type=CRMCollectionItem)
    customName : bpy.props.StringProperty()
    active : bpy.props.BoolProperty()
    
# -------------------------------------------------------------------
#   CRM Operators
# -------------------------------------------------------------------

class CRM_OT_Select(bpy.types.Operator):
    """Select Collection Group"""
    bl_idname = "crm.select"
    bl_label = "CRM Select Group"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
    
        vl = bpy.context.scene.view_layers[0]
        for lc in vl.layer_collection.children:
            lc.exclude = True
            for item in bpy.context.scene.crm_list[self.CRMname].list:
                if item.collectionName == lc.name:
                    lc.exclude = False
                    
        return {"FINISHED"}
    
    
class CRM_OT_SetRender(bpy.types.Operator):
    """Set the render status of this collection group"""
    bl_idname = "crm.setrender"
    bl_label = "CRM Set Render Status"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
        
        bpy.context.scene.crm_list[self.CRMname].active = not bpy.context.scene.crm_list[self.CRMname].active
        return {"FINISHED"}
    
    
class CRM_OT_Delete(bpy.types.Operator):
    """Delete Collection Group"""
    bl_idname = "crm.delete"
    bl_label = "CRM Delete Group"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
        
        index =  bpy.context.scene.crm_list.find(self.CRMname)
        bpy.context.scene.crm_list.remove(index)
        return {"FINISHED"}
    
# -------------------------------------------------------------------
#   ADD
# -------------------------------------------------------------------
    

class CRM_OT_Add(bpy.types.Operator):
    """Add New Collection Group"""
    bl_idname = "crm.add"
    bl_label = "CRM Create Group"
    
    def execute(self, context):
        
        newCRMCollection = bpy.context.scene.crm_list.add()
        
        #index = bpy.types.Scene.CRMIndex
        index = context.scene.crm_index
        context.scene.crm_index += 1
        #while (bpy.context.scene.CRMList[index]):
            #index+=1
            
        #index = len(bpy.context.scene.CRMList)
        #bpy.context.scene.CRMList[-1]
        #if(len(bpy.context.scene.CRMList) > 0):
            #print( "last item", bpy.context.scene.CRMList[-1] )
            #index =  bpy.context.scene.CRMList.find( bpy.context.scene.CRMList[-1] ) + 2
            #index = len(bpy.context.scene.CRMList) + 1
            
        cname = "CRM" + str(index)
        newCRMCollection.name = cname
        newCRMCollection.customName = cname
        newCRMCollection.active = True
        
        vl = bpy.context.scene.view_layers[0]
        for lc in vl.layer_collection.children:
            if( lc.exclude == False ):
                newCRMItem = newCRMCollection.list.add()
                newCRMItem.name = "item_" + str(len(newCRMCollection.list))
                newCRMItem.collectionName = lc.name
                print("added", lc.name)
    
        return {"FINISHED"}
    
# -------------------------------------------------------------------
#   RENDER
# -------------------------------------------------------------------

class CRM_OT_Render(bpy.types.Operator):
    bl_idname = "crm.renderer"
    bl_label = "CRM Batch Renderer"
    
    def execute(self, context):
        
        fpo = bpy.context.scene.render.filepath
        fp = fpo + "\\" +bpy.context.scene.crm_base_name
        vl = bpy.context.scene.view_layers[0]
        cf = 1
        
        while cf <= bpy.context.scene.frame_end:
            #print("iterating", cf)
        
            bpy.context.scene.frame_set(cf)
        
            for CRMCollection in bpy.context.scene.crm_list:
                
                bpy.context.scene.render.filepath = fp+"_"+CRMCollection.customName+"_mat"+str(cf)
                
                for lc in vl.layer_collection.children:
                    lc.exclude = True
                    for item in CRMCollection.list:
                        if item.collectionName == lc.name:
                            lc.exclude = False
                
                if(CRMCollection.active):
                    bpy.ops.render.render(write_still=True)
                
            cf+=1
            
        bpy.context.scene.render.filepath = fpo
        
        return {"FINISHED"}
    
# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class VIEW3D_PT_CollectionRenderManager(bpy.types.Panel):
    bl_category = "Custom Tools"
    bl_label = "Collection Render Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout

        box = layout.column(align=True)
        box.label(text="AVAILABLE COLLECTIONS", icon="OUTLINER_COLLECTION")
        box.separator()
        boxframe = box.box()
        
        
        #Iterate Collections
        vl = bpy.context.scene.view_layers[0]
        for collection in vl.layer_collection.children:
            row = boxframe.row()
            row.prop(collection, "exclude", text="")
            #row.prop(collection, "name", text="")
            row.label(text="%s" % (collection.name))
        
        box.separator()
        
        row = box.row()
        row.operator("crm.add", text="ADD", icon="COLLECTION_NEW")
        
        box.separator()
        box.separator()
        box.separator()
        
        box.label(text="COLLECTION Groups", icon="OUTLINER_OB_GROUP_INSTANCE")
        box.separator()
        
        boxframe = box.box()
        
        #Iterate Collection Groups
        for crmItem in bpy.context.scene.crm_list:
            row = boxframe.row()
            
            current_selection = "HIDE_ON"
            matches = 0
            
            for lc in vl.layer_collection.children:
                hasMatch = False
                if(lc.exclude == False): #is visible
                    for item in crmItem.list:
                        if(lc.name == item.collectionName):
                            hasMatch = True
                else: #is not visible
                    hasMatch = True
                    for item in crmItem.list:
                        if(lc.name == item.collectionName):
                            hasMatch = False
                    
                if(hasMatch):
                    matches += 1
                        
            
                        
            if(matches == len(vl.layer_collection.children)):
                current_selection = "HIDE_OFF"
            
            op = row.operator("crm.select", text="", icon=current_selection)
            op.CRMname = crmItem.name
            
            row.prop(crmItem, "customName", text="")
            
            rendericon = "RESTRICT_RENDER_ON"
            if (crmItem.active):
                rendericon = "RESTRICT_RENDER_OFF"
            
            op = row.operator("crm.setrender", text="", icon=rendericon)
            op.CRMname = crmItem.name
            
            
            op = row.operator("crm.delete", text="", icon="TRASH")
            op.CRMname = crmItem.name
        
        box.separator()
        
        
        row = box.row()
        row.prop(bpy.context.scene, "crm_base_name", text="Base Name")
        
        row = box.row()
        row.prop(bpy.context.scene.render, "filepath", text="Destination")
        
        row = box.row()
        row.operator("crm.renderer", text="RENDER", icon="RESTRICT_RENDER_OFF")
                
# ------------------------------------------------------------------------
#     Registration
# ------------------------------------------------------------------------

classes = (
    CRMCollectionItem,
    CRMCollection,
    CRM_OT_Add,
    CRM_OT_SetRender,
    CRM_OT_Select,
    CRM_OT_Delete,
    CRM_OT_Render,
    VIEW3D_PT_CollectionRenderManager
)
           
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.Scene.crm_list = bpy.props.CollectionProperty(type=CRMCollection)
    bpy.types.Scene.crm_index = 1
    bpy.types.Scene.crm_base_name = "BASENAME"
    
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Scene.crm_list
    del bpy.types.Scene.crm_index
    del bpy.types.Scene.crm_base_name
    
if __name__ == "__main__":
    register()
    