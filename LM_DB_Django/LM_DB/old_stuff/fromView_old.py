'''# currently not necessary anymore DONE: transfer functionality from this into on upload
def handle_uploaded_file(file, bibtex_str, file_name):
    base_destination = MEDIA_ROOT[:-1]  # has wrong side slash at the end, no problem caused, but slicing it off for now
    if file_name is None:
        filename = file.name
    else:
        filename = file_name
        file.name = file_name  # change name
    if bibtex_str is not None:
        bib = bibtexparser.loads(bibtex_str)
        print(bib.entries)
        year = str(bib.entries[0]['year'])
    else:
        year = "unknown_year"
    current_location = os.path.join(base_destination, year)
    print(current_location)
    if not os.path.isdir(current_location) and not os.path.exists(current_location):
        os.makedirs(current_location)
        print("making dir")
    path_and_paper = os.path.join(current_location, filename)
    print(path_and_paper)

    with open(path_and_paper, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            print("writing")

    file_dict = {"complete_file_path": year, "file_name": filename}
    return file_dict'''