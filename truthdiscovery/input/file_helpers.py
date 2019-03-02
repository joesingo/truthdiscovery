from truthdiscovery.input.dataset import Dataset
from truthdiscovery.input.supervised_data import SupervisedData


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
        constructor. This method must be implemented in child classes.

        :param fileobj: file object to read data from
        :yield: data tuples of the form ``(source_label, var_label, value)``
        """
        raise NotImplementedError("Must be implemented in child classes")


class FileSupervisedData(SupervisedData):
    """
    Abstract class for loading supervised data from files
    """
    def __init__(self, dataset, truth_path):
        """
        :param dataset: a :any:`Dataset` (or sub-class) object
        :param filepath: path to file on disk to load true values from
        """
        values = {}
        with open(truth_path) as truth_file:
            values = dict(self.get_pairs(truth_file))
        super().__init__(dataset, values)

    def get_pairs(self, fileobj):
        """
        Parse a file and yield the variables and true values. This method must
        be implemented in child classes.

        :param fileobj: file object to read from
        :yield: tuples of the form ``(var, true_value)``
        """
        raise NotImplementedError("Must be implemented in child classes")
