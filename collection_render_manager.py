bl_info = {
    "name": "Collection Render Manager",
    "author": "Peter",
    "version": (1, 0, 4),
    "blender": (3, 60, 0),
    "location": "3D Viewport > Sidebar > Custom Tools",
    "description": "Collection render manager tool",
    "category": "Development"
}

import bpy
import itertools

# -------------------------------------------------------------------
#   CRM POPUP
# -------------------------------------------------------------------

class CRMPopupOperator(bpy.types.Operator):
    bl_idname = "crm.popup_operator"
    bl_label = "COLLECTION RENDER MANAGER"
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=1000)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        box = layout.column(align=True)
        
        box.separator(factor=5.0)
        
        box.label(text="AVAILABLE COLLECTIONS", icon="OUTLINER_COLLECTION")
        box.separator()
        boxframe = box.box()
        
        
        #Iterate Collections
        vl = bpy.context.scene.view_layers[0]
        for collection in vl.layer_collection.children:
            row = boxframe.row()
            #row.prop(collection, "exclude", text="")
            row.prop(collection, "hide_viewport", text="")
            #row.prop(collection, "name", text="")
            row.label(text="%s" % (collection.name))
        
        row = box.row()
        row.operator("crm.add", text="NEW COLLECTION GROUP", icon="COLLECTION_NEW")
        
        box.separator(factor=5.0)
        
        #Iterate Collection Groups
        
        box.label(text="COLLECTION Groups", icon="OUTLINER_OB_GROUP_INSTANCE")
        box.separator()
        
        boxframe = box.box()
        
        for crmItem in bpy.context.scene.crm_list:
            row = boxframe.row()
            
            current_selection = "HIDE_ON"
            matches = 0
            
            for lc in vl.layer_collection.children:
                hasMatch = False
                if(lc.hide_viewport == False): #is visible
                    for item in crmItem.list:
                        if(lc.name == item.collectionName):
                            #print("found: " + item.collectionName)
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
            
            #if (crmItem.isRendering):
            #    row.prop(crmItem, "isRendering", text="", icon="BLENDER")
            
            rendericon = "RESTRICT_RENDER_ON"
            if (crmItem.active):
                rendericon = "RESTRICT_RENDER_OFF"
            
            op = row.operator("crm.setrender", text="", icon=rendericon)
            op.CRMname = crmItem.name
            
            
            op = row.operator("crm.delete", text="", icon="TRASH")
            op.CRMname = crmItem.name
        
        box.separator(factor=5.0)
        
        #Iterate Material associations
        
        box.label(text="MATERIAL Associations", icon="MATERIAL")
        box.separator()
        
        #if len(bpy.context.scene.crm_mag_list)>0:
        for MAGidx, MAG in enumerate(bpy.context.scene.crm_mag_list):
            #print("MAGLIST", MAGidx, MAG)
            boxframe = box.box()
            #MAG header
            row = boxframe.row()
            row.label(text="MATERIAL Association Group #%s" % (MAGidx + 1))
            op = row.operator("crm.deletemag", text ="", icon="TRASH")
            #print("MAGItem", MAGidx, MAG.name)
            op.MAGidx = MAGidx
            op.MAGName = MAG.name
            
            MAGrow = boxframe.row()
            
            for MAidx, MA in enumerate(MAG.list):
                
                MAcol = MAGrow.box()
                crow = MAcol.row()
                isLast = False 
                if (MAidx + 1) == len(MAG.list):
                    isLast = True
                
                crow.label(text="MATERIAL Association #%s" % (MAidx + 1))
                op = crow.operator("crm.deletema", text="", icon="TRASH")
                #op.MAid = assoc.name
                op.MAGidx = MAGidx
                op.MAidx = MAidx
                
                crow = MAcol.row()
                crow.prop_search(MA, "materialName", bpy.data, "materials", text="")
                
            
                for MAItemidx, MAItem in enumerate(MA.list):
                    crow = MAcol.row()
                    crow.label(icon="ARROW_LEFTRIGHT", text="")
                    crow.prop_search(MAItem, "materialName", bpy.data, "materials", text="")
                    if isLast:
                        op = crow.operator("crm.deletemaitem", text="", icon="TRASH")
                        #op.MAid = assoc.name
                        #op.MAItemid = item.name
                        op.MAGidx = MAGidx
                        op.MAidx = MAidx
                        op.MAItemidx = MAItemidx
                        
                if isLast:
                    crow = MAcol.row()
                    crow.label(text=" ")
                    op = crow.operator("crm.addmaitem", text="", icon="ADD")
                    #op.MAid = assoc.name
                    op.MAGidx = MAGidx
                    op.MAidx = MAidx
                    
                    
            #col = split.column()
            op = MAGrow.operator("crm.addma", text="", icon="ADD")
            op.MAGidx = MAGidx
        
        #if len(bpy.context.scene.crm_ma_list)<1:
            #row = box.row()
            #op = row.operator("crm.addma", text="ADD ASSOCIATION ", icon="ADD")
            #op.MAGidx = MAGidx
            
            #row = boxframe.row()
            
            
        row = box.row()
        row.operator("crm.addmag", text="ADD ASSOCIATION GROUP", icon="ADD")
        
        box.separator(factor=5.0)
        
        #Cameras
        
        box.label(text="CAMERAS", icon="OUTLINER_OB_CAMERA")
        box.separator()
        boxframe = box.box()
        
        for obj in bpy.context.scene.objects:
            if obj.type == "CAMERA":
                row = boxframe.row()
                row.prop(obj, "hide_viewport", text="", icon="NONE")
                row.label(text="%s" % (obj.name))
            
        box.separator(factor=5.0)
        
        #Settings
        
        row = box.row()
        row.prop(bpy.context.scene.crm_settings, "basename", text="Base Name")
        
        row = box.row()
        row.prop(bpy.context.scene.render, "filepath", text="Destination")
        
        #row = box.row()
        #row.prop(bpy.context.scene.crm_settings, "render_timeline", text="Render All Keyframes")
        
        box.separator(factor=3.0)
        
        row = box.row()
        row.operator("crm.renderer", text="RENDER", icon="RESTRICT_RENDER_OFF")

        box.separator(factor=3.0)
        return

