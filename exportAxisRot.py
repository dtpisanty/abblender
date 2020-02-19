import bpy
from math import degrees

frameStart=bpy.context.scene.frame_start
frameEnd=bpy.context.scene.frame_end
armature=bpy.data.objects['Armature']
tool=bpy.data.objects['Tool']
jointtargets=[]
bones=armature.pose.bones[1:]
speed="v1000"
command=""
path="C:\\Users\\D1390\\Dropbox\\investigacion\\robot"
tab="    "
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
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ];".format(degrees(bone.matrix_basis.to_euler().x))
        elif(axis=="y"):
            if(bone.name!="Axis6"):
                if(bone.name!="Axis2"):
                    out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().y)*-1)
                else:
                    out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().y))
            else:
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ];".format(degrees(bone.matrix_basis.to_euler().y))
        elif(axis=="z"):
            if(bone.name!="Axis6"):
                out+="{:.2f},".format(degrees(bone.matrix_basis.to_euler().z))
            else:
                out+="{:.2f}], [ 9E9, 9E9, 9E9, 9E9, 9E9, 9E9] ];".format(degrees(bone.matrix_basis.to_euler().z))
        else:
            return
    return out

def save(filename,module_name="Animation"):
    lines=[]
    lines.append("Module "+module_name+"\n")
    lines.append("\n")
    lines.append(tab+"PERS tooldata noTool := [ TRUE, [ [0, 0, 0], [1, 0, 0 ,0] ], [0.001, [0, 0, 0.001], [1, 0, 0, 0], 0, 0, 0] ];")
    lines.append("\n")
    lines.append(tab+startpos+"\n")
    lines.append(tab+endpos+"\n")
    lines.append(tab+command+"\n")
    lines.append("\n")
    lines.append("PROC animate()\n")
    lines.append(tab+"MoveAbsJ startpos, "+speed+", fine, noTool;"+"\n")
    lines.append(tab+"FOR i FROM 1 TO dim(jointtarget,1) DO\n")
    lines.append(tab+tab+"MoveAbsJ jointtarget{i}, "+speed+", z15, noTool;\n")
    lines.append(tab+"ENDFOR\n")
    lines.append(tab+"MoveAbsJ endpos, "+speed+", fine, noTool;\n")
    lines.append("ENDPROC\n")
    lines.append("\n")
    lines.append("PROC main()\n")
    lines.append(tab+"animate;\n")
    lines.append("ENDPROC\n")
    lines.append("\n")
    lines.append("ENDMODULE\n")
    with open(path+"\\"+filename,'w')as file:
        file.writelines(lines)

#Define start jointtarget
bpy.context.scene.frame_set(frameStart)
startpos="CONST jointtarget startpos := "+toJointtarget(bones)        
#Define end jointtarget
bpy.context.scene.frame_set(frameEnd)
endpos="CONST jointtarget endpos := "+toJointtarget(bones) 
        
#Define motion jointtarget array
for f in range(frameStart,frameEnd):
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
save("animation.mod")
print("Saves as animation.mod")

