def loading_bar(current,total):
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = (current / total) * 100
    print(f'\r|{bar}| {percent:.2f}% Complete ({current/1000000:.2f} MB out of {total/1000000:.2f} MB)', end='\r', flush=True)
    if current == total:
        print()