# -------------------------------------------------------------------
#   CRM PropertyGroups
# -------------------------------------------------------------------

class CRMSettings(bpy.types.PropertyGroup):
    basename : bpy.props.StringProperty(
        default = "BASENAME"
    )
    render_timeline : bpy.props.BoolProperty(
        default = True
    )

class CRMCollectionItem(bpy.types.PropertyGroup):
    collectionName : bpy.props.StringProperty()
    
class CRMCollection(bpy.types.PropertyGroup):
    list : bpy.props.CollectionProperty(type=CRMCollectionItem)
    customName : bpy.props.StringProperty()
    active : bpy.props.BoolProperty()
    isRendering : bpy.props.BoolProperty()
    
class CRMMaterialItem(bpy.types.PropertyGroup):
    materialName : bpy.props.StringProperty()
    
class CRMMaterial(bpy.types.PropertyGroup):
    list : bpy.props.CollectionProperty(type=CRMMaterialItem)
    materialName : bpy.props.StringProperty()
    index : bpy.props.IntProperty(
        default = 1
    )
    #active : bpy.props.BoolProperty()
    #isRendering : bpy.props.BoolProperty()
    
class CRMMaterialGroup(bpy.types.PropertyGroup):
    list : bpy.props.CollectionProperty(type=CRMMaterial)
    index : bpy.props.IntProperty(
        default = 1
    )
    
class CRMCameras(bpy.types.PropertyGroup):
    camera : bpy.props.StringProperty()
    active : bpy.props.BoolProperty(
        default = True
    )
    #active : bpy.props.BoolProperty()
    #isRendering : bpy.props.BoolProperty()
    
# -------------------------------------------------------------------
#   CRM Collection Operators
# -------------------------------------------------------------------

