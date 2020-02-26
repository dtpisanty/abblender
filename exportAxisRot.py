import bpy
from math import degrees

#Golobal parameters
frameStart=bpy.context.scene.frame_start
frameEnd=bpy.context.scene.frame_end
armatureName=bpy.context.object.name
armature=bpy.data.objects[armatureName]
tool=bpy.data.objects['Tool']
bones=armature.pose.bones[1:]
speed="v1000" #TODO intregrate to UI
reportFrame=True #TODO intregrate to UI
host = "127.0.0.1"
port=10000
jointtargets=[]
command=""
path=bpy.path.abspath("//") #TODO intregrate to UI
tab="    "
step=5

def toJointtarget(bones,axis='y'):
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
            if(bone.name!="Axis6"):
                out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().x))
            else:
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().x))
        elif(axis=="y"):
            if(bone.name!="Axis6"):
                out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().y))
            else:
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().y))
        elif(axis=="z"):
            if(bone.name!="Axis6"):
                out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().z))
            else:
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ]".format(degrees(bone.matrix_basis.to_euler().z))
        else:
            return
    return out

def save(module_name="Animation"):
    '''
    Compiles the Rapid code and converts saves it to
    <module_name>.mod
    Takes:
        module_name -> String
    Returns:
        None
    '''
    fps=bpy.context.scene.render.fps
    time=""
    if step>1:
        frames=frameEnd-frameStart
        seconds=(frames)/fps
        duration=step*(seconds/frames)
        time="\\T:={:.3f}".format(duration)
        print(time)
    lines=[]
    lines.append("Module "+module_name+"\n")
    lines.append("\n")
    if reportFrame:
        lines.append(tab+"VAR SocketDev socket0;\n")
        lines.append(tab+"CONST num stride:="+str(step)+";\n")
    lines.append(tab+"PERS tooldata noTool := [ TRUE, [ [0, 0, 0], [1, 0,   0 ,0] ], [0.001, [0, 0, 0.001], [1, 0, 0, 0], 0, 0, 0] ];")
    lines.append("\n")
    lines.append(tab+startpos+";\n")
    lines.append(tab+endpos+";\n")
    lines.append(tab+command+"\n")
    lines.append("\n")
    lines.append("PROC animate()\n")
    if reportFrame:
        lines.append(tab+"SocketCreate socket0;")
        lines.append(tab+"SocketConnect socket0, \""+host+"\","+str(port)+";")
    lines.append(tab+"MoveAbsJ startpos, "+speed+", fine, noTool;"+"\n")
    if reportFrame:
        lines.append(tab+tab+"SocketSend socket0 \Str:=\"0\";\n")
    lines.append(tab+"FOR i FROM 1 TO dim(positions,1)-1 DO\n")
    lines.append(tab+tab+"MoveAbsJ positions{i}, "+speed+time+", z15, noTool;\n")
    if reportFrame:
        lines.append(tab+tab+"SocketSend socket0 \Str:= NumToStr(stride*i,0);\n")
    lines.append(tab+"ENDFOR\n")
    lines.append(tab+"MoveAbsJ endpos, "+speed+", fine, noTool;\n")
    if reportFrame:
        lines.append(tab+"SocketSend socket0 \Str:=\""+str(frameEnd)+"\";\n")
    if reportFrame:
        lines.append(tab+"SocketClose socket0;\n")
    lines.append("ENDPROC\n")
    lines.append("\n")
    lines.append("PROC main()\n")
    lines.append(tab+"animate;\n")
    lines.append("ENDPROC\n")
    lines.append("\n")
    lines.append("ENDMODULE\n")
    with open(path+"\\"+module_name+".mod",'w')as file:
        file.writelines(lines)

#Define start jointtarget
bpy.context.scene.frame_set(frameStart)
startpos="CONST jointtarget startpos := "+toJointtarget(bones)        
#Define end jointtarget
bpy.context.scene.frame_set(frameEnd)
endpos="CONST jointtarget endpos := "+toJointtarget(bones) 
        
#Define motion jointtarget array
for f in range(frameStart,frameEnd,step):
    bpy.context.scene.frame_set(f)
    toolPosition=list(tool.matrix_world.translation) #convert to global matrix
    #print("Tool position: "+str(toolPosition[0]*1000)+","+str(toolPosition[1]*1000)+","+str(toolPosition[2]*1000))
    jointtarget=toJointtarget(bones)
    jointtargets.append(jointtarget)
    #print(jointtarget)
command="CONST jointtarget positions {"+str(len(jointtargets))+"}:= [\n"
for j in range(0,len(jointtargets)-1):
    command+=tab+tab+jointtargets[j]+",\n"
command+=tab+tab+jointtargets[-1]+"\n"+tab+"];"
#print(startpos)
#print(endpos)
save("animation")
print("Saved as "+path+"animation.mod")