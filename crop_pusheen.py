from PIL import Image
def crop_pusheen():
    for name in ['pusheen_gray_1.png', 'pusheen_gray_2.png', 'pusheen_pink_1.png',
                 'pusheen_pink_2.png', 'pusheen_green_1.png', 'pusheen_green_2.png']:
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = Image.open(fullname)
        image = image.crop((450, 685, 2505, 1900))
        image.save(fullname)
