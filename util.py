extensions = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']


def dict2int(x):
    x_ = ''
    for i in x['name']:
        if i.isdigit():
            x_ += i
    return int(x_)


def str2int(x):
    x_ = ''
    for i in x:
        if i.isdigit():
            x_ += i
    return int(x_)


def str_clean(x: str, size=5):
    x = x.split('.')[0]
    if x.isdigit():
        return x.zfill(size)
    x_ = ''
    for i in x:
        if i.isdigit() or i.isalpha():
            x_ += i
    return x_


def str_sum(x, size=15):
    result = 0
    for x_ in x:
        x_ = ord(x_)
        result *= 10
        if 47 < x_ < 58:  # digit 10 ~ 19
            result += x_ - 38
        elif 64 < x_ < 91:  # large 0 ~ 25
            result += x_ - 65
        elif 96 < x_ < 123:  # small 0 ~ 25
            result += x_ - 97
    return result


def check_extension(x):
    flag = False
    for ex in extensions:
        if x.endswith(ex):
            flag = True
            break
    return flag


def clean_dir_list(data):
    result = [d for d in data if check_extension(d)]
    result.sort(key=str_clean)
    return result


if __name__ == '__main__':
    import os
    img_path = 'E:/hitomi_downloader_GUI/hitomi_downloaded/[Henrybird][1351539]/'
    dir_list = os.listdir(img_path)

    img_list = clean_dir_list(dir_list)
    print(img_list)
