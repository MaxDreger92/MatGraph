import pandas as pd
from django.template.loader import render_to_string

from importing.models import ImporterCache


class ReportBuilder:
    """
    Base class for building and saving reports.

    Attributes:
        ReportClass: The Django model class used for creating and saving report objects.
        results: Stores results data for the report.
    """

    def __init__(self, ReportClass):
        """
        Initializes the ReportBuilder with a Django model class for report generation.

        Args:
            ReportClass: The Django model class for creating and saving report objects.
        """
        self.ReportClass = ReportClass
        self.results = None

    def build_results(self):
        """
        Builds the results for the report.
        """
        raise NotImplementedError

    def build_report(self):
        """
        Converts the stored results into a DataFrame and generates an HTML report.
        """
        self.report = pd.DataFrame(self.results)
        self.html_report = render_to_string('reports/results.html', {
            'label': 'Results',
            'columns': self.report.columns,
            'rows': self.report.values.tolist(),
        })

    def save_report(self, **kwargs):
        """
        Saves the generated report to the database.

        Args:
            **kwargs: Keyword arguments containing report details.
        """
        report = self.ReportClass(**kwargs)
        report.save()




class TableDataTransformer(ReportBuilder):
    """
    Transforms table data for reporting. Inherits from ReportBuilder.

    Attributes:
        headers (pandas.Series): The headers of the table data.
        data (pandas.DataFrame): The table data excluding headers.
        context (str): Contextual information about the data.
        file_link (str): Link to the source file.
        file_name (str): Name of the source file.
        report_file_link (str): Link to the generated report.
        cache (bool): Indicates whether to use cached data.
        _results (list): Stores the transformed results.
    """

    def __init__(self, data, context, file_link, file_name, ReportClass, cache= True, **kwargs):
        """
        Initializes the data transformer with the given table data and configuration.

        Args:
            data (pandas.DataFrame): The table data.
            context (str): Context of the data.
            file_link (str): Link to the data file.
            file_name (str): Name of the data file.
            ReportClass: The Django model class for report generation.
            cache (bool): Flag to enable or disable caching.
        """
        self.data = data
        self.context = context
        self.file_link = file_link
        self.file_name = file_name
        self.report_file_link = None
        self._results = []
        self.report = ""
        self.html_report = ""
        self.cache = cache
        self.ReportClass = ReportClass


    @property
    def iterable(self):
        """
        Returns the headers for iteration.

        Returns:
            pandas.Series: The headers of the table data.
        """
        return self.data
    def iterate(self):
        """
        Iterates over each header to transform the data.
        """
        for index, element in enumerate(self.iterable):
            self._process(element = element, index = index)


    def _process(self, **kwargs):
        """
        Processes each header, checking cache and transforming data as needed.

        Args:
            **kwargs: Contains information about the current element and index.
        """
        if self._pre_check(**kwargs):
            return
        elif self._check_cache(**kwargs):
            return
        else:
            self._transform(**kwargs)


    def _check_cache(self, **kwargs):
        """
        Checks for cached data for the current header.

        Args:
            **kwargs: Contains information about the current element and index.

        Returns:
            bool: True if cached data is used.
        """
        column_value = kwargs['element']['column_values'][0]

        if cached := ImporterCache.fetch(kwargs['element']['header'], column_value ):
            self._update_with_cache(cached, **kwargs)
            return True
        return False

    def _pre_check(self, element, **kwargs):
        return NotImplementedError

    @property
    def results(self):
        return self._results

    def _transform(self, **kwargs):
        """
        Transform the data.
        """
        input_string = self._create_input_string(**kwargs)
        query_result = self._llm_request(input_string, **kwargs)
        self._update(query_result, input_string, **kwargs)

    def _update_with_cache(self, element, cached, **kwargs):
        return NotImplemented

    def _update(self, element, **kwargs):
        return NotImplemented

    @property
    def input_string(self):
        return self.input_string

    def _llm_request(self, input_string):
        return NotImplemented
    def run(self):
        """
        Executes the data transformation, builds the report, and saves it.
        """
        self.iterate()
        self.build_results()
        self.build_report()
        self.save_report(report=self.report, context=self.context, file_link=self.file_link,
                         html_report=self.html_report, report_file_link=self.report_file_link,
                         file_name=self.file_name)