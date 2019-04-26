import pandas as pd


class CodeCompleter(object):
    def __init__(self):
        self._imports_counts_df = None

    def load_db(self, imports_lines_df):
        imports_counts_series = imports_lines_df.line.value_counts()
        imports_counts_df = pd.DataFrame(imports_counts_series)
        imports_counts_df.rename(columns={'line': 'count'}, inplace=True)
        imports_counts_df['line'] = imports_counts_df.index.str.strip()
        imports_counts_df.reset_index(drop=True).head()
        self._imports_counts_df = imports_counts_df

    def complete_code(self, string_to_complete, number_of_options=3):
        relevant_df = self._imports_counts_df[self._imports_counts_df['line'].str.startswith(string_to_complete)]
        total_relevant = relevant_df['count'].sum()
        most_relevant_df = relevant_df.sort_values(by='count', ascending=False).iloc[:number_of_options]
        results_df = most_relevant_df[['count', 'line']].reset_index(drop=True)
        results_df['prob'] = results_df['count'] / total_relevant
        print('{:.2f}%'.format(results_df['prob'].sum() * 100))
        return results_df
