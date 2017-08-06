FILES_IMG = (("Image files", ("*.jpg", "*.png")), ("All files", "*.*"))
FILES_STITCH = (("Json file", ("*.json")), ("All files", "*.*"))


def input_int(prompt, imin=None, imax=None):
    '''
    Prompt the user to input an integer, and don't stop prompting until a valid
    integer is given.

    prompt - Prompt given to user
    imin   - Minimum value that will be accepted
    imax   - Maximum value that will be accepted
    '''
    while True:
        i = input(prompt)
        try:
            val = int(i)
            if imin is not None and val < imin:
                print("Number should be at least {}".format(imin))
            elif imax is not None and val > imax:
                print("Number should be at most {}".format(imax))
            else:
                return val
        except ValueError:
            print("Not a valid integer!")
