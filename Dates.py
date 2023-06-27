
def get_time_tuple(current_time):
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    milliseconds = int((current_time % 1) * 1000)
    return minutes, seconds, milliseconds
