from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam
import logging

class LeftJoin(beam.PTransform):
    """This PTransform performs a left join given source_pipeline_name, source_data,
     join_pipeline_name, join_data, common_key constructors"""

    def __init__(self, source_pipeline_name, source_data, join_pipeline_name, join_data, common_key):
        self.join_pipeline_name = join_pipeline_name
        self.source_data = source_data
        self.source_pipeline_name = source_pipeline_name
        self.join_data = join_data
        self.common_key = common_key

    def expand(self, pcolls):
        def _format_as_common_key_tuple(data_dict, common_key):
            return data_dict[common_key], data_dict

        """This part here below starts with a python dictionary comprehension in case you 
        get lost in what is happening :-)"""
        return ({pipeline_name: pcoll | 'Convert to ({0}, object) for {1}'
                .format(self.common_key, pipeline_name)
                                >> beam.Map(_format_as_common_key_tuple, self.common_key)
                 for (pipeline_name, pcoll) in pcolls.items()}
                | 'CoGroupByKey {0}'.format(pcolls.keys()) >> beam.CoGroupByKey()
                | 'Unnest Cogrouped' >> beam.ParDo(UnnestCoGrouped(),
                                                   self.source_pipeline_name,
                                                   self.join_pipeline_name)
                )


class UnnestCoGrouped(beam.DoFn):
    """This DoFn class unnests the CogroupBykey output and emits """

    def process(self, input_element, source_pipeline_name, join_pipeline_name):
        group_key, grouped_dict = input_element
        join_dictionary = grouped_dict[join_pipeline_name]
        source_dictionaries = grouped_dict[source_pipeline_name]
        for source_dictionary in source_dictionaries:
            try:
                source_dictionary.update(join_dictionary[0])
                yield source_dictionary
            except IndexError:  # found no join_dictionary
                yield source_dictionary


class LogContents(beam.DoFn):
    """This DoFn class logs the content of that which it receives """

    def process(self, input_element):
        logging.info("Contents: {}".format(input_element))
        logging.info("Contents type: {}".format(type(input_element)))
        logging.info("Contents Access input_element['Country']: {}".format(input_element['Country']))
        return


def run(argv=None):
    """Main entry point"""
    pipeline_options = PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)

    # Create Example read Dictionary data
    source_pipeline_name = 'source_data'
    source_data = p | 'Create source data' >> beam.Create(
        [{'Country': 'The Netherlands', 'Year': '2011',
          'Cheese consumption per capita per year (kg)': '19.4'},
         {'Country': 'The Netherlands', 'Year': '2012',
          'Cheese consumption per capita per year (kg)': '20.1'},
         {'Country': 'France', 'Year': '2011',
          'Cheese consumption per'
          ' capita per year (kg)': '26.3'},
         {'Country': 'China', 'Year': '2011',
          'Cheese consumption per capita per year (kg)': '0.1'}
         ])
    join_pipeline_name = 'join_data'
    join_data = p | 'Create join data' >> beam.Create(
        [{'Country': 'The Netherl'
                     'ands',
          'Continent': 'Europe'},
         {'Country': 'China', 'Co'
                              'ntinent': 'Asia'},
         {'Country': 'USA', 'Conti'
                            'nent': 'North America'},
         {'Country': 'Brazil', 'Con'
                               'tinent': 'South America'}
         ])

    common_key = 'Country'
    pipelines_dictionary = {source_pipeline_name: source_data,
                            join_pipeline_name: join_data}
    test_pipeline = (pipelines_dictionary
                     | 'Left join' >> LeftJoin(
                source_pipeline_name, source_data,
                join_pipeline_name, join_data, common_key)
                     | 'Log Contents' >> beam.ParDo(LogContents())
                     )

    result = p.run()
    result.wait_until_finish()


if __name__ == '__main__':
    run()
# python -m leftjoin-blogexample --runner DataflowRunner --project YOUR_PROJECT_ID --temp_location gs://YOUR_BUCKET/tmp/