class CRM_OT_Select(bpy.types.Operator):
    """Select Collection Group"""
    bl_idname = "crm.select"
    bl_label = "CRM Select Group"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
        
        #print("collections >>");
    
        vl = bpy.context.scene.view_layers[0]
        for lc in vl.layer_collection.children:
            #print("collection " + lc.name);
            lc.hide_viewport = True
            for item in bpy.context.scene.crm_list[self.CRMname].list:
                if item.collectionName == lc.name:
                    lc.hide_viewport = False
                    
        return {"FINISHED"}
    
    
class CRM_OT_SetRender(bpy.types.Operator):
    """Set the render status of this collection group"""
    bl_idname = "crm.setrender"
    bl_label = "CRM Set Render Status"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
        
        bpy.context.scene.crm_list[self.CRMname].active = not bpy.context.scene.crm_list[self.CRMname].active
        return {"FINISHED"}

class CRM_OT_Add(bpy.types.Operator):
    """Add New Collection Group"""
    bl_idname = "crm.add"
    bl_label = "CRM Create Group"
    
    def execute(self, context):
        
        newCRMCollection = bpy.context.scene.crm_list.add()
        
        index = context.scene.crm_index
        context.scene.crm_index += 1
            
        cname = "CRM" + str(index)
        newCRMCollection.name = cname
        newCRMCollection.customName = cname
        newCRMCollection.active = True
        
        vl = bpy.context.scene.view_layers[0]
        for lc in vl.layer_collection.children:
            if( lc.hide_viewport == False ):
                newCRMItem = newCRMCollection.list.add()
                newCRMItem.name = "item_" + str(len(newCRMCollection.list))
                newCRMItem.collectionName = lc.name
                print("added", lc.name, lc.hide_viewport)
    
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
#   CRM CAMERA Operators
# -------------------------------------------------------------------

class CRM_OT_SetCamera(bpy.types.Operator):
    """Set the render status of this collection group"""
    bl_idname = "crm.setcamera"
    bl_label = "CRM Set Camera Status"
    
    CRMname : bpy.props.StringProperty()
    
    def execute(self, context):
        
        bpy.context.scene.crm_list[self.CRMname].active = not bpy.context.scene.crm_list[self.CRMname].active
    
# -------------------------------------------------------------------
#   CRM Material Operators
# -------------------------------------------------------------------
    
class CRM_OT_AddMAG(bpy.types.Operator):
    """Add New Material Association Group"""
    bl_idname = "crm.addmag"
    bl_label = "CRM Create Material Association Group"
    
    def execute(self, context):
        
        newAssoc = bpy.context.scene.crm_mag_list.add()
        index = context.scene.crm_mag_index
        context.scene.crm_mag_index += 1
        
        cname = "MAG" + str(index)
        newAssoc.name = cname
        
        MAGidx = bpy.context.scene.crm_mag_list.find(cname)
        bpy.ops.crm.addma(MAGidx = MAGidx)
        return {"FINISHED"}
    
class CRM_OT_DeleteMAG(bpy.types.Operator):
    """Delete Material Association Group"""
    bl_idname = "crm.deletemag"
    bl_label = "CRM Delete Material Association Group"
    
    MAGName : bpy.props.StringProperty()
    MAGidx : bpy.props.IntProperty()
    
    def execute(self, context):
        
        bpy.context.scene.crm_mag_list.remove(self.MAGidx)
        return {"FINISHED"}
    

class CRM_OT_AddMA(bpy.types.Operator):
    """Add New Material Association"""
    bl_idname = "crm.addma"
    bl_label = "CRM ADD Material Association"
    
    MAGidx : bpy.props.IntProperty()
    
    def execute(self, context):
        
        print("MAGidx", self.MAGidx)
        print("MAG", bpy.context.scene.crm_mag_list)
        
        MAG = bpy.context.scene.crm_mag_list[self.MAGidx]
        
        newAssoc = MAG.list.add()
        index = MAG.index
        MAG.index += 1
        
        cname = "MA" + str(index)
        newAssoc.name = cname
        
        #copy
        if len(MAG.list) > 1:
            MA = MAG.list[0]
            newAssoc.index = MA.index
            for MAItem in MA.list:
                newAssocItem = newAssoc.list.add()
                newAssocItem.name = MAItem.name
        
        #new        
        else:
            newAssocItem = newAssoc.list.add()
            newAssocItem.name = "item_" + str(newAssoc.index)
            newAssoc.index += 1
        
        return {"FINISHED"}
    
