bl_info={
    "author": "STEAM LAB CENTRO, Diego Trujillo Pisanty",
    "blender":(2,80,0),
    "description":"Export RAPID scripts for ABB robots",
    "name":"ABBlender",
    "support":"COMMUNITY",
    "version":(0,2),
    "wiki_url":"https://github.com/dtpisanty/abblender"    
}


import bpy
from math import degrees
#-----------------------------
#SCENE PROPERTIES
#-----------------------------
class AbblenderProperties(bpy.types.PropertyGroup):
    path:bpy.props.StringProperty(name="Export path",description="Path to save MOD file",default="",subtype="DIR_PATH")
    module_name:bpy.props.StringProperty(name="Filename",description="Output file will be filename.MOD",default="animation")
    speed:bpy.props.IntProperty(name="Speed",default=1000,min=10,max=7000,description="Tool Center point speed mm/s")
    step:bpy.props.IntProperty(name="Step",description="A new position is exported every step frames",default=10,min=1)
    tool_name:bpy.props.StringProperty(name="Tool name",description="Name of tool used",default="tool0")
    outputState:bpy.props.BoolProperty(name="Pulse signal",description="Generates 15ms pulse on output signal")
    signalName:bpy.props.StringProperty(name="Signal name",description="Name of IO signal used",default="")
    IK:bpy.props.BoolProperty(name="Inverse Kinematic",description="Bake IK before exporting")
    reportFrame:bpy.props.BoolProperty(name="Report Frame",description="Send current step over TCP")
    host:bpy.props.StringProperty(name="Host",description="IP to report step",default="127.0.0.1")
    port:bpy.props.IntProperty(name="Port",description="Receiving TCP port number",default=10000,min=0,max=65535)

