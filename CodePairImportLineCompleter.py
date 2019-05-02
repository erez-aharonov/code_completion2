import pandas as pd


class CodePairImportLineCompleter(object):
    def __init__(self):
        self._imports_lines_df = None

    def load_db(self, imports_lines_df):
        self._imports_lines_df = imports_lines_df

    def complete_code(self, line, number_of_options=3):
        line_related_df = self._imports_lines_df[self._imports_lines_df['line'] == line]
        unique_relevant_files_array = line_related_df['file_path'].unique()
        relevant_files_df = \
            self._imports_lines_df[self._imports_lines_df['file_path'].isin(unique_relevant_files_array)]
        imports_counts_df_2 = self._get_line_value_counts_df(relevant_files_df.line)
        lines_values_counts_df = imports_counts_df_2[imports_counts_df_2['line'] != line]
        sorted_lines_values_counts_df = lines_values_counts_df.sort_values(by='count', ascending=False)
        results_df = self._get_most_relevant_with_prob(sorted_lines_values_counts_df, number_of_options)
        return results_df

    @staticmethod
    def _get_most_relevant_with_prob(sorted_lines_values_counts_df, number_of_options):
        total_lines_count = sorted_lines_values_counts_df['count'].sum()
        most_relevant_df = \
            sorted_lines_values_counts_df.sort_values(by='count', ascending=False).iloc[:number_of_options]
        results_df = most_relevant_df[['count', 'line']].reset_index(drop=True)
        results_df['prob'] = results_df['count'] / total_lines_count
        print('{:.2f}%'.format(results_df['prob'].sum() * 100))
        return results_df

    @staticmethod
    def _get_line_value_counts_df(lines_series):
        lines_values_counts_series = lines_series.value_counts()
        lines_values_counts_df = pd.DataFrame(lines_values_counts_series)
        lines_values_counts_df.rename(columns={'line': 'count'}, inplace=True)
        lines_values_counts_df['line'] = lines_values_counts_df.index.str.strip()
        lines_values_counts_df.reset_index(drop=True).head()
        return lines_values_counts_df