class CRM_OT_DeleteMA(bpy.types.Operator):
    """Delete Material Association"""
    bl_idname = "crm.deletema"
    bl_label = "CRM Delete Material Association"
    
    MAidx : bpy.props.IntProperty()
    MAGidx : bpy.props.IntProperty()
    
    def execute(self, context):
        
        bpy.context.scene.crm_mag_list[self.MAGidx].list.remove(self.MAidx)
        return {"FINISHED"}
    
class CRM_OT_AddMAItem(bpy.types.Operator):
    """Add New Material Association Items to this row"""
    bl_idname = "crm.addmaitem"
    bl_label = "CRM ADD Material Association Item"
    
    MAidx : bpy.props.IntProperty()
    MAGidx : bpy.props.IntProperty()
    
    def execute(self, context):
        
        for MA in bpy.context.scene.crm_mag_list[self.MAGidx].list:
            MAItem = MA.list.add()
            MAItem.name = "item_" + str(MA.index)
            MA.index += 1
        
        return {"FINISHED"}
    
class CRM_OT_DeleteMAItem(bpy.types.Operator):
    """Delete Material Association Items in this row"""
    bl_idname = "crm.deletemaitem"
    bl_label = "CRM Delete Material Association Item"
    
    MAItemidx : bpy.props.IntProperty()
    MAidx : bpy.props.IntProperty()
    MAGidx : bpy.props.IntProperty()
    
    
    def execute(self, context):
        
        for MA in bpy.context.scene.crm_mag_list[self.MAGidx].list:
            MA.list.remove(self.MAItemidx)
        
        return {"FINISHED"}

# -------------------------------------------------------------------
#   RENDER
# -------------------------------------------------------------------

class CRM_OT_Render(bpy.types.Operator):
    bl_idname = "crm.renderer"
    bl_label = "CRM Render setup"
    
    def execute(self, context):
        
        fpo = bpy.context.scene.render.filepath
        fp = fpo + "\\" +bpy.context.scene.crm_settings.basename
        obj_list = []
        
        for MAGidx, MAG in enumerate(bpy.context.scene.crm_mag_list):
            
            for MAidx, MA in enumerate(MAG.list):
                print('processing', MA.materialName)
                
                obj_list_ma = [MAGidx, MAidx, MA.materialName]
                obj_list_item = []
                
                for obj in bpy.context.scene.objects:
                    if hasattr(obj.data,'materials') and MA.materialName in obj.data.materials:
                        m_index = obj.data.materials.find(MA.materialName)
                        obj_item = [obj.name, m_index]
                        obj_list_item.append(obj_item)
                        
                obj_list_ma.append(obj_list_item)
                obj_list.append(obj_list_ma)
            
        print("objlist", obj_list)
        
        #iterate material associations
        if len(bpy.context.scene.crm_mag_list)>0:
            
            CRMcombinations = []
            for MAGidx, MAG in enumerate(bpy.context.scene.crm_mag_list):
                
                CRMGroup = []
                for idx, item in enumerate(MAG.list[0].list):
                    
                    CRMBatch = []
                    for MAidx, MA in enumerate(MAG.list):
                        
                        CRMitem = [MAGidx, MAidx, idx]
                        CRMBatch.append(CRMitem)
                        
                    CRMGroup.append(CRMBatch)
                    
                CRMcombinations.append(CRMGroup)
                    
            #solve the permutations using product of the pointer to the combinations options
            prod = list(itertools.product(*CRMcombinations))
            
            for solution in prod:
                
                print ('solving', solution)
                
                MASuffix = ""
                for grp in solution:
                    for idx, block in enumerate(grp):
                        print('block', block)
                        
                        for obj_grp in obj_list:
                            if obj_grp[0] == block[0] and obj_grp[1] == block[1]:
                                
                                MARefItem = bpy.context.scene.crm_mag_list[block[0]].list[block[1]].list[block[2]]
                                MAMaterial = bpy.data.materials.get(MARefItem.materialName)
                                MASuffix += "_"+MARefItem.materialName
                                
                                for obj_item in obj_grp[3]:
                                    obj = bpy.context.scene.objects[obj_item[0]]
                                    obj.data.materials[obj_item[1]] = MAMaterial
                
                #iterate collections groups
                bpy.ops.crm.render_collection(path = fp, suffix = MASuffix)
                             
        else:
            
            #iterate collections groups
            bpy.ops.crm.render_collection(path = fp, suffix = "")
                    
        #Reset values
        bpy.context.scene.render.filepath = fpo
        
        #Reset materials
        for obj_grp in obj_list:
            
            Material = bpy.data.materials.get(obj_grp[2])
            for obj_item in obj_grp[3]:
                obj = bpy.context.scene.objects[obj_item[0]]
                obj.data.materials[obj_item[1]] = Material
        
        return {"FINISHED"}
    
