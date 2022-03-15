def confirm_command():
    response = input('This command is dangerous, are you sure (y/n): ')
    return response.lower() == 'y'
