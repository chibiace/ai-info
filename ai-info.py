#!/usr/bin/env python

#
# -----------------------------------------------------------
#  Gives info on AI generated pictures from ComfyUI, Stable Diffusion
#   and Camera Exif data.
#  chibiace 04/12/2023
# -----------------------------------------------------------
from PIL import Image, ExifTags, TiffImagePlugin
import sys
import json
import ast

# checks to see if there is only two command line arguments, if not check if one.
try:
    script, arg1 = sys.argv
except ValueError:
    # Throws a warning if too many command line arguments and exits
    print("Please use a \033[31mfilename\033[0m in the CWD as argument!")
    sys.exit()



# tries to open the picture
filename = arg1
try:
    im = Image.open(filename)
except FileNotFoundError:
    print("\033[31m"+filename+" not found!\033[0m")
    sys.exit()

im.load()



# has to have prompt, parameters key or exif data
if "prompt" in im.info.keys():
    #comfyui, workflow is also available but we aren't getting that today
    prompt = {}
    prompt.update({"prompt":json.loads(im.info["prompt"])})
else:
    # automatic111, gosh this is a mess.
    if "parameters" in im.info.keys():
        parameters = im.info["parameters"]
        prompt = {"parameters": {}}
        parameters = parameters.split("\n")

        if len(parameters) == 1:
            pass
        if len(parameters) == 2:
            if parameters[0].split(":",1)[0] == "Negative prompt":
                parameters[0] = parameters[0].replace(": ",":")
                parameters[0] = parameters[0].split(":",1)
                
                #neg
                prompt["parameters"].update({parameters[0][0]:parameters[0][1].replace('"',"'")})
            else:
                if parameters[1].split(":",1)[0] == "Steps":
                    #pos
                    prompt["parameters"].update({"Positive prompt":parameters[0].replace('"',"'")})
        if len(parameters) == 3:
            if parameters[1].split(":",1)[0] == "Negative prompt":
                #pos
                prompt["parameters"].update({"Positive prompt":parameters[0].replace('"',"'")})
                parameters[1] = parameters[1].replace(": ",":")
                parameters[1] = parameters[1].split(":",1)
                #neg
                prompt["parameters"].update({parameters[1][0]:parameters[1][1].replace('"',"'")})

        parameters[-1] = parameters[-1].replace(": ",":")
        parameters[-1] = parameters[-1].replace(", ",",")
        parameters[-1] = parameters[-1].split(",")
        for i in range(0,len(parameters[-1])):
            parameters[-1][i] = parameters[-1][i].replace(", ",",")
            parameters[-1][i] = parameters[-1][i].split(":")

            if len(parameters[-1][i]) == 2:
                parameters[-1][i][1] = parameters[-1][i][1].replace('\"',"")
            if parameters[-1][i][0] == "Size":
                parameters[-1][i][1] = parameters[-1][i][1].split("x")

                for s in range(0,len(parameters[-1][i][1])):
                    parameters[-1][i][1][s] = int(parameters[-1][i][1][s])

                prompt["parameters"].update({"width" : parameters[-1][i][1][0]})
                prompt["parameters"].update({"height" : parameters[-1][i][1][1]})

            else:
                try:
                    if parameters[-1][i][1].isnumeric():
                        parameters[-1][i][1] = int(parameters[-1][i][1])
                    #might want to check for floats here
                    prompt["parameters"].update({parameters[-1][i][0] : parameters[-1][i][1]})
                except:
                    if len(parameters[-1][i]) == 1:
                        if len(parameters[-1][i-1]) == 1:
                            values = f'{parameters[-1][i-2][1]},{parameters[-1][i-1][0]},{parameters[-1][i][0]}'.replace('\"',"")

                            
                            try:
                                values = ast.literal_eval(values)
                                prompt["parameters"].update({parameters[-1][i-2][0] : values})
                            except:
                                pass
                                prompt["parameters"].update({parameters[-1][i-2][0] : values})
                        else:
                            values = f'{parameters[-1][i-1][1]},{parameters[-1][i][0]}'.replace('\"',"")
                            try:
                                values = ast.literal_eval(values)
                            except:
                                pass
                            prompt["parameters"].update({parameters[-1][i-1][0] : values})
        

        
    else:
        # exif, camera etc
        exif = im.getexif()

        if not exif is None:
            prompt = {"exif":{}}
            for key, val in exif.items():
                if key in ExifTags.TAGS:
                    #this sony rubbish doesn't play nice
                    if ExifTags.TAGS[key] == "PrintImageMatching":
                        pass
                    else:
                        if type(val) == TiffImagePlugin.IFDRational:
                            val = int(val)
                        if type(val) == str:
                        # val = str(val)
                            val = val.replace("\x00","")
                        
                        prompt["exif"].update({ExifTags.TAGS[key] : val})



# prints out the info
def print2terminal():
    if type(prompt) == dict:
        print(json.dumps(prompt,indent=2))

    if type(prompt) == str:
        print(json.dumps(json.loads(prompt),indent=2))

print2terminal()
