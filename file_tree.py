import os
import pickle
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


LIKEABILITY = 'like.data'


def get_data(path):
    artist_dict = dict()
    source = os.listdir(path)

    for s in source:
        temp = s.split(']')
        artist, hitomi_num = temp[0][1:].split(','), int(temp[1][1:])
        page = len(os.listdir(path + s + '/'))
        for a in artist:
            while a[0] == ' ':
                a = a[1:]
            if a in artist_dict:
                artist_dict[a]['hitomi_num'].append(hitomi_num)
                artist_dict[a]['page'].append(page)
                artist_dict[a]['file name'].append(s)
            else:
                artist_dict[a] = {'hitomi_num': [hitomi_num], 'page': [page], 'file name': [s]}
                # artist_dict[a] = [hitomi_num]

    return artist_dict


def get_artist_tree(path):
    artist_dict = get_data(path)
    artist_widget = QTreeWidget()
    artist_widget.setSortingEnabled(True)
    artist_widget.setHeaderLabels(['artist', 'hitomi number', 'page', 'likeability', 'file name'])

    for artist, data in artist_dict.items():
        parent = QTreeWidgetItem(artist_widget)
        parent.setText(0, artist)
        parent.setText(3, '00000')
        for i, num in enumerate(data['hitomi_num']):
            child = QTreeWidgetItem(parent)
            child.setText(0, str(i+1).zfill(2))
            child.setText(1, str(num))
            child.setText(2, str(data['page'][i]))
            child.setText(3, '0')
            child.setText(4, data['file name'][i])
        parent.setExpanded(False)
    return artist_widget


def open_tree(artist_widget: QTreeWidget, signal=True):
    for i in range(artist_widget.topLevelItemCount()):
        artist = artist_widget.topLevelItem(i)
        artist.setExpanded(signal)


def load_likeability(artist_widget: QTreeWidget):
    if os.path.isfile(LIKEABILITY):
        with open(LIKEABILITY, 'rb') as file:
            likeability_dict = pickle.load(file)
        for i in range(artist_widget.topLevelItemCount()):
            artist = artist_widget.topLevelItem(i)
            if artist.text(0) in likeability_dict:
                artist.setText(3, likeability_dict[artist.text(0)]['likeability'].zfill(5))
                for j in range(artist.childCount()):
                    child = artist.child(j)
                    if child.text(1) in likeability_dict[artist.text(0)]['childs']:
                        child.setText(3, likeability_dict[artist.text(0)]['childs'][child.text(1)])
        # artist_widget.sortItems(3)
        print('load complete from', LIKEABILITY)
    else:
        return False


def save_likeability(artist_widget: QTreeWidget):
    likeability_dict = dict()
    for i in range(artist_widget.topLevelItemCount()):
        artist = artist_widget.topLevelItem(i)
        likeability_dict[artist.text(0)] = {'likeability': artist.text(3), 'childs': {}}
        for j in range(artist.childCount()):
            child = artist.child(j)
            likeability_dict[artist.text(0)]['childs'][child.text(1)] = child.text(3)
    with open(LIKEABILITY, 'wb') as file:
        pickle.dump(likeability_dict, file)


def update_artist_widget(artist_widget: QTreeWidget):
    # update likeability
    current_item = artist_widget.currentItem()
    artist_item = current_item.parent()
    likeability = 0
    for j in range(artist_item.childCount()):
        child = artist_item.child(j)
        likeability += int(child.text(3))
    artist_item.setText(3, str(likeability).zfill(5))

    #save likeability
    save_likeability(artist_widget)


if __name__ == '__main__':
    artist_list = get_data('E:/hitomi_downloader_GUI/hitomi_downloaded/')
