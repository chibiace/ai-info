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
import re
# checks to see if there is only two command line arguments, if not check if one.
try:
    script, arg1 = sys.argv
except ValueError:
    # Throws a warning if too many command line arguments and exits
    print("Please use a \033[31mfilename\033[0m in the CWD as argument!")
    sys.exit()


def type_changer(value):
    if value.isnumeric():
        return int(value)
    else:
        return value

def debug(text):
    print(f'\n\033[31m{text}\033[0m\n')

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
        parameters = re.split('(Negative prompt): |(Negative Template): |(Template): |(ControlNet): |\n',parameters)


        #removes None and new lines
        parameters_clean_none = []
        for i in range(0,len(parameters)):
            if parameters[i] == None:
                pass
            elif parameters[i] == "":
                pass
            else:
                parameters_clean_none.append(parameters[i])
        parameters = parameters_clean_none


        #settings field
        parameters_settings = {}
        for i in range(0,len(parameters)):
            if parameters[i].split(":",1)[0] == "Steps":
                parameters[i] = re.split(", ",parameters[i])
                for k in parameters[i]:
                    k = k.split(": ",1)
                    if len(k) == 2:
                        k[1] = type_changer(k[1])

                        #makes "Size" : "(widthxheight)" into two keys
                        if k[0] == "Size":
                            k[1] = k[1].split("x")
                            for s in range(0,len(k[1])):
                                k[1][s] = type_changer(k[1][s])
                            parameters_settings.update({"width" : k[1][0]})
                            parameters_settings.update({"height" : k[1][1]})
                        
                        else:
                            parameters_settings.update({k[0]:k[1]})


                parameters[i] = parameters_settings
            
        #builder
        parameters_built = {}
        for i in range(0,len(parameters)):
            match parameters[i]:
                case "Negative prompt":
                    parameters_built.update({parameters[i]:parameters[i+1]})
                case "Negative Template":
                    parameters_built.update({parameters[i]:parameters[i+1]})
                case "Template":
                    parameters_built.update({parameters[i]:parameters[i+1]})
                case "ControlNet":
                    parameters_built.update({parameters[i]:parameters[i+1]})
                case dict():
                    parameters_built.update(parameters[i])
                case _:
                    if i == 0:
                        parameters_built.update({"Positive prompt": parameters[i]})
                    pass


        
        prompt["parameters"] = parameters_built


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