class ExportJointTarget(bpy.types.Operator):
    '''
    Export ABB RAPID .mod file describing robot movement as jointtargets
    '''
    bl_idname="abblender.joint_target"
    bl_label="Export Joint Targets"
    bl_options={"REGISTER","UNDO"}
    
    #Fields
    
    fps=24
    frameStart=1
    frameEnd=255
    startpos="";
    endpos="";
    defTargets=""
    ioStates=""
    endState=0
    tab="    "
    hasIKmod=False
    def toJointtarget(self,bones,axis='y'):
        '''
        Converts bones rotation to Rapid jointtarget array
        Takes:
            bones->[pose.bones](list)
            axis->"x","y" or "z"
        Returns
            String
        '''
        out="[["
        for bone in bones:
            if(axis=="x"):
                if (bone.name=="Axis6_IK"):
                    pass
                elif(bone.name!="Axis6"):
                    out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().x))
                else :
                    out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().x))
            elif(axis=="y"):
                if (bone.name=="Axis6_IK"):
                    pass
                elif(bone.name!="Axis6"):
                    out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().y))
                else:
                    out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().y))
            elif(axis=="z"):
                if (bone.name=="Axis6_IK"):
                    pass
                elif(bone.name!="Axis6"):
                    out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().z))
                else:
                    out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().z))
            else:
                return
        return out

    def save(self,context,moduleName="Animation"):
        '''
        Compiles the Rapid code and saves it to
        <moduleName>.mod
        Takes:
            moduleName -> String
        Returns:
            None
        '''
        abbr_props=context.scene.abbrProps
        time="\\T:={:.3f}".format(0)
        toolName=abbr_props.tool_name
        if abbr_props.step>1:
            frames=self.frameEnd-self.frameStart
            seconds=(frames)/self.fps
            duration=abbr_props.step*(seconds/frames)
            time="\\T:={:.3f}".format(duration)
        lines=[]
        lines.append("Module "+moduleName+"\n")
        lines.append("\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+"VAR SocketDev socket0;\n")
            lines.append(self.tab+"CONST num stride:="+str(abbr_props.step)+";\n")
        # lines.append(self.tab+"PERS tooldata noTool := [ TRUE, [ [0, 0, 0], [1, 0,   0 ,0] ], [0.001, [0, 0, 0.001], [1, 0, 0, 0], 0, 0, 0] ];")
        # lines.append("\n")
        lines.append(self.tab+self.startpos+";\n")
        lines.append(self.tab+self.endpos+";\n")
        lines.append(self.tab+self.defTargets+"\n")
        if abbr_props.signalName!="":
            lines.append(self.tab+self.ioStates+"\n")
            lines.append("\n")
        lines.append("PROC move()\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+"SocketCreate socket0;")
            lines.append(self.tab+"SocketConnect socket0, \""+abbr_props.host+"\","+str(abbr_props.port)+";")   
        lines.append(self.tab+"MoveAbsJ startpos, "+"v{0} ".format(abbr_props.speed)+", fine,"+toolName+";\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+self.tab+"SocketSend socket0 \Str:=\"0\";\n")
        lines.append(self.tab+"FOR i FROM 1 TO dim(positions,1)-1 DO\n")
        if abbr_props.signalName!="":
            lines.append(self.tab+self.tab+"IF ioData{i}=1 THEN\n")
            lines.append(self.tab+self.tab+self.tab+"pulseDO "+abbr_props.signalName+";\n")
            lines.append(self.tab+self.tab+"ENDIF\n")
        #lines.append(self.tab+self.tab+"SetDO "+abbr_props.signalName+", ioData{i};\n")
        lines.append(self.tab+self.tab+"MoveAbsJ positions{i}, "+"v{0} ".format(abbr_props.speed)+time+", z15,"+toolName+";\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+self.tab+"SocketSend socket0 \Str:= NumToStr(stride*i,0);\n")
        lines.append(self.tab+"ENDFOR\n")
        lines.append(self.tab+"MoveAbsJ endpos, "+"v{0} ".format(abbr_props.speed)+", fine,"+toolName+";\n")
        if self.endState and abbr_props.signalName!="":
            lines.append(self.tab+"PulseDO "+abbr_props.signalName+";\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+"SocketSend socket0 \Str:=\""+str(self.frameEnd)+"\";\n")
        if abbr_props.reportFrame:
            lines.append(self.tab+"SocketClose socket0;\n")
        lines.append("ENDPROC\n")
        lines.append("\n")
        lines.append("PROC main()\n")
        lines.append(self.tab+"move;\n")
        lines.append("ENDPROC\n")
        lines.append("\n")
        lines.append("ENDMODULE\n")
        with open(abbr_props.path+"\\"+moduleName+".mod",'w')as file:
            file.writelines(lines)

    def execute(self,context):
        jointtargets=[]
        outputStates=[]
        abbr_props=context.scene.abbrProps
        if(abbr_props.path=="//"):
            abbr_props.path=bpy.path.abspath("//")
        scene=context.scene
        self.frameStart=scene.frame_start
        self.frameEnd=scene.frame_end
        armatureName=context.active_object.name
        armature=bpy.data.objects[armatureName]
        bones=armature.pose.bones[1:]
        if abbr_props.IK:
            bpy.ops.object.posemode_toggle()
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.nla.bake(frame_start=1, frame_end=250, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.object.posemode_toggle()
        scene.frame_set(self.frameStart)
        self.startpos="CONST jointtarget startpos := "+self.toJointtarget(bones)
        scene.frame_set(self.frameEnd)
        self.endpos="CONST jointtarget endpos := "+self.toJointtarget(bones)
        self.endState=int(abbr_props.outputState)
        ioState=abbr_props.outputState
        ioPrev=abbr_props.outputState
        for f in range(self.frameStart,self.frameEnd+1):
            scene.frame_set(f)
            if(f%abbr_props.step==0):
                jointtarget=self.toJointtarget(bones)
                jointtargets.append(jointtarget)
                outputStates.append(abbr_props.outputState)
                ioPrev=outputStates[-1]
            elif(ioPrev !=abbr_props.outputState):
                jointtarget=self.toJointtarget(bones)
                jointtargets.append(jointtarget)
                outputStates.append(abbr_props.outputState)
                ioPrev=outputStates[-1]
        #EXPORT POSITIONS
        self.defTargets="CONST jointtarget positions {"+str(len(jointtargets))+"}:= [\n"
        for j in range(0,len(jointtargets)-1):
            self.defTargets+=self.tab+self.tab+jointtargets[j]+",\n"
        self.defTargets+=self.tab+self.tab+jointtargets[-1]+"\n"+self.tab+"];"
        #EXPORT IO
        self.ioStates="CONST num ioData {"+str(len(outputStates))+"}:="+"["
        for j in range(0,len(outputStates)-1):
            self.ioStates+=str(int(outputStates[j]))+","
        self.ioStates+=str(int(outputStates[-1]))+"];\n"
        self.save(context,abbr_props.module_name)
        #print(len(jointtargets))
        return{'FINISHED'}

class abblenderPanel(bpy.types.Panel):
    
    bl_idname="OBJECT_PT_abblender"
    bl_label="ABBlender"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_context="objectmode"
    bl_category="ABBlender"

    def draw(self,context):
        layout=self.layout
        abbr_props=context.scene.abbrProps
        layout.label(text="Export Properties")
        layout.prop(abbr_props,"path")
        layout.prop(abbr_props,"module_name")
        layout.prop(abbr_props,"step")
        layout.prop(abbr_props,"speed")
        layout.label(text="Tool")
        layout.prop(abbr_props,"tool_name")
        layout.label(text="IO Signals")
        layout.prop(abbr_props,"signalName")    
        layout.prop(abbr_props,"outputState")
        layout.label(text="Inverse Kinematics")
        layout.prop(abbr_props,"IK")
        layout.label(text="Communication")
        layout.prop(abbr_props,"reportFrame")
        layout.prop(abbr_props,"host")
        layout.prop(abbr_props,"port")
        layout.separator()
        layout.operator("abblender.joint_target")

#------------------------------------------------
#Class Registration
#------------------------------------------------
classes=(
    AbblenderProperties,
    ExportJointTarget,
    abblenderPanel
    )
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.abbrProps=bpy.props.PointerProperty(type=AbblenderProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.abbrProps