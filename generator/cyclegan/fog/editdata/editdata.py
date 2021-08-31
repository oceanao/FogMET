import PySimpleGUI as sg
# import PySimpleGUIQt as sg
import os.path
import PIL.Image
import io
import base64
#Annotations.csv
"""
    Demo for displaying any format of image file.
    
    Normally tkinter only wants PNG and GIF files.  This program uses PIL to convert files
    such as jpg files into a PNG format so that tkinter can use it.
    
    The key to the program is the function "convert_to_bytes" which takes a filename or a 
    bytes object and converts (with optional resize) into a PNG formatted bytes object that
    can then be passed to an Image Element's update method.  This function can also optionally
    resize the image.
    
    Copyright 2020 PySimpleGUI.org
"""


# PIL supported image types
img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()



# --------------------------------- Define Layout ---------------------------------

# First the window layout...2 columns
file_num_display_elem = sg.Text('File 1 of {}'.format(10), size=(15, 1))
left_col = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,30),key='-FILE LIST-'),
             sg.Listbox(values=[], enable_events=True, size=(10,30),key='-CSV LIST-')],
            [file_num_display_elem]]

# col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
#              [sg.Button('Next', size=(8, 2)), sg.Button('Prev', size=(8, 2)), file_num_display_elem]]
# For now will only show the name of the file that was chosen

images_col = [[sg.Text('You choose from the list:')],
              [sg.Text(size=(120,1), key='-TOUT-')],
              [sg.Image(key='-IMAGE-')],
              [sg.Button('<Prev', size=(8, 1)), sg.Input(key="-fogbit-",size=(6, 1)),sg.Button('Save',size=(4, 1)),sg.Button('Next>', size=(8, 1))]]

# ----- Full layout -----
layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),sg.Column(images_col, element_justification='c')]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('Multiple Format Image Viewer', layout,resizable=True)
fogvalues=[]
# ----- Run the Event Loop -----
# --------------------------------- Event Loop ---------------------------------
# loop reading the user input and displaying image, filename
i = 0
new_size=(720,480)
num_files = 10               # number of iamges found
# 导入CSV安装包
import csv
f = open('Annotations.csv','w',encoding='utf-8')
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        f.close()
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
            num_files=len(file_list)
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))]
        window['-CSV LIST-'].update([])
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)
            # if values['-W-'] and values['-H-']:
            #     new_size = int(values['-W-']), int(values['-H-'])
            # else:
            #     new_size = None
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename
    elif event in ('Next>', 'MouseWheel:Down', 'Down:40', 'Next:34'):
        i += 1
        if i >= num_files:
            i -= num_files
        filename = os.path.join(folder, fnames[i])
        window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
    elif event in ('<Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33'):
        i -= 1
        if i < 0:
            i = num_files + i
        filename = os.path.join(folder, fnames[i])
        window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
    elif event =='Save':
        print(filename,values['-fogbit-'])
        csv_writer = csv.writer(f)
        # window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
        fogvalues.append(values['-fogbit-'])
        window['-CSV LIST-'].update(fogvalues)
        csv_writer.writerow([filename, values['-fogbit-']])
    elif event == 'listbox':            # something from the listbox
        f = values["listbox"][0]            # selected filename
        filename = os.path.join(folder, f)  # read this file
        i = fnames.index(f)                 # update running index
    file_num_display_elem.update('File {} of {}'.format(i + 1, num_files))
# --------------------------------- Close & Exit ---------------------------------
window.close()