class CRM_OT_RenderCollection(bpy.types.Operator):
    bl_idname = "crm.render_collection"
    bl_label = "CRM Batch Renderer"
    
    path : bpy.props.StringProperty()
    suffix : bpy.props.StringProperty()
    
    def execute(self, context):
        
        vl = bpy.context.scene.view_layers[0]
        
        for CRMCollection in bpy.context.scene.crm_list:
                    
            bpy.context.scene.render.filepath = self.path+"_"+CRMCollection.customName
            bpy.context.scene.render.filepath += self.suffix
            
            for lc in vl.layer_collection.children:
                lc.hide_viewport = True
                for item in CRMCollection.list:
                    if item.collectionName == lc.name:
                        lc.hide_viewport = False
            
            
            if(CRMCollection.active):
                bpy.ops.render.render(write_still=True)
        
        return {"FINISHED"}
        
                
# ------------------------------------------------------------------------
#     Registration
# ------------------------------------------------------------------------

classes = (
    CRMSettings,
    CRMCollectionItem,
    CRMCollection,
    CRMMaterialItem,
    CRMMaterial,
    CRMMaterialGroup,
    CRMCameras,
    CRM_OT_Add,
    CRM_OT_SetRender,
    CRM_OT_Select,
    CRM_OT_Delete,
    CRM_OT_Render,
    CRM_OT_RenderCollection,
    CRM_OT_AddMAG,
    CRM_OT_DeleteMAG,
    CRM_OT_AddMA,
    CRM_OT_DeleteMA,
    CRM_OT_AddMAItem,
    CRM_OT_DeleteMAItem,
    CRM_OT_SetCamera,
    CRMPopupOperator
    #VIEW3D_PT_CollectionRenderManager
)

addon_keymaps = []
           
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.Scene.crm_list = bpy.props.CollectionProperty(type=CRMCollection)
    bpy.types.Scene.crm_index = bpy.props.IntProperty(default = 1)
    
    #bpy.types.Scene.crm_ma_list = bpy.props.CollectionProperty(type=CRMMaterial)
    #bpy.types.Scene.crm_ma_index = bpy.props.IntProperty(default = 1)
    
    bpy.types.Scene.crm_mag_list = bpy.props.CollectionProperty(type=CRMMaterialGroup)
    bpy.types.Scene.crm_mag_index = bpy.props.IntProperty(default = 1)
    
    bpy.types.Scene.crm_settings = bpy.props.PointerProperty(type=CRMSettings)
    
     # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(CRMPopupOperator.bl_idname, type='M', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))
    
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Scene.crm_list
    del bpy.types.Scene.crm_index
    
    #del bpy.types.Scene.crm_ma_list
    #del bpy.types.Scene.crm_ma_index
    
    del bpy.types.Scene.crm_mag_list
    del bpy.types.Scene.crm_mag_index
    
    del bpy.types.Scene.crm_settings
    
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()
    
