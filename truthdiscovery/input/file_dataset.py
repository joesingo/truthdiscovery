from truthdiscovery.input.dataset import Dataset


class FileDataset(Dataset):
    """
    Abstract class for loading datasets from files of a custom user-defined
    format
    """
    def __init__(self, filepath, *args, **kwargs):
        """
        :param filepath: path to file on disk to load dataset from
        """
        with open(filepath) as fileobj:
            super().__init__(self.get_tuples(fileobj), *args, **kwargs)

    def get_tuples(self, fileobj):
        """
        Parse a file and yield data tuples as required for the :any:`Dataset`
        constructor.

        This method must be implemented in child classes.

        :param fileobj: file object to read data from
        :yield: data tuples of the form ``(source_label, var_label, value)``
        """
        raise NotImplementedError("Must be implemented in child classes")
