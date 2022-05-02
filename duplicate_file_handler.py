import sys
import os
import hashlib


def _get_file_contents(path):
    """Returns the contents of a file in bytes."""
    with open(path, 'rb') as file:
        contents = file.read()

    return contents


class FileHandler:
    def __init__(self):
        self.args = []
        self.root = ''
        self.file_format = ''
        self.sorting_options = {
            '1': 'Descending',
            '2': 'Ascending'
        }
        self.user_sorting_option = ''
        self.file_dictionary = {}
        self.file_hash_table = {}
        self.duplicate_files = []

    def main(self):
        self._set_root()
        self._check_cmd_input()
        self._set_file_format()
        self._print_sorting_options()
        self._set_sorting_option()
        self._set_file_dictionary()
        self._print_files_sizes()

        if self._wants_duplicate_check():
            self._get_file_hash_table()
            self._print_duplicates()

        if self._is_deleting_duplicates():
            self._format_duplicate_files()
            self._files_to_delete()

        return

    def _set_root(self):
        """Reads the root directory from command line input to set the root attribute."""
        self.args = sys.argv
        self.root = self.args[-1]
        return

    def _check_cmd_input(self):
        """Checks that a root directory was specified via the command line."""
        if len(self.args) == 1:
            print("Directory is not specified")
            return False

        return True

    def _set_file_format(self):
        """Sets the file format attribute via user input."""
        self.file_format = input("Enter file format:\n")
        return

    def _print_sorting_options(self):
        """Presents the sorting options to the user."""
        print("Size  sorting options:")
        for number, selection in self.sorting_options.items():
            print(number + '. ' + selection)
        return

    def _get_sorting_option(self):
        """Returns the sorting option selected by the user."""
        user_choice = input("\nEnter a sorting option (number):\n")
        if user_choice in self.sorting_options.keys():
            return self.sorting_options[user_choice]
        else:
            print("Wrong option")
            return self._get_sorting_option()

    def _set_sorting_option(self):
        """Sets the user_sorting_option attribute."""
        self.user_sorting_option = self._get_sorting_option()
        return

    def _get_file_list(self):
        """Returns a list whose elements are [file_path, file_size]."""
        file_list = []
        for root, dirs, files in os.walk(self.root):
            for file in files:
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                file_list.append([path, size])

        file_name_index = 0
        if self.file_format:
            return [file for file in file_list if file[file_name_index].endswith(self.file_format)]
        else:
            return [file for file in file_list]

    def _get_file_dictionary(self, file_list):
        """Takes a list of lists with elements [file_name, file_size] and returns a dictionary of files sorted by size.
        Keys are sizes and values are a list of the files with that size."""
        sizes = []
        file_name_index = 0
        file_size_index = 1
        file_dictionary = {}

        for file in file_list:
            sizes.append(file[file_size_index])

        sizes = list(set(sizes))
        if self.user_sorting_option == 'Ascending':
            sizes.sort()
        elif self.user_sorting_option == 'Descending':
            sizes.sort(reverse=True)

        for size in sizes:
            file_dictionary[size] = []

        for file in file_list:
            file_dictionary[file[file_size_index]].append(file[file_name_index])

        return file_dictionary

    def _set_file_dictionary(self):
        """Sets the file_dictionary attribute."""
        files = self._get_file_list()
        self.file_dictionary = self._get_file_dictionary(files)
        return

    def _print_files_sizes(self):
        """Prints the files in the given root and subdirectories sorted by size."""
        for size, file in self.file_dictionary.items():
            print('\n' + str(size) + ' bytes')
            print('\n'.join(file))

        return

    def _wants_duplicate_check(self):  # Boolean
        """Sets the duplicate check attribute."""
        answer = input("\nCheck for duplicates? 'yes' or 'no'\n")

        if answer == 'yes':
            return True
        if answer == 'no':
            return False

        print("Wrong option")
        return self._wants_duplicate_check()

    def _get_file_hash_table(self):
        """Creates a dict object where each value is a dict object whose name is a size in bytes.
        These size dict objects have key-value pairs of <hash of file content>: <file path>."""
        for size, file_list in self.file_dictionary.items():
            self._update_hash_bucket(size, file_list)

        return

    def _update_hash_bucket(self, size, file_list):
        """Creates a hash bucket or updates it if one already exists for the given hash."""
        self.file_hash_table[size] = {}
        for file in file_list:
            _hash = hashlib.md5(_get_file_contents(file)).hexdigest()

            try:
                self.file_hash_table[size][_hash].append(file)
            except KeyError:
                self.file_hash_table[size][_hash] = []
                self.file_hash_table[size][_hash].append(file)

        return

    def _print_duplicates(self):
        """Prints the duplicate files."""
        counter = (num for num in range(1, 100))
        for size, hash_table, in self.file_hash_table.items():
            if any([len(self.file_hash_table[size][_hash]) > 1 for _hash in hash_table]):
                print('\n' + str(size), 'bytes')
                self._print_duplicates_assist(hash_table, size, counter)

        return

    def _print_duplicates_assist(self, hash_table, size, counter):
        """Gets rid of a level of nesting in the _print_duplicates method."""
        for _hash in hash_table.keys():
            files = self.file_hash_table[size][_hash]
            if len(files) > 1:
                print(f'Hash: {_hash}')
                duplicate_files = [f'{next(counter)}. {file}' for file in files]
                self.duplicate_files.extend(duplicate_files)
                print(*duplicate_files, sep='\n')

        return

    def _is_deleting_duplicates(self):  # Boolean
        """Determines if the user wants to delete the duplicates found by the program."""
        answer = input('\nDelete files?\n')
        return True if answer == 'yes' else False

    def _format_duplicate_files(self):
        """Reformats the duplicate_files attribute to make it easier to work with.
        It is not a nested list, with elements [<number of duplicate file>, <duplicate file name>]."""
        reformatted_duplicate_files = []
        for file in self.duplicate_files:
            new_format = file.split(' ')
            reformatted_duplicate_files.append(new_format)

        self.duplicate_files = reformatted_duplicate_files
        return

    def _files_to_delete(self):
        """Asks the user which files they want to delete."""
        selections = input('\nEnter file numbers to delete (space separated integers corresponding to the file):\n')
        choices = selections.split()
        if not choices:
            print('\nWrong format')
            return self._files_to_delete()

        if self._choices_are_valid(choices):
            self._delete_duplicate_choices(choices)
            return
        else:
            return self._files_to_delete()

    def _choices_are_valid(self, choices):
        """Determines if the user entered valid file choices to be deleted."""
        valid_choices = [file[0][:-1] for file in self.duplicate_files]  # -1 accounts for the period after the numbers
        if all([(choice in valid_choices) for choice in choices]):
            return True

        print('\nWrong format\n')
        return False

    def _delete_duplicate_choices(self, choices):
        """Deletes the duplicate files selected by the user."""
        freed_up_space = 0

        temp_dict = {file[0][:-1]: file[1] for file in self.duplicate_files}

        for choice in choices:
            freed_up_space += os.path.getsize(temp_dict[choice])
            os.remove(temp_dict[choice])

        print(f'\nTotal freed up space: {freed_up_space} bytes')
        return


my_handler = FileHandler()
my_handler.main()
