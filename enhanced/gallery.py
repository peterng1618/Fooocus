import gradio as gr
import os
import math
import json
import modules.util as util
import modules.config as config

from lxml import etree

output_list = []
max_per_page = 28

images_list=['',[]]

images_prompt=['',[]]

def refresh_output_list():
    global output_list, max_per_page

    listdirs = [f for f in os.listdir(config.path_outputs) if os.path.isdir(os.path.join(config.path_outputs,f))]
    if listdirs is None:
        return
    listdirs1 = listdirs.copy()
    for index in listdirs:
        path_gallery = os.path.join(config.path_outputs, index)
        nums = len(util.get_files_from_folder(path_gallery, ['.png'], None))
        if nums > max_per_page:
            for i in range(1,math.ceil(nums/max_per_page)+1):
                listdirs1.append(index + "/" + str(i))
            listdirs1.remove(index)
    output_list = sorted([f[2:] for f in listdirs1], reverse=True)
    print(f'[Gallery] Refresh_output_list: loaded {len(output_list)} images_lists.')
    return

def refresh_images_list(choice):
    global output_list, images_list


    if choice == images_list[0]:
        if images_list[0] == output_list[0].split('/')[0]:
            images_list[1] = sorted([f for f in util.get_files_from_folder(os.path.join(config.path_outputs, '20' + images_list[0]), ['.png'], None)], reverse=True) 
        return
    images_list[0] = choice
    images_list[1] = sorted([f for f in util.get_files_from_folder(os.path.join(config.path_outputs, '20' + images_list[0]), ['.png'], None)], reverse=True)
    parse_html_log(choice)
    print(f'[Gallery] Refresh_images_list: loaded {len(images_list[1])} image_items of {images_list[0]}.')
    return

def get_images_from_gallery_index(choice):
    global output_list, images_list, max_per_page

    if choice is None:
        refresh_output_list()
        if len(output_list) == 0:
            return None
        choice = output_list[0]
    page = 0
    _page = choice.split("/")
    if len(_page) > 1:
        choice = _page[0]
        page = int(_page[1])

    refresh_images_list(choice)
    images_gallery = images_list[1]
    nums = len(images_gallery)
    if page > 0:
        page = abs(page-math.ceil(nums/max_per_page))+1
        if page*max_per_page < nums:
            images_gallery = images_list[1][(page-1)*max_per_page:page*max_per_page-1]
        else:
            images_gallery = images_list[1][nums-max_per_page:]
    images_gallery = [os.path.join(os.path.join(config.path_outputs, '20' + choice), f) for f in images_gallery]
    #print(f'[Gallery]Get images from index: choice={choice}, page={page}, images_gallery={images_gallery}')
    return images_gallery


refresh_output_list()


def get_images_prompt(choice, selected):
    global images_list, images_prompt

    page = 0
    _page = choice.split("/")
    if len(_page) > 1:
        choice = _page[0]
        page = int(_page[1])

    if choice != images_prompt[0] or images_prompt[1] is None:
        parse_html_log(choice)
        images_prompt[0] = choice
    nums = len(images_prompt[1])
    if page > 0:
        page = abs(page-math.ceil(nums/max_per_page))+1
        if page*max_per_page < nums:
            selected = (page-1)*max_per_page + selected
        else:
            selected = nums-max_per_page + selected
    return images_prompt[1][selected]


def parse_html_log(choice):
    global images_prompt
    
    html_file = os.path.join(os.path.join(config.path_outputs, '20' + choice), 'log.html')

    html = etree.parse(html_file, etree.HTMLParser())
    prompt_infos = html.xpath('/html/body/div')
    images_prompt[1] = []
    for info in prompt_infos:
        def standardized(x):
            if x.startswith(', '):
                x=x[2:]
            if x.endswith(': '):
                x=x[:-2]
            if x==' ':
                x=''
            return x
        text = list(map(standardized, info.xpath('.//p//text()')))
        if text[6]!='':
            text.insert(6, '')
        #print(f'text={text}')
        info_json='{' + f'"Filename": "{text[0]}",\n' \
                      + f'"{text[1]}": "{text[2]}",\n' \
                      + f'"{text[4]}": "{text[5]}",\n' \
                      + f'"{text[7]}": "{text[8]}",\n' \
                      + f'"{text[10]}": "{text[11]}",\n' \
                      + f'"{text[12]}": "{text[13]}",\n' \
                      + f'"{text[14]}": "{text[15]}",\n' \
                      + f'"{text[16]}": "{text[17]}",\n' \
                      + f'"{text[18]}": "{text[19]}",\n' \
                      + f'"{text[20]}": "{text[21]}",\n' \
                      + f'"{text[22]}": "{text[23]}",\n' \
                      + f'"{text[24]}": "{text[25]}",\n' \
                      + f'"{text[26]}": "{text[27]}",\n' \
                      + f'"{text[28]}": "{text[29]}",\n' \
                      + f'"{text[30]}": "{text[31]}",\n' \
                      + f'"{text[32]}": "{text[33]}",\n' \
                      + f'"{text[34]}": "{text[35]}"' + '}'
        #print(f'info_json={info_json}')
        images_prompt[1].append(json.loads(info_json))
    images_prompt[0] = choice
    print(f'[Gallery] Parse_html_log: loaded {len(images_prompt[1])} image_infos of {choice}.')
    

def select_gallery(choice, selected, prompt_info, evt: gr.SelectData):

    result = get_images_prompt(choice, evt.index)
    print(f'[Gallery] Selected_gallery: selected index {evt.index} of {choice} images_list.')

    return result, gr.update(value=make_infobox_markdown(result))

def make_infobox_markdown(info):
    bgcolor = '#ddd'
    if config.theme == "dark":
        bgcolor = '#444'
    html = f'<div style="background: {bgcolor}">'
    if info:
        for key in info:
            if key == 'Filename':
                continue
            html += f'<b>{key}:</b> {info[key]}<br/>'
    else:
        html += '<p>info</p>'
    html += '</div>'
    return html

infobox_state = False

def toggle_prompt_info(prompt_info):
    global infobox_state
    infobox_state = not infobox_state
    print(f'[Gallery] Toggle_image_info: {infobox_state}')
    return gr.update(value=make_infobox_markdown(prompt_info), visible=infobox_state)

